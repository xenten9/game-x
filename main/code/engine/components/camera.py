"""Camera objects for containing information for the screen."""

from pygame import Surface

from ..types.vector import vec2d
from ..types import Component


class Camera(Component):
    """Camera object for defining viewframe."""

    def __init__(self, engine, size: vec2d):
        super().__init__(engine)
        self.size = size
        self.level_size = size
        self._pos = vec2d(0, 0)
        self._surface = Surface(size.ftup())

    @property
    def pos(self) -> vec2d:
        return self._pos

    @pos.setter
    def pos(self, pos: vec2d):
        self._pos = pos

    @property
    def surface(self):
        return self._surface

    def draw_surface(
        self, pos: vec2d, surface: Surface, gui: bool = False, special_flags=0
    ):
        """Draws a surface at a position."""
        if gui:
            self._surface.blit(
                surface, pos.ftup(), special_flags=special_flags
            )
        else:
            self._surface.blit(
                surface, (pos - self.pos).ftup(), special_flags=special_flags
            )

    def blank(self):
        """Blanks the screen"""
        self._surface.fill((255, 255, 255))
