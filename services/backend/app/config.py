from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / '.env')

_INSTANCE_DIR = _BACKEND_ROOT / 'instance'
_INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
_DEFAULT_SQLITE = f"sqlite:///{(_INSTANCE_DIR / 'app.db').as_posix()}"


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', _DEFAULT_SQLITE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    QDRANT_URL = os.environ.get('QDRANT_URL', 'http://localhost:6333')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GOOGLE_CALENDAR_ID = os.environ.get('GOOGLE_CALENDAR_ID', '')
    GOOGLE_CALENDAR_TIMEZONE = os.environ.get('GOOGLE_CALENDAR_TIMEZONE', 'Africa/Casablanca')
    GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '')
    GOOGLE_SHEETS_RANGE = os.environ.get('GOOGLE_SHEETS_RANGE', 'Rendez-vous!A:H')
    GOOGLE_OAUTH_CLIENT_FILE = os.environ.get('GOOGLE_OAUTH_CLIENT_FILE', 'google-oauth-client.json')
    GOOGLE_OAUTH_TOKEN_FILE = os.environ.get('GOOGLE_OAUTH_TOKEN_FILE', 'google-oauth-token.json')
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '')
    GOOGLE_OAUTH_REFRESH_TOKEN = os.environ.get('GOOGLE_OAUTH_REFRESH_TOKEN', '')
    WHATSAPP_ADMIN_NUMBER = os.environ.get('WHATSAPP_ADMIN_NUMBER', '')
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    INFOBIP_BASE_URL = os.environ.get('INFOBIP_BASE_URL', '')
    INFOBIP_API_KEY = os.environ.get('INFOBIP_API_KEY', '')
    INFOBIP_WHATSAPP_SENDER = os.environ.get('INFOBIP_WHATSAPP_SENDER', '')
    INFOBIP_WHATSAPP_TEMPLATE_NAME = os.environ.get('INFOBIP_WHATSAPP_TEMPLATE_NAME', 'appointment_reminder')
    INFOBIP_WHATSAPP_TEMPLATE_LANGUAGE = os.environ.get('INFOBIP_WHATSAPP_TEMPLATE_LANGUAGE', 'en')

