from __future__ import annotations

from flask import Flask, jsonify

from .api.routes import bp as api_bp, register_realtime
from .config import Config
from .extensions import cors, db, jwt, limiter, migrate, socketio


def create_app(config_object: type[Config] = Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')
    register_realtime(socketio)
    socketio.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get('/')
    def index():
        return jsonify({'name': 'AI Enterprise Consulting Platform', 'status': 'running'})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({'error': 'not_found'}), 404

    return app

