from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.device import Device
from app.models.scan import ScanDevice
from datetime import datetime
from flask import request
from app.extensions import db
from flask import Response
from app.services.export_service import export_devices_csv, export_devices_json, export_devices_pdf

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')

@devices_bp.route('/')
@login_required
def devices_list():
    """Shows every unique device ever discovered for this user, with filters."""

    status_filter = request.args.get('status', '')
    os_filter = request.args.get('os', '')
    vendor_filter = request.args.get('vendor', '')
    subnet_filter = request.args.get('subnet', '')

    query = Device.query.filter_by(user_id=current_user.id)

    if status_filter == 'online':
        query = query.filter_by(is_online=True)
    elif status_filter == 'offline':
        query = query.filter_by(is_online=False)

    if os_filter:
        query = query.filter_by(operating_system=os_filter)

    if vendor_filter:
        query = query.filter_by(vendor=vendor_filter)

    if subnet_filter:
        # subnet_filter looks like "192.168.31" — match any IP starting with it
        query = query.filter(Device.ip_address.like(f'{subnet_filter}.%'))

    devices = query.order_by(Device.last_seen.desc()).all()

    # --- Build filter dropdown options from this user's actual data ---
    all_user_devices = Device.query.filter_by(user_id=current_user.id).all()

    available_os = sorted(set(d.operating_system for d in all_user_devices if d.operating_system))
    available_vendors = sorted(set(d.vendor for d in all_user_devices if d.vendor))
    available_subnets = sorted(set(
        '.'.join(d.ip_address.split('.')[:3]) for d in all_user_devices if d.ip_address
    ))

    return render_template(
        'devices_list.html',
        devices=devices,
        status_filter=status_filter,
        os_filter=os_filter,
        vendor_filter=vendor_filter,
        subnet_filter=subnet_filter,
        available_os=available_os,
        available_vendors=available_vendors,
        available_subnets=available_subnets
    )

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



@devices_bp.route('/search')
@login_required
def search_results():
    """Full search results page, triggered by pressing Enter in the search box."""
    query_text = request.args.get('q', '').strip()

    devices = []
    if query_text:
        devices = Device.query.filter(
            Device.user_id == current_user.id,
            db.or_(
                Device.ip_address.ilike(f'%{query_text}%'),
                Device.hostname.ilike(f'%{query_text}%'),
                Device.vendor.ilike(f'%{query_text}%'),
                Device.mac_address.ilike(f'%{query_text}%')
            )
        ).all()

    return render_template('search_results.html', devices=devices, query_text=query_text)

@devices_bp.route('/export/<file_format>')
@login_required
def export_devices(file_format):
    """Exports all of the current user's devices in the requested format."""

    devices = Device.query.filter_by(user_id=current_user.id).order_by(Device.ip_address).all()
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    if file_format == 'csv':
        content = export_devices_csv(devices)
        return Response(
            content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=devices_export_{timestamp}.csv'}
        )

    elif file_format == 'json':
        content = export_devices_json(devices)
        return Response(
            content,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=devices_export_{timestamp}.json'}
        )

    elif file_format == 'pdf':
        content = export_devices_pdf(devices, current_user.username)
        return Response(
            content,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=devices_export_{timestamp}.pdf'}
        )

    else:
        abort(404)