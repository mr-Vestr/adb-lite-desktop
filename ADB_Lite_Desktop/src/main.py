import sys
import os
import platform
import traceback
from datetime import datetime, timezone
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.other.config import ConfigManager
from src.other.utils import Colors, ASCII_LOGO, set_console_title, clear_screen
from src.device.search import DeviceScanner
from src.device.connect import DeviceConnector
from src.actions.install import PluginInstaller
from src.menus.plugin import get_plugin_path
from src.menus.device import scan_and_select_device, try_connect_saved
from src.menus.home import show_main_menu
from src.menus.lang import get_translator
from res.config import VERSION


class Logger:
    def __init__(self, log_file_path):
        self.log_file = open(log_file_path, 'a', encoding='utf-8')
        self.terminal = sys.stdout
        self.last_was_newline = True
        self.session_started = False
        self.lock = threading.Lock()

    def _get_timestamp(self):
        now = datetime.now(timezone.utc)
        utc_offset = now.astimezone().strftime('%z')
        return now.strftime('%d.%m.%Y %H:%M') + f' UTC{utc_offset}'

    def write(self, message):
        self.terminal.write(message)
        
        if message and not self.session_started:
            timestamp = self._get_timestamp()
            self.log_file.write(f"\n\n\n\n\n\n========= NEW {timestamp} ========\n")
            self.session_started = True
        
        if message:
            self.log_file.write(message)
        
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()

    def log_key(self, key):
        with self.lock:
            timestamp = self._get_timestamp()
            self.log_file.write(f"[KEY {timestamp}] {key}\n")
            self.log_file.flush()


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        return
    
    logger = getattr(sys, '_logger', None)
    if logger:
        timestamp = logger._get_timestamp()
        logger.log_file.write(f"\n\n========= CRITICAL ERROR {timestamp} ========\n")
        logger.log_file.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        logger.log_file.write("\n")
        logger.log_file.flush()
    
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    set_console_title("ADB Lite Desktop")
    logger = None
    try:
        config = ConfigManager()
        log_file_path = os.path.join(config.config_dir, 'log.txt')
        logger = Logger(log_file_path)
        sys.stdout = logger
        sys.stderr = logger
        sys._logger = logger
        sys.excepthook = handle_exception
        
        if platform.system() == 'Windows':
            try:
                import keyboard
                import time as _time
                last_log_open = [0.0]
                last_config_open = [0.0]
                ctrl_down = [False]

                def on_key_press(event):
                    logger.log_key(event.name)
                    try:
                        name = (event.name or '').lower()
                        if event.event_type == 'down':
                            if name in ('ctrl', 'control', 'left ctrl', 'right ctrl'):
                                ctrl_down[0] = True
                            elif name in ('q', 'й') or getattr(event, 'scan_code', None) == 16:
                                if ctrl_down[0]:
                                    now = _time.time()
                                    if now - last_log_open[0] > 1.0:
                                        last_log_open[0] = now
                                        from src.menus.config import open_log_file
                                        t_now = get_translator(config.get('language', 'en'))
                                        open_log_file(config, t_now)
                            elif name in ('w', 'ц') or getattr(event, 'scan_code', None) == 17:
                                if ctrl_down[0]:
                                    now = _time.time()
                                    if now - last_config_open[0] > 1.0:
                                        last_config_open[0] = now
                                        from src.menus.config import open_config_file
                                        t_now = get_translator(config.get('language', 'en'))
                                        open_config_file(config, t_now)
                        elif event.event_type == 'up':
                            if name in ('ctrl', 'control', 'left ctrl', 'right ctrl'):
                                ctrl_down[0] = False
                    except Exception:
                        pass
                keyboard.hook(on_key_press)
            except ImportError:
                pass
            except Exception:
                pass
        
        lang = config.get('language', 'en')
        t = get_translator(lang)

        from src.other import updater
        updater.cleanup_leftover()
        updater.check_for_updates_on_load(config)

        scanner = DeviceScanner(translator=t)
        connector = DeviceConnector(config, t)
        installer = PluginInstaller(config, t)

        from src.other import watcher
        install_event = threading.Event()
        installer.install_event = install_event
        watcher.start_install_watcher(config, connector, installer, install_event=install_event)

        clear_screen()
        print(ASCII_LOGO)

        update_info = updater.get_saved_update(config)
        if update_info and str(update_info.get('version', '')) != str(VERSION):
            if updater.show_update_prompt(config, update_info, t):
                os._exit(0)
                return

        from src.other.shortcut import ensure_start_menu_shortcut
        shortcut_status = ensure_start_menu_shortcut()
        if shortcut_status:
            if shortcut_status == 'created':
                print(f"{Colors.GREEN}{t('shortcut_created')}{Colors.ENDC}")
            else:
                print(f"{Colors.GREEN}{t('shortcut_updated')}{Colors.ENDC}")

        saved_result = try_connect_saved(config, t, connector)
        if saved_result[0]:
            show_main_menu(config, t, saved_result[0], saved_result[1], saved_result[2], scanner, connector, installer)
            return

        if config.get('last_device'):
            try:
                choice = input(f"\n{Colors.CYAN}{t('connect_to_another')}{Colors.ENDC}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                raise
            if choice != 'y':
                return

        result = scan_and_select_device(config, t, scanner, connector)
        if result[0]:
            show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)

    except KeyboardInterrupt:
        try:
            print(f"\n{Colors.BLUE}{t('goodbye')}{Colors.ENDC}")
        except Exception:
            pass
    except Exception as e:
        try:
            t = get_translator('en')
            print(f"\n{Colors.FAIL}{t('fatal_error', error=e)}{Colors.ENDC}")
        except Exception:
            pass
        raise
    finally:
        try:
            import keyboard
            keyboard.unhook_all()
        except Exception:
            pass
        if logger:
            try:
                logger.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()
