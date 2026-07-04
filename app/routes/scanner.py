from datetime import datetime
import time
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.scan import Scan, ScanDevice
from app.models.device import Device
from app.services.scanner import run_network_scan

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
    devices_found_count = 0
    for device_data in result['devices']:
        # Does this device (by MAC) already exist for this user?
        existing_device = None
        if device_data['mac_address']:
            existing_device = Device.query.filter_by(
                mac_address=device_data['mac_address'],
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