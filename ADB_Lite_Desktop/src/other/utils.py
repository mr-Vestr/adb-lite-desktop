import platform, os
from res.config import VERSION


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'


ASCII_LOGO = f"""
{Colors.CYAN}{Colors.BOLD}
    █████╗ ██████╗ ██████╗     ██╗     ██╗████████╗███████╗
   ██╔══██╗██╔══██╗██╔══██╗    ██║     ██║╚══██╔══╝██╔════╝
   ███████║██║  ██║██████╔╝    ██║     ██║   ██║   █████╗  
   ██╔══██║██║  ██║██╔══██╗    ██║     ██║   ██║   ██╔══╝  
   ██║  ██║██████╔╝██████╔╝    ███████╗██║   ██║   ███████╗
   ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚══════╝╚═╝   ╚═╝   ╚══════╝
{Colors.ENDC}
{Colors.GREEN}                 Remote Plugin Installer v{VERSION}{Colors.ENDC}
{Colors.BLUE}                      by @mr_Vestr{Colors.ENDC}
"""


def set_console_title(title: str):
    if platform.system() == 'Windows':
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            pass


def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
