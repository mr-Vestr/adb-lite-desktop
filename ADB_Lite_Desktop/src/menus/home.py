import os
import sys
import threading
import time
import platform
from src.other.config import ConfigManager
from src.other.utils import Colors
from src.menus.plugin import get_plugin_path
from src.menus.device import scan_and_select_device
from src.menus.lang import select_language, get_translator
from src.menus.config import open_config_file, open_log_file
from src.actions.install import PluginInstaller
from res.config import CHECK_INTERVAL


def input_with_check(prompt: str, device_unavailable: threading.Event, stop_check: threading.Event, config=None, translator=None, install_event=None) -> str:
    if platform.system() == 'Windows':
        import msvcrt
        result = []
        sys.stdout.write(prompt)
        sys.stdout.flush()

        while not stop_check.is_set() and not device_unavailable.is_set():
            if install_event is not None and install_event.is_set():
                return '__INSTALL__'
            if msvcrt.kbhit():
                char = msvcrt.getch()
                if char == b'\r':
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    return ''.join(result)
                elif char == b'\x08':
                    if result:
                        result.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                elif char == b'\x03':
                    raise KeyboardInterrupt
                else:
                    try:
                        char_decoded = char.decode('utf-8')
                        result.append(char_decoded)
                        sys.stdout.write(char_decoded)
                        sys.stdout.flush()
                    except:
                        pass
            time.sleep(0.1)

        if device_unavailable.is_set():
            return None
        raise KeyboardInterrupt
    else:
        import select
        if not sys.stdin.isatty():
            sys.stdout.write(prompt)
            sys.stdout.flush()
            while not stop_check.is_set() and not device_unavailable.is_set():
                if install_event is not None and install_event.is_set():
                    return '__INSTALL__'
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    line = sys.stdin.readline()
                    if line:
                        return line.strip()
                time.sleep(0.1)
            if device_unavailable.is_set():
                return None
            raise KeyboardInterrupt

        try:
            import termios
            import tty
        except ImportError:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            while not stop_check.is_set() and not device_unavailable.is_set():
                if install_event is not None and install_event.is_set():
                    return '__INSTALL__'
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    line = sys.stdin.readline()
                    if line:
                        return line.strip()
                time.sleep(0.1)
            if device_unavailable.is_set():
                return None
            raise KeyboardInterrupt

        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
        except Exception:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            while not stop_check.is_set() and not device_unavailable.is_set():
                if install_event is not None and install_event.is_set():
                    return '__INSTALL__'
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    line = sys.stdin.readline()
                    if line:
                        return line.strip()
                time.sleep(0.1)
            if device_unavailable.is_set():
                return None
            raise KeyboardInterrupt

        try:
            tty.setraw(fd)
            sys.stdout.write(prompt)
            sys.stdout.flush()
            buf = []
            while not stop_check.is_set() and not device_unavailable.is_set():
                if install_event is not None and install_event.is_set():
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    return '__INSTALL__'
                r, _, _ = select.select([sys.stdin], [], [], 0.1)
                if r:
                    try:
                        ch = os.read(fd, 1)
                    except OSError:
                        continue
                    if not ch:
                        continue
                    if ch == b'\x03':
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                        raise KeyboardInterrupt
                    elif ch == b'\x11':
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        sys.stdout.write('\r\n')
                        sys.stdout.flush()
                        try:
                            if config is not None and translator is not None:
                                open_log_file(config, translator)
                            else:
                                pass
                        except Exception:
                            pass
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                        try:
                            tty.setraw(fd)
                        except Exception:
                            pass
                        sys.stdout.write(prompt + ''.join(buf))
                        sys.stdout.flush()
                        continue
                    elif ch == b'\x17':
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        sys.stdout.write('\r\n')
                        sys.stdout.flush()
                        try:
                            if config is not None and translator is not None:
                                open_config_file(config, translator)
                        except Exception:
                            pass
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                        try:
                            tty.setraw(fd)
                        except Exception:
                            pass
                        sys.stdout.write(prompt + ''.join(buf))
                        sys.stdout.flush()
                        continue
                    elif ch in (b'\r', b'\n'):
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        sys.stdout.write('\r\n')
                        sys.stdout.flush()
                        return ''.join(buf).strip()
                    elif ch == b'\x7f':
                        if buf:
                            buf.pop()
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    elif ch == b'\x08':
                        if buf:
                            buf.pop()
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    elif ch == b'\x15':
                        while buf:
                            buf.pop()
                            sys.stdout.write('\b \b')
                        sys.stdout.flush()
                    else:
                        try:
                            c = ch.decode('utf-8')
                            if c.isprintable():
                                buf.append(c)
                                sys.stdout.write(c)
                                sys.stdout.flush()
                        except Exception:
                            pass
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            if device_unavailable.is_set():
                return None
            raise KeyboardInterrupt
        except KeyboardInterrupt:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass
            raise
        except Exception:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

            sys.stdout.write(prompt)
            sys.stdout.flush()
            while not stop_check.is_set() and not device_unavailable.is_set():
                if install_event is not None and install_event.is_set():
                    return '__INSTALL__'
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    line = sys.stdin.readline()
                    if line:
                        return line.strip()
                time.sleep(0.1)
            if device_unavailable.is_set():
                return None
            raise KeyboardInterrupt


def show_install_on_change_menu(config: ConfigManager, translator):
    t = translator
    while True:
        enabled = bool(config.get('install_on_change', False))
        status = t('install_on_change_enabled') if enabled else t('install_on_change_disabled')
        action = t('disable') if enabled else t('enable')

        print(f"\n{Colors.CYAN}{Colors.BOLD}{t('install_on_change_title', status=status)}{Colors.ENDC}")
        print(f"{Colors.BLUE}{Colors.ITALIC}  ({t('install_on_change_desc')}){Colors.ENDC}")
        print(f"\n{Colors.GREEN}  1 — {t('install_on_change_toggle', action=action)}{Colors.ENDC}")
        print(f"{Colors.GREEN}  2 — {t('install_on_change_back')}{Colors.ENDC}")

        try:
            choice = input(f"\n{Colors.CYAN}{t('enter_choice')}{Colors.ENDC}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == '1':
            config.set('install_on_change', not enabled)
            break
        elif choice == '2':
            break
        else:
            print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")
            continue


def show_main_menu(config: ConfigManager, translator, current_link: str, current_device_name: str, current_client_name: str, scanner, connector, installer: PluginInstaller):
    t = translator
    plugin_path = config.get('plugin_path', '')
    filename = os.path.basename(plugin_path) if plugin_path else t('not_selected')

    stop_check = threading.Event()
    device_unavailable = threading.Event()
    connection_rejected = threading.Event()
    install_event = getattr(installer, 'install_event', None)

    def check_connection_periodically():
        while not stop_check.is_set():
            result = connector.check_connection_with_retry()
            if result == 'yes':
                for _ in range(CHECK_INTERVAL):
                    if stop_check.is_set():
                        return
                    time.sleep(1)
            elif result == 'no':
                connection_rejected.set()
                stop_check.set()
                return
            else:
                device_unavailable.set()
                stop_check.set()
                return

    check_thread = threading.Thread(target=check_connection_periodically, daemon=True)
    check_thread.start()

    print(f"\n{Colors.CYAN}{Colors.BOLD}{t('main_menu')}{Colors.ENDC}")
    print(f"{Colors.BLUE}  IP: {current_link}{Colors.ENDC}")
    print(f"{Colors.BLUE}  {t('device_name', name=current_device_name)}{Colors.ENDC}")
    print(f"{Colors.BLUE}  {t('client_name', name=current_client_name)}{Colors.ENDC}")
    print(f"{Colors.BLUE}  {t('plugin_file', filename=filename)}{Colors.ENDC}")
    print(f"\n{Colors.GREEN}  1 — {t('option_install')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  2 — {t('option_install_on_change')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  3 — {t('option_change_path')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  4 — {t('option_select_device')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  5 — {t('option_change_language')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  6 — {t('option_config_file')} (Ctrl+W){Colors.ENDC}")
    print(f"{Colors.GREEN}  7 — {t('option_log_file')} (Ctrl+Q){Colors.ENDC}")

    while True:
        if connection_rejected.is_set():
            print(f"\n{Colors.WARNING}{t('connection_rejected')}{Colors.ENDC}")
            result = scan_and_select_device(config, t, scanner, connector)
            if result[0]:
                show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
            return

        if device_unavailable.is_set():
            print(f"\n\n{Colors.FAIL}{t('device_not_available')}{Colors.ENDC}")
            print(f"\n{Colors.GREEN}1 — {t('reconnect_device', name=current_device_name)}{Colors.ENDC}")
            print(f"{Colors.GREEN}2 — {t('search_devices_option')}{Colors.ENDC}")
            try:
                choice = input(f"\n{Colors.CYAN}{t('enter_choice')}{Colors.ENDC}").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if choice == '1':
                if connector.connect(current_link, current_device_name):
                    device_unavailable.clear()
                    show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
                else:
                    result = scan_and_select_device(config, t, scanner, connector)
                    if result[0]:
                        device_unavailable.clear()
                        show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
                return
            elif choice == '2':
                result = scan_and_select_device(config, t, scanner, connector)
                if result[0]:
                    device_unavailable.clear()
                    show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
                return
            else:
                break

        try:
            choice = input_with_check(f"\n{Colors.CYAN}{t('enter_choice')}{Colors.ENDC}", device_unavailable, stop_check, config, t, install_event)
        except (EOFError, KeyboardInterrupt):
            if connection_rejected.is_set():
                print(f"\n{Colors.WARNING}{t('connection_rejected')}{Colors.ENDC}")
                result = scan_and_select_device(config, t, scanner, connector)
                if result[0]:
                    show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
                return
            stop_check.set()
            break

        if choice == '__INSTALL__':
            if install_event is not None:
                install_event.clear()
            link = connector.current_link
            if link and connector.check_connection():
                plugin_path = config.get('plugin_path', '')
                if plugin_path and os.path.exists(plugin_path):
                    installer.install(link, plugin_path)
            show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        if choice is None:
            if connection_rejected.is_set():
                print(f"\n{Colors.WARNING}{t('connection_rejected')}{Colors.ENDC}")
                result = scan_and_select_device(config, t, scanner, connector)
                if result[0]:
                    show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
                return

            print(f"\n\n\n{Colors.FAIL}{t('device_not_available')}{Colors.ENDC}")
            print(f"\n{Colors.GREEN}1 — {t('reconnect_device', name=current_device_name)}{Colors.ENDC}")
            print(f"{Colors.GREEN}2 — {t('search_devices_option')}{Colors.ENDC}")
            try:
                choice = input(f"\n{Colors.CYAN}{t('enter_choice')}{Colors.ENDC}").strip()
            except (EOFError, KeyboardInterrupt):
                stop_check.set()
                break

            if choice == '1':
                if connector.connect(current_link, current_device_name):
                    device_unavailable.clear()
                    show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
                else:
                    result = scan_and_select_device(config, t, scanner, connector)
                    if result[0]:
                        device_unavailable.clear()
                        show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
                return
            elif choice == '2':
                result = scan_and_select_device(config, t, scanner, connector)
                if result[0]:
                    device_unavailable.clear()
                    show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
                return
            else:
                stop_check.set()
                break

        if choice == '1':
            stop_check.set()
            plugin_path = config.get('plugin_path', '')
            if not plugin_path or not os.path.exists(plugin_path):
                plugin_path = get_plugin_path(config, t)
            installer.install(current_link, plugin_path)
            show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        elif choice == '2':
            stop_check.set()
            print("\n")
            show_install_on_change_menu(config, t)
            show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        elif choice == '3':
            stop_check.set()
            print("\n")
            config.set('plugin_path', '')
            get_plugin_path(config, t)
            show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        elif choice == '4':
            stop_check.set()
            print("\n")
            result = scan_and_select_device(config, t, scanner, connector)
            if result[0]:
                show_main_menu(config, t, result[0], result[1], result[2], scanner, connector, installer)
            return

        elif choice == '5':
            stop_check.set()
            print("\n")
            new_lang = select_language(config, t)
            new_t = get_translator(new_lang)
            scanner.set_translator(new_t)
            connector.set_translator(new_t)
            installer.set_translator(new_t)
            show_main_menu(config, new_t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        elif choice == '6':
            open_config_file(config, t)
            print()
            show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        elif choice == '7':
            stop_check.set()
            print("\n")
            open_log_file(config, t)
            print()
            show_main_menu(config, t, current_link, current_device_name, current_client_name, scanner, connector, installer)
            return

        else:
            print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")
