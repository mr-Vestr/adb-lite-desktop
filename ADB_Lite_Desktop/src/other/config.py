import os
import json
import time
import locale
import platform
import random
import string
import socket
from typing import Dict, Any
from res.config import CONFIG_FILENAME, APP_NAME


class ConfigManager:
    def __init__(self, app_name: str = APP_NAME):
        self.app_name = app_name
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, CONFIG_FILENAME)
        self.config = self._load_or_create()

    def _get_config_dir(self) -> str:
        system = platform.system()
        if system == 'Windows':
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
        elif system == 'Darwin':
            base_dir = os.path.expanduser('~/Library/Application Support')
        else:
            base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        config_dir = os.path.join(base_dir, self.app_name)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def _load_or_create(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                if not config.get('device_token'):
                    config['device_token'] = self._generate_device_token()
                    self._save(config)
                return config
            except (json.JSONDecodeError, IOError):
                pass

        default_config = {
            "plugin_path": "",
            "devices": [],
            "language": self._detect_language(),
            "last_device": None,
            "device_token": self._generate_device_token()
        }

        self._save(default_config)
        return default_config

    @staticmethod
    def _generate_device_token() -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=30))

    def get_device_token(self) -> str:
        token = self.config.get('device_token')
        if not token:
            token = self._generate_device_token()
            self.set('device_token', token)
        return token

    @staticmethod
    def get_local_address() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = socket.gethostbyname(socket.gethostname())
            finally:
                s.close()
            return ip
        except Exception:
            return platform.node()

    def _detect_language(self) -> str:
        try:
            lang = locale.getdefaultlocale()[0]
            if lang and lang.startswith('ru'):
                return 'ru'
        except Exception:
            pass
        return 'en'

    def _save(self, config: Dict[str, Any]):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self._save(self.config)

    def add_device(self, link: str, name: str, client: str, device_key: str = ''):
        devices = self.config.get('devices', [])
        devices = [d for d in devices if d.get('link') != link]
        entry = {
            'link': link,
            'name': name,
            'client': client,
            'last_connected': time.time()
        }
        if device_key:
            entry['key'] = device_key
        devices.append(entry)
        self.set('devices', devices)
        self.set('last_device', {'link': link, 'name': name, 'client': client, 'key': device_key})
