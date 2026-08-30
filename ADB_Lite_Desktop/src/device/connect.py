import threading
import platform
import requests
from src.other.config import ConfigManager
from res.config import TIMEOUT_CONNECT, SUPPORT
from src.other.utils import Colors


class DeviceConnector:
    def __init__(self, config: ConfigManager, translator):
        self.config = config
        self.t = translator
        self.current_link = None
        self.current_device_name = None

    def set_translator(self, translator):
        self.t = translator

    def connect(self, link: str, device_name: str = "Python Client") -> bool:
        print(f"{Colors.CYAN}{self.t('connecting_to', device=device_name)}{Colors.ENDC}")
        print(f"{Colors.WARNING}{self.t('cancel_hint')}{Colors.ENDC}")
        result = [None, None]
        done = threading.Event()
        token = self.config.get_device_token()
        pc_address = ConfigManager.get_local_address()

        def do_request():
            try:
                payload = f"adb_lite_s\n{platform.node()}\n{platform.system()}\n{token}\n{pc_address}\n{SUPPORT}"
                response = requests.post(
                    f"{link}/connect",
                    data=payload,
                    timeout=TIMEOUT_CONNECT
                )
                result[0] = response
            except Exception as e:
                result[1] = e
            finally:
                done.set()

        thread = threading.Thread(target=do_request, daemon=True)
        thread.start()
        try:
            while not done.is_set():
                done.wait(timeout=0.5)
        except KeyboardInterrupt:
            print(f"{Colors.WARNING}{self.t('connection_rejected')}{Colors.ENDC}\n")
            return False

        error = result[1]
        if error is not None:
            print(f"{Colors.FAIL}{self.t('connection_failed', device=link)}{Colors.ENDC}")
            print(f"{Colors.FAIL}{self.t('error_prefix', error=error)}{Colors.ENDC}")
            return False

        response = result[0]
        if response is not None:
            if response.status_code == 200:
                result_text = response.content.decode('utf-8').strip()
                if result_text == 'yes':
                    print(f"{Colors.GREEN}{self.t('connection_confirmed')}{Colors.ENDC}")
                    self.current_link = link
                    self.current_device_name = device_name
                    return True
                else:
                    print(f"{Colors.WARNING}{self.t('connection_rejected')}{Colors.ENDC}\n")
                    return False
            else:
                print(f"{Colors.FAIL}{self.t('connection_failed', device=link)}{Colors.ENDC}")
                return False

        return False

    def check_connection(self) -> bool:
        if not self.current_link:
            return False
        try:
            token = self.config.get_device_token()
            payload = f"{token}\n{self.current_device_name}"
            response = requests.post(
                f"{self.current_link}/check",
                data=payload,
                timeout=10
            )
            if response.status_code == 200:
                result_text = response.text.strip()
                return result_text == 'yes'
        except Exception:
            pass
        return False

    def check_connection_with_retry(self):
        if not self.current_link:
            return 'no'

        token = self.config.get_device_token()
        for _ in range(12):
            try:
                payload = f"{token}\n{self.current_device_name}"
                response = requests.post(
                    f"{self.current_link}/check",
                    data=payload,
                    timeout=5
                )
                if response.status_code == 200:
                    result_text = response.text.strip()
                    if result_text == 'yes':
                        return 'yes'
                    elif result_text == 'no':
                        return 'no'
            except requests.Timeout:
                pass
            except Exception:
                pass
            
        return 'timeout'
