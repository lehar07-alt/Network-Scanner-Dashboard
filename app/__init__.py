from flask import Flask
from config import Config


def create_app():
    """Application factory: builds and configures the Flask app."""

    # __name__ tells Flask where to look for templates/static relative to this file
    app = Flask(__name__)

    # Load settings from our Config class
    app.config.from_object(Config)

    # Register blueprints (route groups) — we only have one so far
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app