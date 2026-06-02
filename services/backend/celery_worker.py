from celery import Celery
from app.config import Config
from app.extensions import socketio


def make_celery():
    celery = Celery('worker', broker=Config.CELERY_BROKER_URL)
    celery.conf.update(result_backend=Config.CELERY_RESULT_BACKEND)
    return celery

celery = make_celery()

@celery.task
def ping():
    return 'pong'


@celery.task
def broadcast_lead_created(payload):
    socketio.emit('lead_created', payload, namespace='/')
    return payload

