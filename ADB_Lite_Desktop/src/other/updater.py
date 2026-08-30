import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import threading
import webbrowser
import requests
from res.config import VERSION, UPDATE_FILENAME, UPDATE_URL, OLD_EXE_SUFFIX
from src.other.utils import Colors


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def _update_file_path(config) -> str:
    return os.path.join(config.config_dir, UPDATE_FILENAME)


def _save_update(config, data: dict):
    path = _update_file_path(config)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _clear_update(config):
    path = _update_file_path(config)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def get_saved_update(config):
    path = _update_file_path(config)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def check_for_updates(config):
    if not is_frozen():
        return
    try:
        resp = requests.get(UPDATE_URL, timeout=20)
        if resp.status_code != 200:
            return
        info = resp.json()
        remote = str(info.get('version', ''))
        if remote and remote != str(VERSION):
            _save_update(config, info)
        else:
            _clear_update(config)
    except Exception:
        pass


def check_for_updates_on_load(config):
    if not is_frozen():
        return

    def _run():
        time.sleep(1.0)
        check_for_updates(config)

    threading.Thread(target=_run, daemon=True).start()


def _changelog_for(info: dict, lang: str) -> str:
    if lang == 'ru':
        return info.get('changelog_ru', '')
    return info.get('changelog_en', '')


def open_view(info: dict):
    url = info.get('view', '')
    if not url:
        return
    
    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.Popen(['cmd', '/c', 'start', '', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, close_fds=True, creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
        elif system == 'Darwin':
            subprocess.Popen(['open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, close_fds=True)
        else:
            subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, close_fds=True, start_new_session=True)
    except Exception:
        try:
            webbrowser.open(url)
        except Exception:
            pass


def cleanup_leftover():
    try:
        if not is_frozen():
            return
        cur_exe = os.path.abspath(sys.executable)
        exe_dir = os.path.dirname(cur_exe)
        exe_name = os.path.basename(cur_exe)
        stem = os.path.splitext(exe_name)[0]

        def _worker():
            time.sleep(3)
            for _ in range(12):
                removed_any = False
                import glob
                patterns = [
                    os.path.join(exe_dir, stem + OLD_EXE_SUFFIX),
                    os.path.join(exe_dir, "*_oldadblite.exe"),
                    os.path.join(exe_dir, "*_old*.exe"),
                ]
                seen = set()
                for pat in patterns:
                    for p in glob.glob(pat):
                        if p in seen:
                            continue
                        seen.add(p)
                        if os.path.normcase(os.path.abspath(p)) == os.path.normcase(cur_exe):
                            continue
                        try:
                            if os.path.exists(p):
                                os.remove(p)
                                removed_any = True
                        except OSError:
                            pass
                if not seen:
                    return
                still = any(os.path.exists(p) for p in seen)
                if not still:
                    return
                time.sleep(0.5)

        threading.Thread(target=_worker, daemon=True, name="cleanup-old").start()
    except Exception:
        pass


def _download_to(path: str, url: str) -> bool:
    try:
        resp = requests.get(url, stream=True, timeout=120, allow_redirects=True)
        resp.raise_for_status()
        tmp = path + '.part'
        with open(tmp, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                if chunk:
                    f.write(chunk)
        os.replace(tmp, path)
        with open(path, 'rb') as f:
            head = f.read(2)
        if head != b'MZ':
            return False
        if os.path.getsize(path) < 1024:
            return False
        return True
    except Exception:
        try:
            if os.path.exists(path + '.part'):
                os.remove(path + '.part')
        except OSError:
            pass
        return False


def apply_update(config, info: dict, t) -> bool:
    if not is_frozen():
        open_view(info)
        return False
    if platform.system() != 'Windows':
        open_view(info)
        return False

    link = info.get('link', '')
    if not isinstance(link, str) or not link:
        open_view(info)
        return False

    cur_exe = os.path.abspath(sys.executable)
    exe_dir = os.path.dirname(cur_exe)
    exe_name = os.path.basename(cur_exe)
    old_exe = os.path.join(exe_dir, os.path.splitext(exe_name)[0] + OLD_EXE_SUFFIX)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.tmp')
    os.close(tmp_fd)
    if not _download_to(tmp_path, link):
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False

    try:
        if os.path.exists(old_exe):
            os.remove(old_exe)
        os.rename(cur_exe, old_exe)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False
    
    try:
        shutil.move(tmp_path, cur_exe)
    except Exception:
        try:
            os.rename(old_exe, cur_exe)
        except OSError:
            pass
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False
    
    try:
        env = os.environ.copy()
        for k in [k for k in env if k.startswith("_PYI_") or k == "_MEIPASS"]:
            env.pop(k, None)
        if hasattr(sys, "_MEIPASS"):
            mei = os.path.normcase(sys._MEIPASS.rstrip("\\/"))
            env["PATH"] = os.pathsep.join(
                p for p in env.get("PATH", "").split(os.pathsep)
                if os.path.normcase(p.rstrip("\\/")) != mei
            )
        flags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
        subprocess.Popen([cur_exe], cwd=exe_dir, env=env, creationflags=flags)
    except Exception:
        try:
            flags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
            subprocess.Popen([cur_exe], cwd=exe_dir, creationflags=flags)
        except Exception:
            pass

    return True


def show_update_prompt(config, info: dict, t) -> bool:
    version = str(info.get('version', ''))
    print(f"\n{Colors.CYAN}{Colors.BOLD}{t('update_available_title', version=version)}{Colors.ENDC}")
    changelog = _changelog_for(info, config.get('language', 'en'))
    if changelog:
        print(f"{Colors.BLUE}{t('changelog_label')}{Colors.ENDC}")
        print(f"{Colors.BLUE}{changelog}{Colors.ENDC}")
    print(f"\n{Colors.GREEN}1 — {t('update_option')}{Colors.ENDC}")
    print(f"{Colors.GREEN}2 — {t('ignore_option')}{Colors.ENDC}")
    while True:
        try:
            choice = input(f"\n{Colors.CYAN}{t('enter_choice')}{Colors.ENDC}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            raise
        if choice in ('1', 'u', 'update', 'да', 'yes'):
            return apply_update_and_handle(config, info, t)
        elif choice in ('2', 'i', 'ignore', 'нет', 'no'):
            return False
        else:
            print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")


def apply_update_and_handle(config, info: dict, t) -> bool:
    system = platform.system()
    if system == 'Windows' and is_frozen():
        print(f"\n{Colors.CYAN}{t('update_downloading')}{Colors.ENDC}")
        if apply_update(config, info, t):
            return True
        print(f"{Colors.FAIL}{t('update_failed')}{Colors.ENDC}")
        return False
    apply_update(config, info, t)
    return False
