import nmap
from datetime import datetime


def run_network_scan(target_range):
    """
    Runs an Nmap scan against the given target range (e.g. '192.168.1.0/24')
    and returns a list of dicts, one per discovered host.

    Uses Nmap arguments:
      -sn  : ping scan only (host discovery), no port scan — fast first pass
    Then for hosts that are up, we run a fuller scan:
      -O   : attempt OS detection (requires admin/root privileges)
      -sV  : service/version detection on open ports
    """
    scanner = nmap.PortScanner()

    results = []

    try:
        # Step 1: quick host discovery — who's actually alive on this range?
        scanner.scan(hosts=target_range, arguments='-sn')
        live_hosts = scanner.all_hosts()

        # Step 2: for each live host, do a deeper scan for ports/services/OS
        for host_ip in live_hosts:
            try:
                # -O requires elevated privileges; if it fails, we still
                # want port/service data, so we catch failures per-host
                scanner.scan(hosts=host_ip, arguments='-sV -O --host-timeout 30s')
            except Exception:
                # Fallback: service scan only, without OS detection
                scanner.scan(hosts=host_ip, arguments='-sV --host-timeout 30s')

            host_data = scanner[host_ip]

            # --- Extract basic info ---
            hostname = host_data.hostname() or None
            status = host_data.state()  # 'up' or 'down'

            # --- MAC address & vendor (only available on local network scans) ---
            mac_address = None
            vendor = None
            if 'mac' in host_data['addresses']:
                mac_address = host_data['addresses']['mac']
                vendor_dict = host_data.get('vendor', {})
                vendor = vendor_dict.get(mac_address) if vendor_dict else None

            # --- OS detection (best guess, often unavailable without admin rights) ---
            operating_system = None
            if 'osmatch' in host_data and len(host_data['osmatch']) > 0:
                operating_system = host_data['osmatch'][0]['name']

            # --- Open ports & services ---
            open_ports = []
            services = []
            if 'tcp' in host_data:
                for port, port_data in host_data['tcp'].items():
                    if port_data['state'] == 'open':
                        open_ports.append(str(port))
                        service_name = port_data.get('name', 'unknown')
                        if service_name not in services:
                            services.append(service_name)

            results.append({
                'ip_address': host_ip,
                'hostname': hostname,
                'status': status,
                'mac_address': mac_address,
                'vendor': vendor,
                'operating_system': operating_system,
                'open_ports': ','.join(open_ports),
                'services': ','.join(services),
            })

        return {'success': True, 'devices': results, 'error': None}

    except Exception as e:
        return {'success': False, 'devices': [], 'error': str(e)}