from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.scan import Scan, ScanDevice
from app.models.device import Device

app = create_app()

with app.app_context():
    # 1. Get our existing user
    user = User.query.first()
    print("Found user:", user.username)

    # 2. Create a fresh scan (so we don't reuse leftover test data)
    test_scan = Scan(
        target_range='192.168.1.0/24',
        status='completed',
        user_id=user.id
    )
    db.session.add(test_scan)
    db.session.commit()
    print("Created scan:", test_scan)

    # 3. Create a Device (a unique host on the network)
    test_device = Device(
        ip_address='192.168.1.50',
        mac_address='AA:BB:CC:DD:EE:FF',
        hostname='test-laptop',
        vendor='Dell Inc.',
        user_id=user.id
    )
    db.session.add(test_device)
    db.session.commit()
    print("Created device:", test_device)

    # 4. Create the ScanDevice link row — this records
    #    "this device was seen during this scan, with these ports open"
    link = ScanDevice(
        scan_id=test_scan.id,
        device_id=test_device.id,
        open_ports='22,80,443',
        services='ssh,http,https'
    )
    db.session.add(link)
    db.session.commit()
    print("Created link:", link)

    # 5. Walk the full chain: Scan -> ScanDevice -> Device
    print("\n--- Walking the relationship chain ---")
    print("test_scan.devices:", test_scan.devices)
    print("First linked device's IP:", test_scan.devices[0].device.ip_address)
    print("First linked device's open ports:", test_scan.devices[0].open_ports)