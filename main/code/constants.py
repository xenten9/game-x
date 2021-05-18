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
TGREEN = '\033[92m' #GREEN
TYELLOW = '\033[93m' #YELLOW
TRED = '\033[91m' #RED
TWHITE = '\033[0m' #RESET COLOR

# Static methods
def colorize(text: str, color: str) -> str:
    if color == 'green':
        return TGREEN + text + TWHITE
    elif color == 'red':
        return TRED + text + TWHITE
    elif color == 'yellow':
        return TYELLOW + text + TWHITE
    else:
        return color + text + TWHITE

def cprint(text: str, color: str):
    print(colorize(text, color))

# Clear the terminal
def clear_terminal():
    if osname == 'nt':
        print('\n'*4)
        system('cls')
    else:
        print('\n'*4)
        system('clear')
