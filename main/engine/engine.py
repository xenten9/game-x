##############################################################################
"""engine.py
    engine.py is a game engine which uses pygame as a base.
"""
# Pylint not being cool
# pylint: disable=no-name-in-module
# pylint: disable=invalid-name
# pylint: disable=unused-import
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes


# Imports
import os
import ast

import pygame
from pygame.locals import (QUIT, KEYUP, KEYDOWN, MOUSEBUTTONDOWN,
                           MOUSEBUTTONUP, MOUSEMOTION)

from .helper_functions.tuple_functions import f_tupmult, f_tupadd
from .helper_functions.file_system import ObjFile

from .components.level import ObjLevel
from .components.inputs import ObjInput
from .components.window import ObjWindow
from .components.colliders import ObjCollider
from .components.object_handler import ObjObjectHandler
from .components.tile import ObjTileMap
from .components.font import ObjFont

# Methods
# Flip color
def f_cinverse(rgb=(0, 0, 0)) -> tuple:
    """Converts 16 bit tuple to its 16 bit inverse(RGB)."""
    return f_tupmult(f_tupadd((-255, -255, -255), rgb), -1)

# Creates a grid
def f_make_grid(size, default_value):
    """Makes a grid populated with some default value."""
    grid = []
    for _ in range(size[0]):
        grid.append([default_value] * size[1])
    return grid

# Returns a grid with a new size preserving as many old values as possible
def f_change_grid_dimensions(grid, size, value):
    """Updates an existing grid to be a new size."""
    dy = size[1] - len(grid[0])
    dx = size[0] - len(grid)

    # Add to existing columns
    if dy > 0:
        for x in range(len(grid)):
            for _ in range(dy):
                grid[x].append(value)
    elif dy < 0:
        for x in range(len(grid)):
            grid[x] = grid[x][0:len(grid)+dy]

    # Add new columns
    if dx > 0:
        for _ in range(dx):
            grid.append([value]*size[1])
    else:
        for x in range(size[0]):
            grid = grid[0:size[0]]
    return grid

# Return a value following packman logic
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
class GameHandler():
    """Game handler."""
    def __init__(self, screen_size: tuple, full_tile: int,
                 path: list, object_creator):
        # File paths
        self.PATH = path

        # Constants
        self.FULLTILE = full_tile
        self.HALFTILE = int(full_tile/2)

        # Constant Objects
        self.window = ObjWindow(self, screen_size)
        self.obj = ObjObjectHandler(self, object_creator)
        self.collider = ObjCollider(self)
        self.level = ObjLevel(self, self.PATH['LEVELS'])
        self.tile = ObjTileMap(self, self.PATH['TILEMAPS'])
        self.input = ObjInput()
        self.font = ObjFont()

        # Game loop
        self.run = 1

    def clear(self):
        """Clears out all objects and colliders."""
        self.obj.clear()
        self.collider.st.clear()
        self.collider.dy.clear()

    def end(self):
        """Ends the game."""
        self.clear()
        self.run = 0
        pygame.quit()
