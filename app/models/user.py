from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """Represents a registered dashboard user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Settings we'll actually use starting Section 13
    theme_preference = db.Column(db.String(10), default='light')
    email_notifications = db.Column(db.Boolean, default=True)

    def set_password(self, raw_password):
        """Hashes and stores the given plaintext password."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Returns True if the given plaintext password matches the stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f'<User {self.username}>'