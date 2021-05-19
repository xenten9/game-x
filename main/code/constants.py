"""All constants."""
# Standard Library
from os import getpid, name as osname, system
from psutil import Process

# Local imports
try:
    from .engine.types.vector import vec2d
    SIZE = vec2d(1024, 768)
except ImportError:
    SIZe = None

# Constants
FULLTILE = 32
FPS = 60
PROCESS = Process(getpid())
TRED = '\033[91m'
TYELLOW = '\033[93m'
TGREEN = '\033[92m'
TBLUE = '\033[34m'
TMAGENTA = '\033[35m'
TCYAN = '\033[36m'
TWHITE = '\033[0m' #RESET COLOR

# Static methods
def colorize(text: str, color: str) -> str:
    if color == 'green':
        return TGREEN + text + TWHITE
    elif color == 'red':
        return TRED + text + TWHITE
    elif color == 'yellow':
        return TYELLOW + text + TWHITE
    elif color == 'blue':
        return TBLUE + text + TWHITE
    elif color == 'magenta':
        return TMAGENTA + text + TWHITE
    elif color == 'cyan':
        return TCYAN + text + TWHITE
    else:
        return color + text + TWHITE

def cprint(text: str, color: str):
    print(colorize(text, color))

# Clear the terminal
def clear_terminal():
    if osname == 'nt':
        system('cls')
    else:
        system('clear')
