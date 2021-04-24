"""Camera objects for getting images."""
from pygame import Surface, Rect, draw
from .vector import vec2d

# Camera object
class ObjCamera():
    """Camera object for defining viewframe."""
    def __init__(self, size):
        self.size = size
        self._pos = (0, 0)
        self._surface = Surface(size)

    @property
    def surface(self):
        return self._surface

    def draw_text(self, pos: vec2d, text: str, font, color=(0, 0, 0), gui=0):
        """Draws text at a position in a given font and color."""
        if gui:
            self._surface.blit(font.render(text, 0, color), pos)
        else:
            self._surface.blit(font.render(text, 0, color), pos - self.pos)

    def draw_rect(self, pos: vec2d, size: vec2d, color=(0, 0, 0), gui=0):
        """Draws a rectangle at a position in a given color."""
        if gui:
            draw.rect(self._surface, color, Rect(pos, size))
        else:
            draw.rect(self._surface, color, Rect(self.pos-pos, size))

    def draw_image(self, pos: vec2d, image: Surface,
                   gui: bool = False, special_flags=0):
        """Draws an image at a position."""
        if gui:
            self._surface.blit(image, pos, special_flags=special_flags)
        else:
            self._surface.blit(image, pos - self.pos,
                               special_flags=special_flags)

    def blank(self):
        """Blanks the screen"""
        self._surface.fill((255, 255, 255))
