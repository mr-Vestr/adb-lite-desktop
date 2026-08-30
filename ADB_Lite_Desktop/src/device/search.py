import time
import threading
from typing import List, Dict
from res.config import TIMEOUT_SCAN
from src.other.utils import Colors


class DeviceScanner:
    def __init__(self, translator=None):
        self.zeroconf = None
        self.devices = []
        self.t = translator or (lambda key, **kwargs: key)
        self._stop_event = threading.Event()

    def set_translator(self, translator):
        self.t = translator or (lambda key, **kwargs: key)

    def scan(self, timeout: float = TIMEOUT_SCAN) -> List[Dict[str, str]]:
        self.devices = []
        self._stop_event.clear()

        try:
            from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

            class ADBLiteListener(ServiceListener):
                def __init__(self, scanner):
                    self.scanner = scanner

                def add_service(self, zc, type_, name):
                    try:
                        info = zc.get_service_info(type_, name)
                        if info:
                            ip = '.'.join(str(b) for b in info.addresses[0]) if info.addresses else None
                            if ip:
                                device = {
                                    'name': info.properties.get(b'device', b'Unknown').decode('utf-8', errors='ignore'),
                                    'manufacturer': info.properties.get(b'manufacturer', b'Unknown').decode('utf-8', errors='ignore'),
                                    'version': info.properties.get(b'version', b'1.0').decode('utf-8', errors='ignore'),
                                    'ip': ip,
                                    'port': info.port,
                                    'link': f"http://{ip}:{info.port}",
                                    'client': info.properties.get(b'app', b'exteraGram').decode('utf-8', errors='ignore'),
                                    'key': info.properties.get(b'key', b'').decode('utf-8', errors='ignore')
                                }
                                self.scanner.devices.append(device)
                    except Exception:
                        pass

                def remove_service(self, zc, type_, name):
                    pass

                def update_service(self, zc, type_, name):
                    pass

            self.zeroconf = Zeroconf()
            listener = ADBLiteListener(self)
            browser = ServiceBrowser(self.zeroconf, "_adblite._tcp.local.", listener)
            start_time = time.time()
            while not self._stop_event.is_set():
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    break
                remaining = timeout - elapsed
                self._stop_event.wait(min(0.1, remaining))
            
            self.zeroconf.close()
            self.zeroconf = None

        except ImportError:
            print(f"{Colors.FAIL}{self.t('zeroconf_not_installed')}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}{self.t('mdns_failed', error=e)}{Colors.ENDC}")

        return self.devices

    def stop_scan(self):
        self._stop_event.set()
