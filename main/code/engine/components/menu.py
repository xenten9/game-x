"""Menu's for all manner of occasions."""
# Standard library
from __future__ import annotations
from typing import Callable, Tuple

# External libraries
from pygame import Surface, Rect

# Local imports
from ..types.vector import vec2d
from ..types.component import Component
from .draw import Draw

class Menu(Component):
    """Object used for menus."""
    def __init__(self, engine: object, size: vec2d, pos: vec2d = vec2d(0, 0)):
        super().__init__(engine)
        self.size = size
        self.pos = pos
        self.visible = True
        self.elements = {}
        self.surface = Surface(self.size.ftup()).convert_alpha()

    def add(self, element: MenuElement):
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
        return None

    def blank(self):
        """Blank menu to be empty."""
        self.surface.fill((0, 0, 0, 0))

    def draw(self, draw: Draw):
        """Draw all elements to menu."""
        self.blank()
        if self.visible:
            for i in self.elements:
                try:
                    self.elements[i].draw(draw)
                except AttributeError:
                    pass

class MenuElement():
    def __init__(self, engine, menu: Menu, name: str):
        self._engine = engine
        self._menu = menu
        self._name = name
        self._pos = vec2d(0, 0)
        self._depth = 8
        self._center = 7
        self._surface = Surface((0, 0))
        self._cache = True
        self.menu.add(self)

    @property
    def menu(self):
        return self._menu

    @property
    def name(self):
        return self._name

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, depth):
        self._depth = depth

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center: int):
        if 1 <= center <= 9:
            self._center = center
            self._cache = True

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos: vec2d):
        self._pos = pos

    def get_cpos(self, size: vec2d):
        if self.center == 1:
            return self.pos - vec2d(0, size.y)
        if self.center == 2:
            return self.pos - vec2d(size.x/2, size.y)
        if self.center == 3:
            return self.pos - size
        if self.center == 4:
            return self.pos - vec2d(0, size.y/2)
        if self.center == 5:
            return self.pos - size/2
        if self.center == 6:
            return self.pos - vec2d(size.x, size.y/2)
        if self.center == 7:
            return self.pos
        if self.center == 8:
            return self.pos - vec2d(size.x/2, 0)
        if self.center == 9:
            return self.pos - vec2d(size.x, 0)

class MenuElementVisible(MenuElement):
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)
        self._surface = Surface((0, 0))

    @property
    def surface(self):
        return self._surface

    @surface.setter
    def surface(self, surface: Surface):
        self._surface = surface

    def cache(self):
        self.surface = Surface((0, 0))

    def draw(self, draw: Draw):
        surface = self.surface
        pos = self.get_cpos(vec2d(*surface.get_size()))
        if self._cache:
            self.cache()
        draw.add(self.depth, pos=pos, surface=surface, gui=True)

class SubMenu(MenuElement, Menu):
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)

class MenuText(MenuElementVisible):
    """Text menu element."""
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)
        self._size = 12
        self._font = 'arial'
        self._text = name
        self._color = (255, 0, 255)
        self.menu.add(self)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: int):
        self._size = size
        self._cache = True

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font: str):
        self._font = font
        self._cache = True

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self._cache = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color: Tuple[int, int, int]):
        for value in color:
            if value < 0 or value > 255:
                code = ['Colors must be bounded by 0-255',
                        'Colors: {}'.format(color),
                        'Colors<type>: {}'.format(type(color))]
                raise ValueError('\n'.join(code))
        self._color = color
        self._cache = True

    def cache(self):
        """Render text to surface."""
        font = self._engine.font.get(self.font, self.size)
        render = font.render(self.text, 0, self.color)
        self.surface = render

class MenuRect(MenuElementVisible):
    """Rectangle menu element."""
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)
        self._size = vec2d(0, 0)
        self._color = (0, 0, 0)
        menu.add(self)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: vec2d):
        self._size = size.floor()
        self._cache = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        for value in color:
            if value < 0 or value > 255:
                code = ['Colors must be bounded by 0-255',
                        'Color: {}'.format(color),
                        'Color<type>: {}'.format(type(color))]
                raise ValueError('\n'.join(code))
        self._color = color
        self._cache = True

    def cache(self):
        """Render rect to surface."""
        self.surface = Surface(self.size.ftup())
        if len(self.color) == 4:
            self.surface = self.surface.convert_alpha() # type: ignore
        self.surface.fill(self.color)

class MenuButton(MenuElement):
    """Button menu element."""
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)
        self._size = vec2d(0, 0)
        self._mkey = 1
        self._call = None
        self._held = False
        self._focus = False
        menu.add(self)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: vec2d):
        self._size = size

    @property
    def mkey(self):
        return self._mkey

    @mkey.setter
    def mkey(self, mkey: int):
        if 1 <= mkey <= 3:
            self._mkey = mkey

    @property
    def call(self):
        return self._call

    @call.setter
    def call(self, call: Callable):
        self._call = call

    @property
    def held(self):
        return self._held

    @held.setter
    def held(self, held: bool):
        self._held = held

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, focus: bool):
        self._focus = focus

    def update(self):
        if self.menu.visible:
            pos = self._engine.inp.ms.get_button_pressed_pos(self.mkey)
            if pos is not None:
                if self.collide(pos):
                    if self.held:
                        self.focus = True
                    else:
                        self.call(self, pos - self.pos)
            if self.focus:
                if self._engine.inp.ms.get_button_held(self.mkey):
                    pos = self._engine.inp.ms.get_pos()
                    self.call(self, pos - self.pos)
                else:
                    self._focus = False

    def collide(self, pos) -> bool:
        pos -= self.get_cpos(self.size)
        if Rect((0, 0), self.size.tup()).collidepoint(pos):
            return True
        return False

class MenuButtonFull(SubMenu):
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)
        self.elements = {}
        self.text = MenuText(self._engine, self, name + '-text')
        self.rect = MenuRect(self._engine, self, name + '-rect')
        self.button = MenuButton(self._engine, self, name + '-button')
        self._size = vec2d(0, 0)

    @property
    def visible(self):
        return self.menu.visible

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos: vec2d):
        self._pos = pos
        self.text.pos = pos
        self.rect.pos = pos
        self.button.pos = pos

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center: int):
        if 1 <= center <= 9:
            self._center = center
            self.text.center = self.center
            self.rect.center = self.center
            self.button.center = self.center

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: vec2d):
        self._size = size.floor()
        self.text.size = self.size.y
        self.rect.size = self.size
        self.button.size = self.size

    def update(self):
        self.button.update()

    def draw(self, draw: Draw):
        self.text.draw(draw)
        self.rect.draw(draw)

class MenuSlider(SubMenu):
    def __init__(self, engine, menu: Menu, name: str):
        super().__init__(engine, menu, name)
        self.elements = {}
        self.rect_slide = MenuRect(self._engine, self, name + '-rect-slide')
        self.rect_slide.depth = 12
        self.rect_back = MenuRect(self._engine, self, name + '-rect-back')
        self.button = MenuButton(self._engine, self, name + '-button')
        self.button.held = True
        self._size = vec2d(0, 0)
        self._value = 1

    @property
    def visible(self):
        return self.menu.visible

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos: vec2d):
        self._pos = pos
        self.rect_slide.pos = pos
        self.rect_back.pos = pos
        self.button.pos = pos

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center: int):
        if 1 <= center <= 9:
            self._center = center
            self.rect_slide.center = self.center
            self.rect_back.center = self.center
            self.button.center = self.center

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: vec2d):
        self._size = size.floor()
        self.rect_slide.size = vec2d(self.value * self.size.x, self.size.y)
        self.rect_back.size = self.size
        self.button.size = self.size

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: float):
        self._value = value
        self.rect_slide.size = vec2d(self.value * self.size.x, self.size.y)

    def update(self):
        self.button.update()

    def draw(self, draw: Draw):
        self.rect_slide.draw(draw)
        self.rect_back.draw(draw)
