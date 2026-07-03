from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Attach extensions to this app instance
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Tell Flask-Login which route to redirect unauthenticated users to
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Flask-Login needs to know how to load a user from an ID stored in the session
    from app.models.user import User
    from app.models.scan import Scan, ScanDevice
    from app.models.device import Device
    from app.models.notification import Notification

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Create database tables if they don't exist yet
    with app.app_context():
        db.create_all()

    return app