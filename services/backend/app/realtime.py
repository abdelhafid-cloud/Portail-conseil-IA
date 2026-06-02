from __future__ import annotations

from flask_socketio import emit

from .services.ai import build_consultation_reply


def register_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        emit('consultant_status', {'status': 'connected'})

    @socketio.on('consultant_message')
    def handle_consultant_message(payload):
        message = str(payload.get('message', ''))
        context = payload.get('context') or {}
        emit('consultant_reply', build_consultation_reply(message, context))
