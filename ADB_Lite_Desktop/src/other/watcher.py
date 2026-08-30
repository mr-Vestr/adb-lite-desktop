import os
import time
import threading
import hashlib


def start_install_watcher(config, connector, installer, install_event=None, poll_interval: float = 1.0, debounce: float = 2.0):
    state = {
        'last_hash': None,
        'pending': False,
        'pending_time': 0.0,
    }

    def _hash_file(path):
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()

    def _worker():
        while True:
            try:
                if not config.get('install_on_change', False):
                    state['last_hash'] = None
                    state['pending'] = False
                    time.sleep(poll_interval)
                    continue

                plugin_path = config.get('plugin_path', '')
                if not plugin_path or not os.path.exists(plugin_path):
                    time.sleep(poll_interval)
                    continue

                try:
                    current_hash = _hash_file(plugin_path)
                except OSError:
                    time.sleep(poll_interval)
                    continue

                if state['last_hash'] is None:
                    state['last_hash'] = current_hash
                    time.sleep(poll_interval)
                    continue

                if current_hash != state['last_hash']:
                    state['last_hash'] = current_hash
                    state['pending'] = True
                    state['pending_time'] = time.time()

                if state['pending'] and (time.time() - state['pending_time'] >= debounce):
                    state['pending'] = False
                    if install_event is not None:
                        install_event.set()
                    else:
                        link = connector.current_link
                        if link and connector.check_connection():
                            installer.install(link, plugin_path)

                time.sleep(poll_interval)
            except Exception:
                try:
                    time.sleep(poll_interval)
                except Exception:
                    pass

    thread = threading.Thread(target=_worker, daemon=True, name="install-on-change")
    thread.start()
    return thread
