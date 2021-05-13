"""Collision detection handlers."""
# External libraries
from pygame import Rect, Surface, draw as pydraw

# Local imports
from ..types.vector import vec2d
from ..types.component import Component
from ..types.array import array2d

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
        self.array = array2d((16, 16))
        self.visible = True

    def add(self, pos: vec2d):
        """Add a wall at a given position."""
        pos //= self.fulltile
        x, y = pos
        self.array.set(x, y, True)

    def remove(self, pos: vec2d):
        """Remove a wall at a given position."""
        pos //= self.fulltile
        x, y = pos
        self.array.delete(x, y)

    def get(self, pos: vec2d) -> bool:
        """Check for a collision at a given position."""
        pos //= self.fulltile
        x, y = pos.ftup()
        try:
            if self.array.get(x, y):
                return True
            else:
                return False
        except IndexError:
            #print('outside of static collider')
            return False

    def clear(self):
        """Clear all Static collision points off of grid"""
        self.array = array2d((16, 16))

    def toggle_visibility(self):
        self.visible = not self.visible

    def debug_draw(self, draw: object):
        size = (vec2d(*self.array.size) * self.fulltile).ftup()
        surface = Surface(size).convert_alpha()
        surface.fill((0, 0, 0, 0))
        color = (16, 16, 16)
        size = (vec2d(1, 1) * self.fulltile).ftup()
        if self.visible:
            for x in range(self.array.width):
                for y in range(self.array.height):
                    if self.array.get(x, y):
                        pos = vec2d(x, y) * self.fulltile
                        rect = Rect(pos, size)
                        pydraw.rect(surface, color, rect)
            pos = vec2d(0, 0)
            self.engine.draw.add(0, pos=pos, surface=surface)

    def minimize(self):
        self.array.minimize()

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
