"""
Flask application factory
"""
import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_migrate import Migrate

from config import config

# Path to frontend files (parent directory of backend)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

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

    # Static file serving for frontend
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        # Try to serve the file directly
        file_path = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(file_path):
            return send_from_directory(FRONTEND_DIR, filename)
        # For SPA-style navigation, serve index.html for HTML pages
        if filename.endswith('.html'):
            return send_from_directory(FRONTEND_DIR, filename)
        # Fallback to index.html for client-side routing
        return send_from_directory(FRONTEND_DIR, 'index.html')

    return app
