"""Objects for handling collision detection."""
from pygame import Rect, Surface, draw as pydraw

from ..types.vector import vec2d
from ..types.component import Component
from .grid import f_make_grid, f_change_grid_dimensions, f_minimize_grid

class Collider(Component):
    def __init__(self, engine: object):
        super().__init__(engine)
        self.dy = DynamicCollider(engine)
        self.st = StaticCollider(engine)

# Handles static collision
class StaticCollider(Component):
    """Handles static collisions aligned to a grid."""
    def __init__(self, engine: object):
        super().__init__(engine)
        self.size = vec2d(16, 16)
        self.grid = f_make_grid(self.size, 0)
        self.visible = True

    def add(self, pos: vec2d):
        """Add a wall at a given position."""
        pos //= self.fulltile
        try:
            self.grid[int(pos.x)][int(pos.y)] = 1
        except IndexError:
            if len(self.grid) == 0:
                size = pos + vec2d(1, 1)
            else:
                size = vec2d(max(pos[0] + 1, len(self.grid)),
                             max(pos[1] + 1, len(self.grid[0])))
            self.expand(size)
            self.grid[int(pos.x)][int(pos.y)] = 1

    def remove(self, pos: vec2d):
        """Remove a wall at a given position."""
        pos //= self.fulltile
        try:
            self.grid[int(pos.x)][int(pos.y)] = 0
        except IndexError:
            pass

    def get(self, pos):
        """Check for a collision at a given position."""
        pos //= self.fulltile
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

    def debug_draw(self, draw: object):
        size = vec2d(1, 1) * self.fulltile
        surface = Surface((size * self.fulltile).ftup()).convert_alpha()
        surface.fill((0, 0, 0, 0))
        color = (16, 16, 16)
        size = size.ftup()
        if self.visible:
            for row, slice in enumerate(self.grid):
                for column, cell in enumerate(slice):
                    if cell:
                        pos = vec2d(row, column) * self.fulltile
                        rect = Rect(pos.ftup(), size)
                        pydraw.rect(surface, color, rect)
            pos = vec2d(0, 0)
            self.engine.draw.add(0, pos=pos, surface=surface)

    def minimize(self):
        self.grid = f_minimize_grid(self.grid, 0)

# Handles Dynamic collisions
class DynamicCollider(Component):
    """Handles collisions with moving objects."""
    def __init__(self, engine: object):
        super().__init__(engine)
        self.colliders = {}

    def add(self, key: int, obj: object):
        """Adds a collider to self.colliders."""
        self.colliders[key] = obj

    def remove(self, key: int):
        """Removes a collider to self.colliders."""
        try:
            del self.colliders[key]
        except KeyError:
            pass

    def get_collision(self, pos: vec2d, size: vec2d, origin: vec2d, key: int = -1) -> list:
        """Checks each collider to see if they overlap a rectangle."""
        collide = []
        pos = pos + origin
        new_pos = pos.tup()
        new_size = size.tup()
        rect0 = Rect(new_pos, new_size)
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
