from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.device import Device
from app.models.scan import ScanDevice
from datetime import datetime

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')


@devices_bp.route('/')
@login_required
def devices_list():
    """Shows every unique device ever discovered for this user."""
    devices = Device.query.filter_by(user_id=current_user.id).order_by(Device.last_seen.desc()).all()
    return render_template('devices_list.html', devices=devices)


@devices_bp.route('/<int:device_id>')
@login_required
def device_detail(device_id):
    """Shows full profile + scan history for one specific device."""

    # Scope by user_id too — prevents viewing another user's device by guessing IDs
    device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()

    if not device:
        abort(404)

    # Every time this device was seen, across all scans, newest first
    scan_history = (
        ScanDevice.query
        .filter_by(device_id=device.id)
        .join(ScanDevice.scan)
        .order_by(ScanDevice.detected_at.desc())
        .all()
    )
    days_known = (datetime.utcnow() - device.first_seen).days

    return render_template(
        'device_detail.html',
        device=device,
        scan_history=scan_history,
        days_known=days_known
    )