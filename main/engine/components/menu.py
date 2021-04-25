"""Menu's for all manner of occasions."""
from typing import Callable
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
            try:
                self.elements[i].draw()
            except AttributeError:
                pass

class ObjTextElement():
    """Text menu element."""
    def __init__(self, menu, name: str):
        self.menu = menu
        self.name = name
        self.size = 12
        self.pos = vec2d(0, 0)
        self.color = (255, 0, 255)
        self.text = ''
        self.font = 'arial'
        self.backdrop = False
        self.center = False
        self.depth = 16
        self.surface = Surface(vec2d(12, 12)).convert_alpha()

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def set_vars(self, size: tuple = None, pos: tuple = None,
                 color: tuple = None, text: str = None, font: str = None,
                 backdrop: bool = None, center: bool = None,
                 depth: int = None):
        res = False
        if size not in (None, self.size):
            self.size = size
            res = True
        if pos not in (None, self.pos):
            self.pos = pos
            res = True
        if color not in (None, self.color):
            self.color = color
            res = True
        if text not in (None, self.text):
            self.text = text
            res = True
        if font not in (None, self.font):
            self.font = font
            res = True
        if backdrop not in (None, self.backdrop):
            self.backdrop = backdrop
            res = True
        if center not in (None, self.center):
            self.center = center
            res = True
        if depth not in (None, self.depth):
            self.depth = depth
            res = True
        if res:
            self.cache()

    def cache(self):
        """Render text to surface."""
        font = self.menu.game.font.get(self.font, self.size)
        render = font.render(self.text, 0, self.color)
        self.surface = Surface(render.get_size())
        if not self.backdrop:
            self.surface.set_colorkey((0, 0, 0))
        self.surface.blit(render, vec2d(0, 0))

    def draw(self):
        """Draw text to menu."""
        if not self.center:
            pos = self.pos
        else:
            pos = self.pos - (vec2d(*self.surface.get_size()) / 2)
        surface = self.surface
        self.menu.game.draw.add(self.depth, pos=pos, surface=surface, gui=1)

class ObjRectElement():
    """Rectangle menu element."""
    def __init__(self, menu, name: str):
        self.menu = menu
        self.name = name
        self.size = vec2d(0, 0)
        self.pos = vec2d(0, 0)
        self.color = (255, 0, 255)
        self.depth = 16
        self.surface = Surface(vec2d(12, 12)).convert_alpha()

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def set_vars(self, size: tuple = None, pos: tuple = None,
                 color: tuple = None, depth: int = None):
        res = False
        if size not in (None, self.size):
            self.size = size
            res = True
        if pos not in (None, self.pos):
            self.pos = pos
            res = True
        if color not in (None, self.color):
            self.color = color
            res = True
        if depth not in (None, self.depth):
            self.depth = depth
            res = True
        if res:
            self.cache()

    def cache(self):
        """Render rect to surface."""
        self.surface = Surface(self.size)
        draw.rect(self.surface, self.color, Rect(self.pos, self.size))

    def draw(self):
        """Draw rect to menu."""
        surface = self.surface
        pos = self.pos
        self.menu.game.draw.add(self.depth, pos=pos, surface=surface, gui=1)

class ObjButtonElement():
    """Button menu element."""
    def __init__(self, menu, name: str):
        self.menu = menu
        self.name = name
        self.size = vec2d(0, 0)
        self.pos = vec2d(0, 0)
        self.mkey = 1
        self.call = None
        self.center = 0
        self.surface = Surface(vec2d(12, 12)).convert_alpha()

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def update(self):
        pos = self.menu.game.input.ms.get_button_pressed_pos(self.mkey)
        if pos != None:
            if Rect(self.pos - self.size / 2, self.size).collidepoint(pos):
                self.call(self.name)

    def set_vars(self, size: tuple = None, pos: tuple = None,
                 mkey: int = None, call: Callable = None,
                 center: bool = False):
        if size not in (None, self.size):
            self.size = size
        if pos not in (None, self.pos):
            self.pos = pos
        if mkey not in (None, self.mkey):
            self.mkey = mkey
        if call not in (None, self.call):
            self.call = call
        if center not in (None, self.center):
            self.center = center
