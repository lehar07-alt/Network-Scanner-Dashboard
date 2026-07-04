from datetime import datetime
import time
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.scan import Scan, ScanDevice
from app.models.device import Device
from app.services.scanner import run_network_scan
from app.services.email_service import send_new_device_alert

scanner_bp = Blueprint('scanner', __name__, url_prefix='/scan')


@scanner_bp.route('/')
@login_required
def scan_page():
    """Renders the page with the 'enter a range and scan' form."""
    return render_template('scan.html')


@scanner_bp.route('/run', methods=['POST'])
@login_required
def run_scan():
    """
    Handles the actual scan request (called via JS fetch, returns JSON).
    Saves results into Scan, Device, and ScanDevice tables.
    """
    target_range = request.form.get('target_range', '').strip()

    if not target_range:
        return jsonify({'success': False, 'error': 'Please provide a target range.'}), 400

    # --- Create the Scan record first, marked as 'running' ---
    scan_record = Scan(
        target_range=target_range,
        status='running',
        user_id=current_user.id
    )
    db.session.add(scan_record)
    db.session.commit()

    # --- Run the actual Nmap scan ---
    # --- Run the actual Nmap scan, timed ---
    scan_start_time = time.time()
    result = run_network_scan(target_range)
    scan_end_time = time.time()
    scan_duration_seconds = round(scan_end_time - scan_start_time, 2)

    if not result['success']:
        scan_record.status = 'failed'
        scan_record.error_message = result['error']
        scan_record.completed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'success': False,
            'error': result['error'],
            'scan_duration_seconds': scan_duration_seconds
        }), 500
    # --- Save each discovered device ---
    # --- Save each discovered device ---
    devices_found_count = 0
    for device_data in result['devices']:
        existing_device = None

        # 1st choice: match by MAC address — most reliable, survives IP changes
        if device_data['mac_address']:
            existing_device = Device.query.filter_by(
                mac_address=device_data['mac_address'],
                user_id=current_user.id
            ).first()

        # Fallback: no MAC available (common without admin privileges) —
        # match by IP address instead, so we don't create endless duplicates
        if not existing_device:
            existing_device = Device.query.filter_by(
                ip_address=device_data['ip_address'],
                user_id=current_user.id
            ).first()

        if existing_device:
            # Update existing device's info (IP might have changed via DHCP)
            existing_device.ip_address = device_data['ip_address']
            existing_device.hostname = device_data['hostname']
            existing_device.vendor = device_data['vendor']
            existing_device.operating_system = device_data['operating_system']
            existing_device.is_online = (device_data['status'] == 'up')
            existing_device.last_seen = datetime.utcnow()
            device_row = existing_device
        else:
            # New device — create it
            device_row = Device(
                ip_address=device_data['ip_address'],
                mac_address=device_data['mac_address'],
                hostname=device_data['hostname'],
                vendor=device_data['vendor'],
                operating_system=device_data['operating_system'],
                is_online=(device_data['status'] == 'up'),
                user_id=current_user.id
            )
            db.session.add(device_row)
            db.session.flush()  # assigns device_row.id without a full commit yet

            # Notify the user by email, only if they have notifications enabled
            if current_user.email_notifications:
                send_new_device_alert(current_user.email, device_row)

        # Link this device to this scan, with THIS scan's port findings
        link = ScanDevice(
            scan_id=scan_record.id,
            device_id=device_row.id,
            open_ports=device_data['open_ports'],
            services=device_data['services']
        )
        db.session.add(link)
        devices_found_count += 1

    # --- Finalize the scan record ---
    scan_record.status = 'completed'
    scan_record.devices_found = devices_found_count
    scan_record.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'scan_id': scan_record.id,
        'devices_found': devices_found_count,
        'devices': result['devices'],
        'scan_duration_seconds': scan_duration_seconds
    })

@scanner_bp.route('/history')
@login_required
def history():
    """Displays all past scans for the logged-in user, with optional
    search/filter/sort via query string parameters."""

    # Read query string params, e.g. /scan/history?status=completed&sort=oldest
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '').strip()
    sort_order = request.args.get('sort', 'newest')

    # Start with scans belonging ONLY to the current user — critical for security
    query = Scan.query.filter_by(user_id=current_user.id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    if search_query:
        # .ilike() = case-insensitive LIKE, %term% means "contains term anywhere"
        query = query.filter(Scan.target_range.ilike(f'%{search_query}%'))

    if sort_order == 'oldest':
        query = query.order_by(Scan.started_at.asc())
    else:
        query = query.order_by(Scan.started_at.desc())

    scans = query.all()
    total_scans = len(scans)
    total_devices_found = sum(scan.devices_found for scan in scans)

    return render_template(
        'scan_history.html',
        scans=scans,
        status_filter=status_filter,
        search_query=search_query,
        sort_order=sort_order,
        total_scans=total_scans,
        total_devices_found=total_devices_found
    )


@scanner_bp.route('/history/<int:scan_id>/delete', methods=['POST'])
@login_required
def delete_scan(scan_id):
    """Deletes a single scan record (and its ScanDevice links, via cascade)."""

    scan_record = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first()

    if not scan_record:
        flash('Scan not found.', 'danger')
        return redirect(url_for('scanner.history'))

    db.session.delete(scan_record)
    db.session.commit()
    flash('Scan deleted successfully.', 'success')
    return redirect(url_for('scanner.history'))