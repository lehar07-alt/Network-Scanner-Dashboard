from datetime import datetime
from app.extensions import db


class Scan(db.Model):
    """A single scan event — e.g. 'scanned 192.168.1.0/24 at 3:42pm'."""

    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    target_range = db.Column(db.String(50), nullable=False)   # e.g. '192.168.1.0/24'
    status = db.Column(db.String(20), default='pending')       # pending / running / completed / failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    devices_found = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # A scan sees many devices, via the link table
    devices = db.relationship('ScanDevice', back_populates='scan', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Scan {self.target_range} - {self.status}>'


class ScanDevice(db.Model):
    """Link table: records that a specific device was seen during a specific scan,
    plus scan-specific details (open ports found THAT time)."""

    __tablename__ = 'scan_devices'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)

    open_ports = db.Column(db.Text, nullable=True)     # stored as comma-separated for simplicity, e.g. "80,443,22"
    services = db.Column(db.Text, nullable=True)        # e.g. "http,https,ssh"
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    scan = db.relationship('Scan', back_populates='devices')
    device = db.relationship('Device', back_populates='scans')

    def __repr__(self):
        return f'<ScanDevice scan={self.scan_id} device={self.device_id}>'