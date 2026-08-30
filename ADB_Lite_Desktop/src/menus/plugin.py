import os
from src.other.config import ConfigManager
from src.other.utils import Colors


def get_plugin_path(config: ConfigManager, translator) -> str:
    t = translator
    plugin_path = config.get('plugin_path', '')
    if plugin_path and os.path.exists(plugin_path):
        return plugin_path
    while True:
        try:
            path = input(f"{Colors.CYAN}{t('select_plugin_path')}{Colors.ENDC}").strip()
        except (EOFError, KeyboardInterrupt):
            raise
        path = path.strip('"\'')
        print("\n")

        if os.path.exists(path):
            config.set('plugin_path', path)
            return path
        else:
            print(f"{Colors.FAIL}{t('file_not_found', path=path)}{Colors.ENDC}")
