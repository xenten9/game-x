from pygame import Surface, Rect, draw

# Camera object
class ObjCamera():
    """Camera object for defining viewframe."""
    def __init__(self, size):
        self._size = size
        self._pos = (0, 0)
        self._surface = Surface(size)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def rect(self):
        return Rect(self._pos, self._size)

    @property
    def surface(self):
        return self._surface

    def draw_text(self, pos: tuple, text: str, font, color=(0, 0, 0)):
        """Draws text at a position in a given font and color."""
        self._surface.blit(font.render(text, 0, color), pos)

    def draw_rect(self, pos: tuple, size: tuple, color=(0, 0, 0)):
        """Draws a rectangle at a position in a given color."""
        draw.rect(self._surface, color, Rect(pos, size))

    def draw_image(self, pos: tuple, image):
        """Draws an image at a position."""
        self._surface.blit(image, pos)

    def blank(self):
        """Blanks the screen"""
        self._surface.fill((255, 255, 255))
