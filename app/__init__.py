from flask import Flask

from app.api.v1.routes import api as v1_api

# from app.api.v2.routes import api as v2_api


def create_app():
    app = Flask(__name__)

    # Register API blueprints
    app.register_blueprint(v1_api, url_prefix='/api/v1')
    # app.register_blueprint(v2_api, url_prefix='/api/v2')

    return app