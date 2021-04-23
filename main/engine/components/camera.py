"""Camera objects for getting images."""
from pygame import Surface, Rect, draw
from ..helper_functions.tuple_functions import f_tupadd, f_tupmult

def f_tupsub(tup0: tuple, tup1: tuple):
    tup0 = f_tupmult(tup0, -1)
    return f_tupadd(tup0, tup1)

# Camera object
class ObjCamera():
    """Camera object for defining viewframe."""
    def __init__(self, size):
        self._size = size
        self._pos = (0, 0)
        self._surface = Surface(size)

    @property
    def surface(self):
        return self._surface

    def draw_text(self, pos: tuple, text: str, font, color=(0, 0, 0), gui=0):
        """Draws text at a position in a given font and color."""
        if gui:
            self._surface.blit(font.render(text, 0, color), pos)
        else:
            self._surface.blit(font.render(text, 0, color), f_tupsub(self.pos, pos))

    def draw_rect(self, pos: tuple, size: tuple, color=(0, 0, 0), gui=0):
        """Draws a rectangle at a position in a given color."""
        if gui:
            draw.rect(self._surface, color, Rect(pos, size))
        else:
            draw.rect(self._surface, color, Rect(f_tupsub(self.pos, pos), size))

    def draw_image(self, pos: tuple, image, gui=0):
        """Draws an image at a position."""
        if gui:
            self._surface.blit(image, pos)
        else:
            self._surface.blit(image, f_tupsub(self.pos, pos))

    def blank(self):
        """Blanks the screen"""
        self._surface.fill((255, 255, 255))
