from __future__ import annotations

from datetime import datetime

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    role = db.Column(db.String(50), nullable=False, default='client')
    google_id = db.Column(db.String(255), unique=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)

    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'role': self.role,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class RefreshToken(db.Model, TimestampMixin):
    __tablename__ = 'refresh_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(50), nullable=False, default='refresh')
    revoked = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)


class Conversation(db.Model, TimestampMixin):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False, default='AI Consultation')
    status = db.Column(db.String(50), nullable=False, default='active')
    summary = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')


class Message(db.Model, TimestampMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(50), nullable=False, default='voice')
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)


class LeadProfile(db.Model, TimestampMixin):
    __tablename__ = 'lead_profiles'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50))
    company_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255))
    employee_count = db.Column(db.String(50))
    business_goals = db.Column(db.Text)
    challenges = db.Column(db.Text)
    budget = db.Column(db.String(100))
    decision_maker_status = db.Column(db.String(100))
    lead_score = db.Column(db.Integer, nullable=False, default=0)
    conversion_probability = db.Column(db.Float, nullable=False, default=0.0)
    priority_level = db.Column(db.String(50), nullable=False, default='medium')
    recommended_services = db.Column(db.JSON, nullable=False, default=list)
    estimated_project_value = db.Column(db.String(100))
    memory_summary = db.Column(db.Text)
    source = db.Column(db.String(50), nullable=False, default='voice')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'industry': self.industry,
            'lead_score': self.lead_score,
            'conversion_probability': self.conversion_probability,
            'priority_level': self.priority_level,
            'recommended_services': self.recommended_services,
            'estimated_project_value': self.estimated_project_value,
        }


class KnowledgeDocument(db.Model, TimestampMixin):
    __tablename__ = 'knowledge_documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    source_type = db.Column(db.String(50), nullable=False, default='upload')
    summary = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='queued')
    qdrant_point_id = db.Column(db.String(255))


class Appointment(db.Model, TimestampMixin):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead_profiles.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(50), nullable=False, default='scheduled')
    meeting_url = db.Column(db.String(500))
    calendar_event_id = db.Column(db.String(255))
    notes = db.Column(db.Text)
    lead = db.relationship('LeadProfile', backref=db.backref('appointments', lazy=True))


class Proposal(db.Model, TimestampMixin):
    __tablename__ = 'proposals'

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead_profiles.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    scope = db.Column(db.Text, nullable=False)
    timeline = db.Column(db.Text)
    budget = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False, default='draft')
    pdf_url = db.Column(db.String(500))
    docx_url = db.Column(db.String(500))
    lead = db.relationship('LeadProfile', backref=db.backref('proposals', lazy=True))


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    entity = db.Column(db.String(255), nullable=False)
    entity_id = db.Column(db.String(255), nullable=False)
    details = db.Column(db.JSON, nullable=False, default=dict)

