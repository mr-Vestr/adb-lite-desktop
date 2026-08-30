import os
import sys
import platform
import subprocess
from res.config import SHORTCUT_NAME


def _start_menu_programs_dirs():
    dirs = []
    appdata = os.environ.get('APPDATA', '')
    if appdata:
        dirs.append(os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs'))
    programdata = os.environ.get('ProgramData', '')
    if programdata:
        dirs.append(os.path.join(programdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs'))
    return dirs


def _current_launch():
    target = sys.executable or ''
    if getattr(sys, 'frozen', False):
        args = ''
        workdir = os.path.dirname(target)
    else:
        main_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'main.py'
        )
        args = f'"{main_script}"'
        workdir = os.path.dirname(main_script)
    return target, args, workdir


def _ps_quote(value):
    return str(value).replace("'", "''")


def _read_shortcut(lnk_path):
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{_ps_quote(lnk_path)}'); "
        "Write-Output $s.TargetPath; "
        "Write-Output $s.Arguments"
    )
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps],
            capture_output=True, text=True, timeout=10
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if lines:
            target = lines[0]
            args = lines[1] if len(lines) > 1 else ''
            return target, args
    except Exception:
        pass
    return None, None


def _icon_path():
    if not getattr(sys, 'frozen', False):
        return None
    meipass = getattr(sys, '_MEIPASS', '')
    candidates = []
    if meipass:
        candidates.append(os.path.join(meipass, 'res', 'icon.ico'))
    candidates.append(os.path.join(os.path.dirname(sys.executable), 'res', 'icon.ico'))
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _create_shortcut(lnk_path, target, args, workdir):
    icon_loc = _icon_path() or target
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{_ps_quote(lnk_path)}'); "
        f"$s.TargetPath = '{_ps_quote(target)}'; "
        f"$s.Arguments = '{_ps_quote(args)}'; "
        f"$s.WorkingDirectory = '{_ps_quote(workdir)}'; "
        f"$s.IconLocation = '{_ps_quote(icon_loc)},0'; "
        "$s.Save()"
    )
    try:
        subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps],
            capture_output=True, text=True, timeout=15
        )
        return os.path.exists(lnk_path)
    except Exception:
        return False


def ensure_start_menu_shortcut():
    if platform.system() != 'Windows':
        return None

    if not getattr(sys, 'frozen', False):
        return None

    dirs = _start_menu_programs_dirs()
    if not dirs:
        return None

    target, args, workdir = _current_launch()
    if not target:
        return None

    for folder in dirs:
        lnk = os.path.join(folder, SHORTCUT_NAME)
        if os.path.exists(lnk):
            cur_target, cur_args = _read_shortcut(lnk)
            if (cur_target or '').strip().lower() == target.strip().lower() and (cur_args or '').strip().lower() == args.strip().lower():
                return None

    try:
        os.makedirs(dirs[0], exist_ok=True)
    except Exception:
        return None

    lnk = os.path.join(dirs[0], SHORTCUT_NAME)
    existed = os.path.exists(lnk)
    if _create_shortcut(lnk, target, args, workdir):
        return 'updated' if existed else 'created'
    return None
