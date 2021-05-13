"""All constants."""
# Standard Library
from os import getpid
from psutil import Process

# Local imports
from .engine.types.vector import vec2d

# Constants
FULLTILE = 32
FPS = 60
SIZE = vec2d(1024, 768)
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
