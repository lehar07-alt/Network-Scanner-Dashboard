import csv
import io
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def export_devices_csv(devices):
    """Builds CSV file content (as a string) from a list of Device objects."""

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(['IP Address', 'Hostname', 'MAC Address', 'Vendor', 'Operating System', 'Status', 'First Seen', 'Last Seen'])

    for device in devices:
        writer.writerow([
            device.ip_address,
            device.hostname or '',
            device.mac_address or '',
            device.vendor or '',
            device.operating_system or '',
            'Online' if device.is_online else 'Offline',
            device.first_seen.strftime('%Y-%m-%d %H:%M:%S'),
            device.last_seen.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return output.getvalue()


def export_devices_json(devices):
    """Builds JSON file content (as a string) from a list of Device objects."""

    data = [
        {
            'ip_address': device.ip_address,
            'hostname': device.hostname,
            'mac_address': device.mac_address,
            'vendor': device.vendor,
            'operating_system': device.operating_system,
            'status': 'online' if device.is_online else 'offline',
            'first_seen': device.first_seen.isoformat(),
            'last_seen': device.last_seen.isoformat(),
        }
        for device in devices
    ]

    return json.dumps(data, indent=2)


def export_devices_pdf(devices, username):
    """Builds a PDF report (as raw bytes) from a list of Device objects."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # --- Title ---
    elements.append(Paragraph("NetScan Device Report", styles['Title']))
    elements.append(Paragraph(f"Generated for: {username}", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    # --- Table data ---
    table_data = [['IP Address', 'Hostname', 'Vendor', 'OS', 'Status']]
    for device in devices:
        table_data.append([
            device.ip_address,
            device.hostname or '-',
            device.vendor or '-',
            (device.operating_system or '-')[:30],  # truncate long OS strings so they fit
            'Online' if device.is_online else 'Offline'
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f6f9')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()

def export_scans_csv(scans):
    """Builds CSV content from a list of Scan objects."""

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Target Range', 'Status', 'Devices Found', 'Started At', 'Completed At'])

    for scan in scans:
        writer.writerow([
            scan.target_range,
            scan.status,
            scan.devices_found,
            scan.started_at.strftime('%Y-%m-%d %H:%M:%S'),
            scan.completed_at.strftime('%Y-%m-%d %H:%M:%S') if scan.completed_at else ''
        ])

    return output.getvalue()