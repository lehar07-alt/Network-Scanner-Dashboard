from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# These are created here, unattached to any app, then "attached"
# inside create_app() via .init_app(app). This avoids circular imports
# between models, routes, and the app factory.
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()