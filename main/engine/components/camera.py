"""Camera objects for getting images."""
from pygame import Surface, Rect, draw
from .vector import vec2d

# Camera object
class ObjCamera():
    """Camera object for defining viewframe."""
    def __init__(self, size: vec2d):
        self.size = size
        self._pos = vec2d(0, 0)
        self._surface = Surface(size)

    @property
    def surface(self):
        return self._surface

    def draw_surface(self, pos: vec2d, surface: Surface,
                   gui: bool = False, special_flags=0):
        """Draws a surface at a position."""
        if gui:
            self._surface.blit(surface, pos,
                               special_flags=special_flags)
        else:
            self._surface.blit(surface, pos - self.pos,
                               special_flags=special_flags)

    def blank(self):
        """Blanks the screen"""
        self._surface.fill((255, 255, 255))
