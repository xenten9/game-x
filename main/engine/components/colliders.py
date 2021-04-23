"""Objects for handling collision detection."""
from ..helper_functions.tuple_functions import f_tupround, f_tupmult, f_tupadd
from ..helper_functions.number_functions import (
    f_make_grid, f_change_grid_dimensions, f_minimize_grid)
from ..helper_functions.collisions import f_col_rects

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
        self.size = (16, 16)
        self.grid = f_make_grid(self.size, 0)
        self.visible = True

    def add(self, pos: tuple):
        """Add a wall at a given position."""
        pos = f_tupround(f_tupmult(pos, 1/self.tile_size), 0)
        try:
            self.grid[pos[0]][pos[1]] = 1
        except IndexError:
            if len(self.grid) == 0:
                size = (f_tupadd(pos, (1, 1)))
            else:
                size = (max(pos[0] + 1, len(self.grid)),
                        max(pos[1] + 1, len(self.grid[0])))
            self.expand(size)
            self.grid[pos[0]][pos[1]] = 1

    def remove(self, pos: tuple):
        """Remove a wall at a given position."""
        pos = f_tupround(f_tupmult(pos, 1/self.tile_size), -1)
        try:
            self.grid[pos[0]][pos[1]] = 0
        except IndexError:
            pass

    def get(self, pos):
        """Check for a collision at a given position."""
        pos = f_tupround(f_tupmult(pos, 1/self.tile_size), -1)
        try:
            return self.grid[pos[0]][pos[1]]
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

    def debug_draw(self, window):
        if self.visible:
            for row, _ in enumerate(self.grid):
                for column, cell in enumerate(self.grid[row]):
                    if cell:
                        pos = f_tupmult((row, column), self.tile_size)
                        tile = (self.tile_size, self.tile_size)
                        window.draw_rect(pos, tile)

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

    def get_collision(self, pos, rect, key=-1) -> list:
        """Checks each collider to see if they overlap a rectangle."""
        collide = []
        dom = f_tupadd(rect[0], pos[0])
        ran = f_tupadd(rect[1], pos[1])
        for col in self.colliders:
            if col != key:
                cobj = self.colliders[col]
                crect = cobj.crect
                cpos = cobj.pos
                cdom = f_tupadd(crect[0], cpos[0])
                cran = f_tupadd(crect[1], cpos[1])
                if f_col_rects(dom, ran, cdom, cran):
                    collide.append(cobj)
        return collide

    def clear(self):
        """Remove all colliders."""
        self.colliders = {}
