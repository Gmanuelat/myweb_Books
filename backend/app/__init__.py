"""
Flask application factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_migrate import Migrate

from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS
    CORS(app,
         origins=[app.config['FRONTEND_URL']],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])

    # Configure login manager
    login_manager.session_protection = 'strong'

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify
        return jsonify({'error': 'Authentication required'}), 401

    # Register blueprints
    from app.api import auth, books, library
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(books.bp, url_prefix='/api/books')
    app.register_blueprint(library.bp, url_prefix='/api/me')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok'}

    return app
