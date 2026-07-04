from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.device import Device

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard page — now protected, requires login."""
    recent_devices = (
        Device.query
        .filter_by(user_id=current_user.id)
        .order_by(Device.last_seen.desc())
        .limit(5)
        .all()
    )
    return render_template('dashboard.html', recent_devices=recent_devices)