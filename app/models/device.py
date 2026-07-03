from datetime import datetime
from app.extensions import db


class Device(db.Model):
    """A unique device ever discovered on any scanned network.
    One row per unique MAC address (or IP, if MAC is unavailable)."""

    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)

    ip_address = db.Column(db.String(45), nullable=False)   # 45 chars fits IPv6 too
    mac_address = db.Column(db.String(17), unique=True, nullable=True)  # e.g. AA:BB:CC:DD:EE:FF
    hostname = db.Column(db.String(255), nullable=True)
    vendor = db.Column(db.String(255), nullable=True)
    operating_system = db.Column(db.String(255), nullable=True)

    is_online = db.Column(db.Boolean, default=True)

    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Which user's network this device belongs to (devices aren't shared across users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship to the link table (defined in scan.py) — lets us do device.scans
    scans = db.relationship('ScanDevice', back_populates='device', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Device {self.ip_address} ({self.mac_address})>'