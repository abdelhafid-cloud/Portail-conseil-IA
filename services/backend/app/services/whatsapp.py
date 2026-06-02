from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import Any

from flask import current_app

logger = logging.getLogger(__name__)


def normalize_phone(number: str) -> str:
    return re.sub(r'\D', '', number)


def normalize_base_url(base_url: str) -> str:
    url = base_url.strip().rstrip('/')
    if not url:
        return ''
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    return url


def notify_appointment_booked(lead, appointment) -> dict[str, Any]:
    recipient = current_app.config.get('WHATSAPP_ADMIN_NUMBER', '').strip()
    if not recipient:
        return {'sent': False, 'reason': 'no_recipient'}

    to_digits = normalize_phone(recipient)
    if not to_digits:
        return {'sent': False, 'reason': 'invalid_recipient'}

    scheduled_date = appointment.scheduled_at.strftime('%d/%m/%Y')
    scheduled_time = appointment.scheduled_at.strftime('%H:%M')

    token = current_app.config.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', '')
    if token and phone_id:
        body = _build_appointment_text(lead, appointment, scheduled_date, scheduled_time)
        return _send_via_meta(to_digits, body, token, phone_id)

    infobip_base_url = normalize_base_url(current_app.config.get('INFOBIP_BASE_URL', ''))
    infobip_api_key = current_app.config.get('INFOBIP_API_KEY', '')
    infobip_sender = current_app.config.get('INFOBIP_WHATSAPP_SENDER', '')
    if infobip_base_url and infobip_api_key and infobip_sender:
        template_name = current_app.config.get('INFOBIP_WHATSAPP_TEMPLATE_NAME', 'appointment_reminder')
        template_language = current_app.config.get('INFOBIP_WHATSAPP_TEMPLATE_LANGUAGE', 'en')
        return _send_infobip_template(
            to_digits=to_digits,
            base_url=infobip_base_url,
            api_key=infobip_api_key,
            sender=infobip_sender,
            template_name=template_name,
            template_language=template_language,
            placeholders=[lead.full_name, scheduled_date, scheduled_time],
        )

    logger.warning('WhatsApp non configuré pour le rendez-vous #%s', appointment.id)
    return {'sent': False, 'reason': 'not_configured'}


def _build_appointment_text(lead, appointment, scheduled_date: str, scheduled_time: str) -> str:
    lines = [
        'Nouveau rendez-vous',
        f'Client: {lead.full_name}',
        f'Téléphone: {lead.phone or "—"}',
        f'Email: {lead.email}',
        f'Entreprise: {lead.company_name}',
        f'Date: {scheduled_date} {scheduled_time}',
        f'Durée: {appointment.duration_minutes} min',
    ]
    if appointment.notes:
        lines.append(f'Notes: {appointment.notes}')
    if appointment.meeting_url:
        lines.append(f'Visio: {appointment.meeting_url}')
    return '\n'.join(lines)


def _parse_infobip_response(data: dict[str, Any]) -> dict[str, Any]:
    status = data.get('status') if isinstance(data.get('status'), dict) else {}
    if not status and isinstance(data.get('messages'), list) and data['messages']:
        status = data['messages'][0].get('status') or {}

    group_name = str(status.get('groupName', '')).upper()
    status_name = str(status.get('name', ''))

    if group_name == 'REJECTED' or status_name.startswith('REJECTED'):
        logger.error('WhatsApp Infobip rejeté: %s', json.dumps(data))
        return {
            'sent': False,
            'provider': 'infobip',
            'reason': status_name or 'rejected',
            'detail': status.get('description') or 'Message rejeté par Infobip',
            'action': status.get('action'),
        }

    message_id = data.get('messageId')
    messages = data.get('messages')
    if isinstance(messages, list) and messages:
        message_id = messages[0].get('messageId') or message_id

    logger.info('WhatsApp Infobip accepté: messageId=%s status=%s', message_id, status_name or group_name)
    return {
        'sent': True,
        'provider': 'infobip',
        'message_id': message_id,
        'status': status_name or group_name or 'ACCEPTED',
    }


def _send_infobip_template(
    to_digits: str,
    base_url: str,
    api_key: str,
    sender: str,
    template_name: str,
    template_language: str,
    placeholders: list[str],
) -> dict[str, Any]:
    url = f'{base_url}/whatsapp/1/message/template'
    payload = json.dumps({
        'messages': [{
            'from': normalize_phone(sender),
            'to': to_digits,
            'content': {
                'templateName': template_name,
                'templateData': {
                    'body': {'placeholders': placeholders},
                },
                'language': template_language,
            },
        }],
    }).encode('utf-8')

    request = urllib.request.Request(url, data=payload, method='POST')
    request.add_header('Authorization', f'App {api_key}')
    request.add_header('Content-Type', 'application/json')
    request.add_header('Accept', 'application/json')

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            result = _parse_infobip_response(data)
            if result.get('sent'):
                result['template'] = template_name
            return result
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', errors='replace')
        logger.error('WhatsApp Infobip template error: %s', detail)
        return {'sent': False, 'reason': 'infobip_api_error', 'detail': detail}
    except OSError as error:
        logger.error('WhatsApp Infobip network error: %s', error)
        return {'sent': False, 'reason': 'network_error', 'detail': str(error)}


def _send_via_meta(to_digits: str, body: str, token: str, phone_id: str) -> dict[str, Any]:
    url = f'https://graph.facebook.com/v19.0/{phone_id}/messages'
    payload = json.dumps({
        'messaging_product': 'whatsapp',
        'to': to_digits,
        'type': 'text',
        'text': {'body': body},
    }).encode('utf-8')

    request = urllib.request.Request(url, data=payload, method='POST')
    request.add_header('Authorization', f'Bearer {token}')
    request.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return {'sent': True, 'provider': 'meta', 'message_id': data.get('messages', [{}])[0].get('id')}
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', errors='replace')
        logger.error('WhatsApp Meta API error: %s', detail)
        return {'sent': False, 'reason': 'meta_api_error', 'detail': detail}
    except OSError as error:
        logger.error('WhatsApp Meta network error: %s', error)
        return {'sent': False, 'reason': 'network_error', 'detail': str(error)}
