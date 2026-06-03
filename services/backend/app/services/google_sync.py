from __future__ import annotations

import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Any

from flask import current_app

logger = logging.getLogger(__name__)

GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
]


def _backend_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _resolve_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = _backend_root() / raw
    return path


def _load_token_credentials(token_path: Path):
    from google.oauth2.credentials import Credentials

    try:
        return Credentials.from_authorized_user_file(str(token_path), GOOGLE_SCOPES)
    except ValueError:
        data = json.loads(token_path.read_text(encoding='utf-8'))
        return Credentials(
            token=data.get('token'),
            refresh_token=data.get('refresh_token'),
            token_uri=data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            scopes=data.get('scopes', GOOGLE_SCOPES),
        )


def _build_credentials():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        logger.error('Installez: pip install google-api-python-client google-auth google-auth-oauthlib')
        return None

    token_file = current_app.config.get('GOOGLE_OAUTH_TOKEN_FILE', 'google-oauth-token.json').strip()
    token_path = _resolve_path(token_file)

    refresh_token = current_app.config.get('GOOGLE_OAUTH_REFRESH_TOKEN', '').strip()
    client_id = current_app.config.get('GOOGLE_OAUTH_CLIENT_ID', '').strip()
    client_secret = current_app.config.get('GOOGLE_OAUTH_CLIENT_SECRET', '').strip()

    credentials = None

    if token_path.exists():
        try:
            credentials = _load_token_credentials(token_path)
        except Exception:
            logger.exception('Impossible de charger le token Google OAuth')
            credentials = None

    if credentials and credentials.expired:
        if credentials.refresh_token:
            try:
                credentials.refresh(Request())
                token_path.write_text(credentials.to_json(), encoding='utf-8')
            except Exception:
                logger.exception('Google OAuth refresh failed')
                credentials = None
        else:
            logger.error(
                'Token Google expire sans refresh_token. '
                'Relancez: python scripts/google_oauth_setup.py'
            )
            credentials = None

    if credentials and credentials.valid:
        return credentials

    if refresh_token and client_id and client_secret:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=GOOGLE_SCOPES,
        )
        credentials.refresh(Request())
        token_path.write_text(credentials.to_json(), encoding='utf-8')
        return credentials

    return None


def sync_appointment_to_calendar(lead, appointment) -> dict[str, Any]:
    calendar_id = current_app.config.get('GOOGLE_CALENDAR_ID', '').strip() or 'primary'
    credentials = _build_credentials()
    if not credentials:
        return {'synced': False, 'reason': 'missing_google_oauth'}

    try:
        from googleapiclient.discovery import build
    except ImportError:
        return {'synced': False, 'reason': 'google_api_client_not_installed'}

    start = appointment.scheduled_at
    end = start + timedelta(minutes=appointment.duration_minutes)
    timezone = current_app.config.get('GOOGLE_CALENDAR_TIMEZONE', 'Africa/Casablanca')

    start_value = start.isoformat()
    end_value = end.isoformat()

    description_lines = [
        f'Client: {lead.full_name}',
        f'Email: {lead.email}',
        f'Téléphone: {lead.phone or "—"}',
        f'Entreprise: {lead.company_name}',
    ]
    if appointment.notes:
        description_lines.append(f'Notes: {appointment.notes}')

    event_body = {
        'summary': f'Consultation IA — {lead.full_name}',
        'description': '\n'.join(description_lines),
        'start': {'dateTime': start_value, 'timeZone': timezone},
        'end': {'dateTime': end_value, 'timeZone': timezone},
        'conferenceData': {
            'createRequest': {
                'requestId': f'appt-{appointment.id}-{int(start.timestamp())}',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            },
        },
    }

    try:
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_body,
            conferenceDataVersion=1,
        ).execute()

        meeting_url = event.get('hangoutLink')
        if not meeting_url:
            entry_points = event.get('conferenceData', {}).get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    meeting_url = entry.get('uri')
                    break

        return {
            'synced': True,
            'calendar_event_id': event.get('id'),
            'meeting_url': meeting_url,
            'html_link': event.get('htmlLink'),
        }
    except Exception as error:
        logger.exception('Google Calendar sync failed')
        return {'synced': False, 'reason': 'calendar_api_error', 'detail': str(error)}


def sync_appointment_to_sheet(lead, appointment) -> dict[str, Any]:
    spreadsheet_id = current_app.config.get('GOOGLE_SHEETS_ID', '').strip()
    if not spreadsheet_id or spreadsheet_id == '0':
        logger.warning(
            'Google Sheets ignoré: GOOGLE_SHEETS_ID manquant ou égal à 0. '
            'Copiez l\'ID depuis l\'URL du spreadsheet dans .env'
        )
        return {'synced': False, 'reason': 'missing_sheets_id'}

    credentials = _build_credentials()
    if not credentials:
        return {'synced': False, 'reason': 'missing_google_oauth'}

    try:
        from googleapiclient.discovery import build
    except ImportError:
        return {'synced': False, 'reason': 'google_api_client_not_installed'}

    sheet_range = current_app.config.get('GOOGLE_SHEETS_RANGE', 'Rendez-vous!A:H')
    row = [
        appointment.scheduled_at.strftime('%Y-%m-%d %H:%M'),
        lead.full_name,
        lead.email,
        lead.phone or '',
        lead.company_name,
        str(appointment.duration_minutes),
        appointment.notes or '',
        appointment.meeting_url or '',
    ]

    try:
        service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]},
        ).execute()

        return {'synced': True, 'spreadsheet_id': spreadsheet_id, 'range': sheet_range}
    except Exception as error:
        logger.exception('Google Sheets sync failed')
        return {'synced': False, 'reason': 'sheets_api_error', 'detail': str(error)}


def sync_appointment(lead, appointment) -> dict[str, Any]:
    calendar_result = sync_appointment_to_calendar(lead, appointment)
    sheets_result = sync_appointment_to_sheet(lead, appointment)
    return {'calendar': calendar_result, 'sheets': sheets_result}
