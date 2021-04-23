##############################################################################
"""A game engine, for all your game engine needs."""

import pygame
from typing import Callable

from .helper_functions.tuple_functions import f_tupmult, f_tupadd

from .components.level import ObjLevel
from .components.inputs import ObjInput
from .components.window import ObjWindow
from .components.colliders import ObjCollider
from .components.object_handler import ObjObjectHandler
from .components.tile import ObjTileMap
from .components.font import ObjFont
from .components.audio import ObjMixer
from .components.debug import ObjDebug

# Methods
# Flip color
def f_cinverse(rgb=(0, 0, 0)) -> tuple:
    """Converts 16 bit tuple to its 16 bit inverse(RGB)."""
    return f_tupmult(f_tupadd((-255, -255, -255), rgb), -1)

# Return a value following pacman logic
def f_loop(val, minval, maxval):
    """Returns a number that loops between the min and max
    Ex. n = 8, minval = 3, maxval = 5;
        8 is 3 more then 5
        minval + 3 = 6
        6 is 1 more then 5
        minval + 1 = 4
        minval < 4 < maxval
        return 4
    """
    if minval <= val <= maxval:
        return val
    if val <= minval:
        return maxval - (minval - val) + 1
    return minval + (val - maxval) - 1

# Return the value closest to the range min to max
def f_limit(val, minval, maxval):
    """Reutrns value n
    limits/clamps the value n between the min and max
    """
    if val < minval:
        return minval
    if val > maxval:
        return maxval
    return val


# Classes
# Game handling object
class ObjGameHandler():
    """Game handler."""
    def __init__(self, screen_size: tuple, full_tile: int,
                 path: list, object_creator: Callable, fps: int,
                 debug: bool = False):
        # File paths
        self.PATH = path

        # Constants
        self.FULLTILE = full_tile
        self.HALFTILE = int(full_tile/2)
        self.FPS = fps

        # Constant Objects
        self.window = ObjWindow(self, screen_size)
        self.obj = ObjObjectHandler(self, object_creator)
        self.collider = ObjCollider(self)
        self.level = ObjLevel(self)
        self.tile = ObjTileMap(self)
        self.input = ObjInput(self)
        self.font = ObjFont()
        self.audio = ObjMixer(self)
        self.debug = ObjDebug(self)
        self.debug.on = bool(debug)

        # Game loop
        self.run = 1

    def clear_cache(self):
        """Clears out all objects and colliders."""
        self.audio.sfx.clear()
        self.tile.clear()

    def clear_ent(self):
        """Clears out all objects and colliders."""
        self.obj.clear()
        self.collider.st.clear()
        self.collider.dy.clear()

    def end(self):
        """Ends the game."""
        self.clear_ent()
        self.clear_cache()
        self.run = 0
        pygame.quit()
