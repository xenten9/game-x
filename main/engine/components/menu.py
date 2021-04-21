from pygame import Surface, draw, Rect

class ObjMenu():
    """Object used for menus."""
    def __init__(self, game: object, size: tuple, pos: tuple = (0, 0)):
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
        for i in self.elements:
            self.elements[i].draw()

    def render(self, window: object):
        """Render menu to window."""
        window.draw_image(self.pos, self.surface, gui=1)

class ObjTextElement():
    """Text menu element."""
    def __init__(self, menu, name: str, size: tuple, pos=(0, 0), **kwargs):
        self.menu = menu
        self.name = name
        self.size = size
        self.pos = pos

        # Kwargs interpretation
        if True:
            try:
                self.color = kwargs['color']
            except KeyError:
                self.color = (255, 0, 255)
            try:
                self.text = kwargs['text']
            except KeyError:
                self.text = ''
            try:
                self.font = kwargs['font']
            except KeyError:
                self.font = 'arial'
            try:
                self.backdrop = kwargs['backdrop']
            except KeyError:
                self.backdrop = 0

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def draw(self):
        """Draw text to menu."""
        font = self.menu.game.font.get(self.font, self.size[1])
        render = font.render(self.text, 0, self.color)
        if self.backdrop:
            surf = Surface(render.get_size())
            surf.blit(render, (0, 0))
            self.menu.surface.blit(surf, self.pos)
        else:
            self.menu.surface.blit(render, self.pos)

class ObjRectElement():
    """Rectangle menu element."""
    def __init__(self, menu, name: str, size: tuple, pos=(0, 0), **kwargs):
        self.menu = menu
        self.name = name
        self.size = size
        self.pos = pos

        # Kwargs interpretation
        if True:
            try:
                self.color = kwargs['color']
            except KeyError:
                self.color = (255, 255, 255)

        menu.add(self)

    def __del__(self):
        self.menu.remove(self.name)

    def draw(self):
        """Draw rect to menu."""
        draw.rect(self.menu.surface, self.color, Rect(self.pos, self.size))
