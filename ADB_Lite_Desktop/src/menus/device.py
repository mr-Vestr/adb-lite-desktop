from src.other.config import ConfigManager
from src.other.utils import Colors
from res.config import TIMEOUT_SCAN
from src.device.search import DeviceScanner
from src.device.connect import DeviceConnector


def connect_manually(config: ConfigManager, translator, connector: DeviceConnector) -> tuple:
    t = translator
    print(f"{Colors.CYAN}{t('enter_address')}{Colors.ENDC}")
    try:
        address = input().strip()
    except (EOFError, KeyboardInterrupt):
        raise

    if address.startswith('http://'):
        address = address[7:]
    elif address.startswith('https://'):
        address = address[8:]

    if ':' not in address:
        print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")
        return None, None, None
    
    link = f"http://{address}"
    device_name = "Manual Connection"
    
    if connector.connect(link, device_name):
        try:
            import requests
            response = requests.get(f"{link}/test", timeout=5)
            if response.status_code == 200:
                device_info = response.json()
                device_name = device_info.get('device', device_name)
                client_name = device_info.get('app', 'Unknown')
            else:
                client_name = "Unknown"
        except Exception:
            client_name = "Unknown"
        
        config.add_device(link, device_name, client_name, '')
        return link, device_name, client_name
    else:
        return None, None, None


def scan_and_select_device(config: ConfigManager, translator, scanner: DeviceScanner, connector: DeviceConnector, timeout: float = TIMEOUT_SCAN) -> tuple:
    t = translator
    print(f"{Colors.CYAN}{t('searching_devices')}{Colors.ENDC}")
    print(f"{Colors.WARNING}{t('show_found_hint')}{Colors.ENDC}")
    try:
        devices = scanner.scan(timeout)
    except KeyboardInterrupt:
        scanner.stop_scan()
        devices = scanner.devices

    if not devices:
        print(f"{Colors.FAIL}{t('no_devices')}{Colors.ENDC}")
        print(f"\n{Colors.GREEN}1 — {t('search_again')}{Colors.ENDC}")
        print(f"{Colors.GREEN}2 — {t('connect_manually')}{Colors.ENDC}")
        while True:
            try:
                choice = input(f"\n{Colors.CYAN}{t('select_device')}{Colors.ENDC}").strip()
            except (EOFError, KeyboardInterrupt):
                raise
            if choice == '1':
                print("\n")
                return scan_and_select_device(config, translator, scanner, connector, timeout * 2)
            elif choice == '2':
                print("\n")
                result = connect_manually(config, t, connector)
                if result[0]:
                    return result
                else:
                    return scan_and_select_device(config, translator, scanner, connector, timeout)
            else:
                print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")

    for i, device in enumerate(devices, 1):
        _display_link = device['link'].replace('http://', '', 1).replace('https://', '', 1)
        print(f"{Colors.GREEN}{i} — {t('device_found', link=_display_link, device=device['name'], client=device['client'])}{Colors.ENDC}")
    print(f"{Colors.GREEN}{len(devices) + 1} — {t('connect_manually')}{Colors.ENDC}")
    print(f"{Colors.GREEN}{len(devices) + 2} — {t('search_again')}{Colors.ENDC}")

    while True:
        try:
            choice = input(f"\n{Colors.CYAN}{t('select_device')}{Colors.ENDC}").strip()
        except (EOFError, KeyboardInterrupt):
            raise
        try:
            idx = int(choice) - 1
        except ValueError:
            print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")
            continue
        if 0 <= idx < len(devices):
            selected = devices[idx]
            if connector.connect(selected['link'], selected['name']):
                config.add_device(
                    selected['link'],
                    selected['name'],
                    selected['client'],
                    selected.get('key', '')
                )
                return selected['link'], selected['name'], selected['client']
            else:
                return scan_and_select_device(config, translator, scanner, connector, timeout)
        elif idx == len(devices):
            print("\n")
            result = connect_manually(config, t, connector)
            if result[0]:
                return result
            else:
                return scan_and_select_device(config, translator, scanner, connector, timeout)
        elif idx == len(devices) + 1:
            print("\n")
            return scan_and_select_device(config, translator, scanner, connector, timeout * 2)
        else:
            print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")


def try_connect_saved(config: ConfigManager, translator, connector: DeviceConnector) -> tuple:
    last_device = config.get('last_device')
    if not last_device:
        return None, None, None
    link = last_device.get('link')
    name = last_device.get('name', 'Unknown')
    client = last_device.get('client', 'Unknown')
    if connector.connect(link, name):
        return link, name, client
    config.set('last_device', None)
    return None, None, None
