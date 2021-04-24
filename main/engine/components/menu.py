"""Menu's for all manner of occasions."""
from pygame import Surface, draw, Rect, surface

from .vector import vec2d

class ObjMenu():
    """Object used for menus."""
    def __init__(self, game: object, size: vec2d, pos: vec2d = vec2d(0, 0)):
        self.game = game
        self.size = size
        self.pos = pos
        self.elements = {}
        self.surface = Surface(self.size).convert_alpha()

    def add(self, element: object):
        """Add element to menu."""
        self.elements[element.name] = element

    def remove(self, name: str):
        """Remove element from menu."""
        del self.elements[name]

    def get(self, name: str):
        """Get element by name."""
        for i in self.elements:
            if self.elements[i].name == name:
                return self.elements[i]

    def blank(self):
        """Blank menu to be empty."""
        self.surface.fill((0, 0, 0, 0))

    def draw(self):
        """Draw all elements to menu."""
        self.blank()
        for i in self.elements:
            self.elements[i].draw()

    def render(self, window: object):
        """Render menu to window."""
        window.draw_image(self.pos, self.surface, gui=1)

class ObjTextElement():
    """Text menu element."""
    def __init__(self, menu, name: str, size: vec2d = vec2d(0, 0),
                 pos: vec2d = vec2d(0, 0), color: tuple = (255, 0, 255),
                 text: str = '', font: str = 'arial',
                 backdrop: bool = False):
        self.menu = menu
        self.name = name
        self.size = size
        self.pos = pos
        self.color = color
        self.text = text
        self.font = font
        self.backdrop = backdrop
        self.surface = Surface(size).convert_alpha()

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def cache(self):
        """Render text to surface."""
        font = self.menu.game.font.get(self.font, self.size[1])
        self.surface.fill((0, 0, 0, 0))
        render = font.render(self.text, 0, self.color)
        if self.backdrop:
            self.surface = Surface(render.get_size())
        self.surface.blit(render, (0, 0))

    def set_vars(self, size: tuple = None, pos: tuple = None,
                 color: tuple = None, text: str = None,
                 font: str = None, backdrop: bool = None) -> bool:
        res = 0
        if size not in (None, self.size):
            self.size = size
            res = 1
        if pos not in (None, self.pos):
            self.pos = pos
            res = 1
        if color not in (None, self.color):
            self.color = color
            res = 1
        if text not in (None, self.text):
            self.text = text
            res = 1
        if font not in (None, self.font):
            self.font = font
            res = 1
        if backdrop not in (None, self.backdrop):
            self.backdrop = backdrop
            res = 1
        if res == 1:
            self.cache()
            return True
        return False

    def draw(self):
        """Draw text to menu."""
        self.menu.surface.blit(self.surface, self.pos)

class ObjRectElement():
    """Rectangle menu element."""
    def __init__(self, menu, name: str, size: vec2d,
                 pos: vec2d = vec2d(0, 0), **kwargs):
        self.menu = menu
        self.name = name
        self.size = size
        self.pos = pos
        self.surface = surface(size)

        # Kwargs interpretation
        if True:
            try:
                self.color = kwargs['color']
            except KeyError:
                self.color = (255, 255, 255)

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def cache(self):
        """Render rect to surface."""
        draw.rect(self.surface, self.color, Rect(self.pos, self.size))

    def draw(self):
        """Draw rect to menu."""
        self.menu.blit(self.surface)

