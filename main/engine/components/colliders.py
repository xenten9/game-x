"""Objects for handling collision detection."""
from pygame import Rect, Surface, draw
from ..helper_functions.number_functions import (
    f_make_grid, f_change_grid_dimensions, f_minimize_grid)

from .vector import vec2d

class ObjCollider():
    def __init__(self, game):
        self.game = game
        self.dy = ObjDynamicCollider()
        self.st = ObjStaticCollider(game.FULLTILE)

# Handles static collision
class ObjStaticCollider():
    """Handles static collisions aligned to a grid."""
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.size = vec2d(16, 16)
        self.grid = f_make_grid(self.size, 0)
        self.visible = True

    def add(self, pos: vec2d):
        """Add a wall at a given position."""
        pos //= self.tile_size
        try:
            self.grid[pos.x][pos.y] = 1
        except IndexError:
            if len(self.grid) == 0:
                size = pos + vec2d(1, 1)
            else:
                size = vec2d(max(pos[0] + 1, len(self.grid)),
                             max(pos[1] + 1, len(self.grid[0])))
            self.expand(size)
            self.grid[pos.x][pos.y] = 1

    def remove(self, pos: vec2d):
        """Remove a wall at a given position."""
        pos //= self.tile_size
        try:
            self.grid[pos.x][pos.y] = 0
        except IndexError:
            pass

    def get(self, pos):
        """Check for a collision at a given position."""
        pos //= self.tile_size
        pos = pos.floor()
        try:
            return self.grid[pos.x][pos.y]
        except IndexError:
            print('outside of static collider')
            return 0

    def expand(self, size):
        """Expand grid to accomodate new colliders."""
        self.size = size
        self.grid = f_change_grid_dimensions(self.grid, size, 0)

    def clear(self):
        """Clear all Static collision points off of grid"""
        self.grid = f_make_grid((16, 16), 0)

    def toggle_visibility(self):
        self.visible = not self.visible

    def debug_draw(self, window: object):
        size = vec2d(1, 1) * self.tile_size
        surface = Surface(self.size * self.tile_size).convert_alpha()
        surface.fill((0, 0, 0, 0))
        if self.visible:
            for row, slice in enumerate(self.grid):
                for column, cell in enumerate(slice):
                    if cell:
                        pos = vec2d(row, column) * self.tile_size
                        draw.rect(surface, (0, 0, 0), Rect(pos, size))
            window.add(0, pos=vec2d(0, 0), surface=surface)

    def minimize(self):
        self.grid = f_minimize_grid(self.grid, 0)

# Handles Dynamic collisions
class ObjDynamicCollider():
    """Handles collisions with moving objects."""
    def __init__(self):
        self.colliders = {}

    def add(self, key, obj):
        """Adds a collider to self.colliders."""
        self.colliders[key] = obj

    def remove(self, key):
        """Removes a collider to self.colliders."""
        try:
            del self.colliders[key]
        except KeyError:
            pass

    def get_collision(self, pos, size, origin, key=-1) -> list:
        """Checks each collider to see if they overlap a rectangle."""
        collide = []
        rect0 = Rect(pos + origin, size)
        for col in self.colliders:
            if col != key:
                cobj = self.colliders[col]
                rect1 = Rect(cobj.pos + cobj.origin, cobj.size)
                if rect0.colliderect(rect1):
                    collide.append(cobj)
        return collide

    def clear(self):
        """Remove all colliders."""
        self.colliders = {}
