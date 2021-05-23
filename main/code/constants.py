"""All constants."""
# Standard Library
from os import getpid
from psutil import Process

# Local imports
from .engine.types.vector import vec2d

# Constants
PROCESS = Process(getpid())
SIZE = vec2d(1024, 768)
FULLTILE = 32
FPS = 60
