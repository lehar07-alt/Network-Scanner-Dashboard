from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    """An alert shown to a user, e.g. 'New device discovered: 192.168.1.55'."""

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    notif_type = db.Column(db.String(30), default='info')   # info / warning / danger
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Notification {self.message[:30]}>'