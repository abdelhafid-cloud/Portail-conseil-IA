from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, limiter
from ..models import Appointment, AuditLog, Conversation, KnowledgeDocument, LeadProfile, Message, RefreshToken, User
from ..realtime import register_socket_events
from ..services.ai import build_consultation_reply, generate_lead_insights, generate_meeting_brief, generate_proposal
from ..services.memory import summarize_conversation
from ..services.google_sync import sync_appointment
from ..services.scheduling import build_appointment_payload
from ..services.whatsapp import notify_appointment_booked

bp = Blueprint('api', __name__)


def _issue_tokens(user: User) -> dict:
    access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'email': user.email})
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims={'role': user.role, 'email': user.email})
    decoded_refresh = decode_token(refresh_token)

    db.session.add(
        RefreshToken(
            jti=decoded_refresh['jti'],
            user_id=user.id,
            expires_at=datetime.fromtimestamp(decoded_refresh['exp'], tz=timezone.utc),
        )
    )
    db.session.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token}

OPENAPI_SPEC = {
    'openapi': '3.1.0',
    'info': {
        'title': 'AI Enterprise Consulting Platform API',
        'version': '1.0.0',
        'description': 'Enterprise AI consulting backend with authentication, lead qualification, knowledge base, and scheduling.',
    },
    'paths': {
        '/api/health': {'get': {'summary': 'Health check'}},
        '/api/auth/register': {'post': {'summary': 'Create an account'}},
        '/api/auth/login': {'post': {'summary': 'Authenticate user'}},
        '/api/consultant/respond': {'post': {'summary': 'Generate consulting response'}},
        '/api/leads': {'get': {'summary': 'List leads'}, 'post': {'summary': 'Create or update a lead'}},
        '/api/appointments': {'get': {'summary': 'List appointments'}, 'post': {'summary': 'Schedule an appointment'}},
        '/api/knowledge': {'get': {'summary': 'List knowledge documents'}, 'post': {'summary': 'Register uploaded knowledge document'}},
        '/api/proposals': {'post': {'summary': 'Generate proposal draft'}},
        '/api/openapi.json': {'get': {'summary': 'OpenAPI specification'}},
    },
}


@bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'ai-enterprise-backend'})


@bp.route('/openapi.json')
def openapi_json():
    return jsonify(OPENAPI_SPEC)


@bp.route('/docs')
def docs():
    return jsonify({
        'message': 'OpenAPI spec available at /api/openapi.json',
        'swagger_ui_hint': 'Serve this spec in Swagger UI or Redoc in production.',
    })


def _serialize_appointment(appointment: Appointment) -> dict:
    return {
        'id': appointment.id,
        'lead_id': appointment.lead_id,
        'scheduled_at': appointment.scheduled_at.isoformat(),
        'duration_minutes': appointment.duration_minutes,
        'status': appointment.status,
        'meeting_url': appointment.meeting_url,
        'calendar_event_id': appointment.calendar_event_id,
    }


@bp.route('/auth/register', methods=['POST'])
@limiter.limit('10/minute')
def register():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', '')).strip()
    full_name = str(data.get('full_name', '')).strip()

    if not email or not password or not full_name:
        return jsonify({'error': 'email, password and full_name are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already registered'}), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        company_name=data.get('company_name'),
        role=data.get('role', 'client'),
        email_verified=bool(data.get('email_verified', False)),
    )
    db.session.add(user)
    db.session.commit()

    tokens = _issue_tokens(user)
    return jsonify({'user': user.to_dict(), **tokens}), 201


@bp.route('/auth/login', methods=['POST'])
@limiter.limit('20/minute')
def login():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', '')).strip()
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'invalid credentials'}), 401

    tokens = _issue_tokens(user)
    return jsonify({'user': user.to_dict(), **tokens})


@bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = int(get_jwt_identity())
    refresh_jti = get_jwt()['jti']
    stored_refresh = RefreshToken.query.filter_by(jti=refresh_jti, revoked=False, user_id=current_user_id).first()

    if not stored_refresh:
        return jsonify({'error': 'invalid refresh token'}), 401

    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404

    return jsonify({'access_token': create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'email': user.email})})


@bp.route('/auth/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    refresh_jti = get_jwt()['jti']
    stored_refresh = RefreshToken.query.filter_by(jti=refresh_jti, revoked=False).first()
    if stored_refresh:
        stored_refresh.revoked = True
        db.session.commit()
    return jsonify({'status': 'logged_out'})


@bp.route('/auth/me')
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'user': user.to_dict()})


@bp.route('/auth/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'user not found'}), 404

    user.email_verified = True
    db.session.commit()
    return jsonify({'status': 'verified', 'user': user.to_dict()})


@bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    return jsonify({'status': 'queued', 'email': data.get('email')})


@bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    return jsonify({'status': 'reset_complete'})


@bp.route('/consultant/respond', methods=['POST'])
@jwt_required(optional=True)
def consultant_respond():
    data = request.get_json() or {}
    message = str(data.get('message', '')).strip()
    context = data.get('context') or {}
    reply = build_consultation_reply(message, context)

    conversation = None
    user_id = get_jwt_identity()
    if user_id:
        conversation = Conversation.query.filter_by(user_id=int(user_id)).order_by(Conversation.created_at.desc()).first()
        if conversation:
            db.session.add(Message(conversation_id=conversation.id, sender='user', content=message))
            db.session.add(Message(conversation_id=conversation.id, sender='assistant', content=reply['reply']))
            conversation.summary = summarize_conversation([
                {'content': message},
                {'content': reply['reply']},
            ])
            db.session.commit()

    return jsonify({'reply': reply['reply'], 'suggested_services': reply['suggested_services'], 'follow_up_questions': reply['follow_up_questions']})


@bp.route('/leads', methods=['GET', 'POST'])
@jwt_required(optional=True)
def leads():
    if request.method == 'GET':
        leads = LeadProfile.query.order_by(LeadProfile.created_at.desc()).all()
        return jsonify({'items': [lead.to_dict() for lead in leads]})

    data = request.get_json() or {}
    insights = generate_lead_insights(data)
    lead = LeadProfile(
        full_name=str(data.get('full_name', '')), email=str(data.get('email', '')).lower(), phone=data.get('phone'),
        company_name=str(data.get('company_name', '')), industry=data.get('industry'), employee_count=data.get('employee_count'),
        business_goals=data.get('business_goals'), challenges=data.get('challenges'), budget=data.get('budget'),
        decision_maker_status=data.get('decision_maker_status'), lead_score=insights['lead_score'],
        conversion_probability=insights['conversion_probability'], priority_level=insights['priority_level'],
        recommended_services=insights['recommended_services'], estimated_project_value=insights['estimated_project_value'],
        memory_summary=data.get('memory_summary'), source=data.get('source', 'voice'),
    )
    db.session.add(lead)
    db.session.add(AuditLog(actor='system', action='lead_created', entity='lead', entity_id='new', details=insights))
    db.session.commit()
    return jsonify({'lead': lead.to_dict(), 'insights': insights}), 201


@bp.route('/appointments', methods=['GET', 'POST'])
@jwt_required(optional=True)
def appointments():
    if request.method == 'GET':
        items = Appointment.query.order_by(Appointment.scheduled_at.desc()).all()
        return jsonify({'items': [_serialize_appointment(item) for item in items]})

    data = request.get_json() or {}
    lead_id = int(data.get('lead_id', 0))
    lead = db.session.get(LeadProfile, lead_id)
    if not lead:
        return jsonify({'error': 'lead not found'}), 404

    payload = build_appointment_payload(data.get('scheduled_at'))
    appointment = Appointment(
        lead_id=lead_id,
        scheduled_at=datetime.fromisoformat(payload['scheduled_at']),
        duration_minutes=int(data.get('duration_minutes', 30)),
        status='scheduled',
        meeting_url=payload['meeting_url'],
        calendar_event_id=payload['calendar_event_id'],
        notes=data.get('notes'),
    )
    db.session.add(appointment)
    db.session.commit()

    google = sync_appointment(lead, appointment)
    if google.get('calendar', {}).get('synced'):
        appointment.calendar_event_id = google['calendar'].get('calendar_event_id') or appointment.calendar_event_id
        if google['calendar'].get('meeting_url'):
            appointment.meeting_url = google['calendar']['meeting_url']
        db.session.commit()

    whatsapp = notify_appointment_booked(lead, appointment)
    return jsonify({
        'appointment': _serialize_appointment(appointment),
        'whatsapp': whatsapp,
        'google': google,
    }), 201


@bp.route('/knowledge', methods=['GET', 'POST'])
@jwt_required(optional=True)
def knowledge():
    if request.method == 'GET':
        documents = KnowledgeDocument.query.order_by(KnowledgeDocument.created_at.desc()).all()
        return jsonify({'items': [
            {
                'id': document.id,
                'filename': document.filename,
                'mime_type': document.mime_type,
                'status': document.status,
                'summary': document.summary,
            } for document in documents
        ]})

    data = request.get_json() or {}
    document = KnowledgeDocument(
        filename=str(data.get('filename', 'untitled')),
        mime_type=str(data.get('mime_type', 'application/octet-stream')),
        source_type=str(data.get('source_type', 'upload')),
        summary=data.get('summary'),
        status='queued',
        qdrant_point_id=data.get('qdrant_point_id'),
    )
    db.session.add(document)
    db.session.commit()
    return jsonify({'document_id': document.id}), 201


@bp.route('/proposals', methods=['POST'])
@jwt_required(optional=True)
def proposals():
    data = request.get_json() or {}
    proposal = generate_proposal(data)
    return jsonify({'proposal': proposal, 'meeting_brief': generate_meeting_brief(data)})


@bp.route('/voice-session', methods=['POST'])
@jwt_required(optional=True)
def voice_session():
    data = request.get_json() or {}
    return jsonify({
        'session_id': f"voice_{int(datetime.now(timezone.utc).timestamp())}",
        'instructions': 'Use speech-to-text, GPT Realtime, knowledge retrieval, and text-to-speech in a single conversation loop.',
        'assistant_brief': build_consultation_reply(str(data.get('message', '')), data.get('context') or {}),
    })


def register_realtime(socketio):
    register_socket_events(socketio)

