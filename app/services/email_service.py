from flask_mail import Message
from app.extensions import mail
from app.models.notification import Notification


def send_new_device_alert(recipient_email, device):
    """Sends an email alert when a new device is discovered on the network."""

    subject = f"New Device Detected: {device.ip_address}"

    body = f"""
A new device was just discovered on your network.

IP Address: {device.ip_address}
Hostname: {device.hostname or 'Unknown'}
MAC Address: {device.mac_address or 'Unknown'}
Vendor: {device.vendor or 'Unknown'}
First Seen: {device.first_seen.strftime('%B %d, %Y at %I:%M %p')}

If you don't recognize this device, review your network security settings.

— NetScan Dashboard
"""

    msg = Message(subject=subject, recipients=[recipient_email], body=body)

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False