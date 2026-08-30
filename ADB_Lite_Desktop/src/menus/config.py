import os
import platform
import subprocess
from src.other.config import ConfigManager
from src.other.utils import Colors


def _popen_detached(cmd):
    kwargs = dict(
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )
    if platform.system() != 'Windows':
        kwargs['start_new_session'] = True
    else:
        kwargs['creationflags'] = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
    return subprocess.Popen(cmd, **kwargs)


def open_config_file(config: ConfigManager, translator):
    config_path = config.config_file
    system = platform.system()
    t = translator
    try:
        if system == 'Windows':
            _popen_detached(['notepad.exe', config_path])
        elif system == 'Darwin':
            _popen_detached(['open', '-a', 'TextEdit', config_path])
        else:
            _popen_detached(['xdg-open', config_path])
        print(f"{Colors.GREEN}{t('config_open_success')}{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}{t('config_open_error', error=str(e))}{Colors.ENDC}")
        return False


def open_log_file(config: ConfigManager, translator):
    log_path = os.path.join(config.config_dir, 'log.txt')
    system = platform.system()
    t = translator

    if not os.path.exists(log_path):
        print(f"{Colors.FAIL}{t('log_file_not_found')}{Colors.ENDC}")
        return False

    try:
        if system == 'Windows':
            _popen_detached(['notepad.exe', log_path])
        elif system == 'Darwin':
            _popen_detached(['open', '-a', 'TextEdit', log_path])
        else:
            _popen_detached(['xdg-open', log_path])
        print(f"{Colors.GREEN}{t('log_file_open_success')}{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}{t('log_file_open_error', error=str(e))}{Colors.ENDC}")
        return False
