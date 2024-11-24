import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.api.v1.routes import api as v1_api
from app.api.v2.routes import api as v2_api
from app.db import db
from app.models import parking_logs


def create_app():
    app = Flask(__name__)
    

    # Register API blueprints
    app.register_blueprint(v1_api, url_prefix='/api/v1')
    app.register_blueprint(v2_api, url_prefix='/api/v2')

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')  # Use DATABASE_URI from .env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        print("Database initialized!")


    return app