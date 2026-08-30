import json
import os
import sys
from src.other.utils import Colors


def _resolve_lang_dir(lang_dir: str = None):
    if lang_dir is not None:
        return lang_dir

    candidates = []
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'langs'))
    except Exception:
        pass

    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidates.append(os.path.join(meipass, 'langs'))
        candidates.append(os.path.join(meipass, 'ADB Lite Desktop', 'langs'))
        candidates.append(os.path.join(meipass, 'ADB Lite Desktop', 'ADB Lite Desktop', 'langs'))

    try:
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        candidates.append(os.path.join(exe_dir, 'langs'))
        candidates.append(os.path.join(exe_dir, 'ADB Lite Desktop', 'langs'))
        candidates.append(os.path.join(exe_dir, 'ADB Lite Desktop', 'ADB Lite Desktop', 'langs'))
        candidates.append(os.path.join(os.path.dirname(exe_dir), 'langs'))
    except Exception:
        pass
    
    try:
        cwd = os.getcwd()
        candidates.append(os.path.join(cwd, 'langs'))
        candidates.append(os.path.join(cwd, 'ADB Lite Desktop', 'langs'))
        candidates.append(os.path.join(cwd, 'ADB Lite Desktop', 'ADB Lite Desktop', 'langs'))
    except Exception:
        pass

    for d in candidates:
        if d and os.path.isdir(d):
            return d
        
    return candidates[0] if candidates else ''


def get_translator(lang: str, lang_dir: str = None):
    lang_dir = _resolve_lang_dir(lang_dir)
    search_dirs = [lang_dir]
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        search_dirs.append(os.path.join(meipass, 'langs'))
    try:
        search_dirs.append(os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'langs'))
    except Exception:
        pass

    translations = {}
    for d in search_dirs:
        for cand in (os.path.join(d, f'{lang}.json'), os.path.join(d, 'en.json')):
            if os.path.isfile(cand):
                try:
                    with open(cand, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                    if translations:
                        break
                except Exception:
                    continue
        if translations:
            break
    else:
        lang_file = os.path.join(lang_dir, f'{lang}.json')
        if not os.path.exists(lang_file):
            lang_file = os.path.join(lang_dir, 'en.json')
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        except Exception:
            translations = {}

    def translator(key: str, **kwargs) -> str:
        text = translations.get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    return translator


def select_language(config, translator) -> str:
    t = translator
    print(f"{Colors.CYAN}{Colors.BOLD}{t('select_language_title')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  1 — {t('option_english')}{Colors.ENDC}")
    print(f"{Colors.GREEN}  2 — {t('option_russian')}{Colors.ENDC}")

    while True:
        try:
            choice = input(f"\n{Colors.CYAN}{t('enter_choice')}{Colors.ENDC}").strip()
        except (EOFError, KeyboardInterrupt):
            raise
        if choice == '1':
            config.set('language', 'en')
            return 'en'
        elif choice == '2':
            config.set('language', 'ru')
            return 'ru'
        else:
            print(f"{Colors.FAIL}{t('invalid_selection')}{Colors.ENDC}")
