from datetime import datetime, timedelta
from collections import Counter
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.scan import Scan, ScanDevice
from app.models.device import Device


api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/dashboard-stats')
@login_required
def dashboard_stats():
    """Returns the 4 KPI numbers shown in the stat cards."""

    total_devices = Device.query.filter_by(user_id=current_user.id).count()
    online_devices = Device.query.filter_by(user_id=current_user.id, is_online=True).count()
    total_scans = Scan.query.filter_by(user_id=current_user.id).count()
    failed_scans = Scan.query.filter_by(user_id=current_user.id, status='failed').count()

    # Sum of open ports across all this user's devices' most recent scan links
    all_links = (
        db.session.query(ScanDevice)
        .join(Scan)
        .filter(Scan.user_id == current_user.id)
        .all()
    )
    total_open_ports = 0
    for link in all_links:
        if link.open_ports:
            total_open_ports += len([p for p in link.open_ports.split(',') if p])

    return jsonify({
        'total_devices': total_devices,
        'online_devices': online_devices,
        'total_open_ports': total_open_ports,
        'total_scans': total_scans,
        'failed_scans': failed_scans
    })


@api_bp.route('/devices-over-time')
@login_required
def devices_over_time():
    """Returns device discovery counts for the last 7 days, one point per day."""

    today = datetime.utcnow().date()
    labels = []
    counts = []

    for i in range(6, -1, -1):  # 6 days ago -> today
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        count = Device.query.filter(
            Device.user_id == current_user.id,
            Device.first_seen >= day_start,
            Device.first_seen <= day_end
        ).count()

        labels.append(day.strftime('%a'))  # e.g. 'Mon'
        counts.append(count)

    return jsonify({'labels': labels, 'counts': counts})


@api_bp.route('/common-services')
@login_required
def common_services():
    """Returns the top 5 most frequently seen services across all scans."""

    links = (
        db.session.query(ScanDevice)
        .join(Scan)
        .filter(Scan.user_id == current_user.id)
        .all()
    )

    service_counter = Counter()
    for link in links:
        if link.services:
            for service in link.services.split(','):
                service = service.strip()
                if service:
                    service_counter[service] += 1

    top_services = service_counter.most_common(5)

    labels = [item[0] for item in top_services]
    counts = [item[1] for item in top_services]

    return jsonify({'labels': labels, 'counts': counts})

@api_bp.route('/online-status')
@login_required
def online_status():
    """Returns counts of online vs offline devices for the current user."""

    online_count = Device.query.filter_by(user_id=current_user.id, is_online=True).count()
    offline_count = Device.query.filter_by(user_id=current_user.id, is_online=False).count()

    return jsonify({
        'labels': ['Online', 'Offline'],
        'counts': [online_count, offline_count]
    })

@api_bp.route('/search')
@login_required
def search():
    """Live search-as-you-type — returns top matching devices as JSON."""
    query_text = request.args.get('q', '').strip()

    if not query_text or len(query_text) < 2:
        return jsonify({'results': []})

    matches = Device.query.filter(
        Device.user_id == current_user.id,
        db.or_(
            Device.ip_address.ilike(f'%{query_text}%'),
            Device.hostname.ilike(f'%{query_text}%'),
            Device.vendor.ilike(f'%{query_text}%'),
            Device.mac_address.ilike(f'%{query_text}%')
        )
    ).limit(8).all()

    return jsonify({
        'results': [
            {
                'id': d.id,
                'ip_address': d.ip_address,
                'hostname': d.hostname or 'Unknown',
                'vendor': d.vendor or 'Unknown'
            }
            for d in matches
        ]
    })
