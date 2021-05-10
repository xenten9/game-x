from os import getpid
from psutil import Process
from ..engine.types.vector import vec2d

# Constants
FULLTILE = 32
FPS = 60
SIZE = vec2d(1024, 768)
PROCESS = Process(getpid())
