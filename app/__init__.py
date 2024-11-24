import os

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

from app.api.v1.routes import \
    create_v1_routes  # Ensure this is the correct import
from app.api.v2.routes import api as v2_api
from app.db import db


def create_app():
    app = Flask(__name__)

    # Initialize Limiter
    limiter = Limiter(
        get_remote_address,  # Use IP address to track requests
        app=app,  # Bind the limiter to the Flask app
        default_limits=["200 per day", "50 per hour"],  # Default rate limits
        storage_uri="memory://",  # In-memory storage for rate limits (ideal for dev, not for prod)
    )

    # Register API blueprints
    app.register_blueprint(create_v1_routes(limiter), url_prefix='/api/v1')
    app.register_blueprint(v2_api, url_prefix='/api/v2')

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')  # Use DATABASE_URI from .env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.errorhandler(429)
    def rate_limit_error(error):
        return jsonify({
            "error": "Too Many Requests",
            "message": "You have exceeded the rate limit. Please try again later.",
            "status_code": 429
        }), 429

    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        print("Database initialized!")

    return app
