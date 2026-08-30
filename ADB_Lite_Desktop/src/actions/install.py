import os
import threading
import requests
from src.other.config import ConfigManager
from src.other.utils import Colors


class PluginInstaller:
    def __init__(self, config: ConfigManager, translator):
        self.config = config
        self.t = translator

    def set_translator(self, translator):
        self.t = translator

    def install(self, link: str, plugin_path: str) -> bool:
        if not os.path.exists(plugin_path):
            print(f"{Colors.FAIL}{self.t('file_not_found', path=plugin_path)}{Colors.ENDC}")
            return False

        print(f"\n{Colors.CYAN}{self.t('installing')}{Colors.ENDC}")

        result = [None, None]
        done = threading.Event()

        def do_request():
            try:
                filename = os.path.basename(plugin_path)
                with open(plugin_path, 'rb') as f:
                    file_data = f.read()
                headers = {
                    'X-Filename': filename,
                    'X-Device-Token': self.config.get_device_token(),
                    'Content-Type': 'application/octet-stream'
                }
                response = requests.post(
                    f"{link}/install",
                    data=file_data,
                    headers=headers,
                    timeout=60
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
            raise

        error = result[1]
        if error is not None:
            print(f"{Colors.FAIL}{self.t('install_failed', error=str(error))}{Colors.ENDC}")
            return False

        response = result[0]
        if response is not None:
            if response.status_code == 200:
                result_text = response.content.decode('utf-8').strip()
                if result_text.startswith('yes'):
                    print(f"{Colors.GREEN}{self.t('install_success')}{Colors.ENDC}")
                    return True
                else:
                    error_msg = result_text
                    if 'error:' in result_text:
                        error_msg = result_text.split('error:')[1].strip()
                    print(f"{Colors.FAIL}{self.t('install_failed', error=error_msg)}{Colors.ENDC}")
                    return False
            else:
                print(f"{Colors.FAIL}{self.t('install_failed', error=f'HTTP {response.status_code}')}{Colors.ENDC}")
                return False

        return False
