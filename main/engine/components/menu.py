from pygame import Surface, draw, Rect

class ObjMenu():
    def __init__(self, game, size, pos=(0, 0)):
        self.game = game
        self.size = size
        self.pos = pos
        self.elements = {}
        self.surface = Surface(self.size).convert_alpha()

    def add(self, element):
        self.elements[element.name] = element

    def remove(self, name):
        del self.elements[name]

    def get(self, name: str):
        for i in self.elements:
            if self.elements[i].name == name:
                return self.elements[i]

    def blank(self):
        self.surface.fill((0, 0, 0, 0))

    def draw(self):
        for i in self.elements:
            self.elements[i].draw()

    def render(self, window):
        window.draw_image(self.pos, self.surface, gui=1)

class ObjTextElement():
    def __init__(self, menu, name: str, size: tuple, pos=(0, 0), **kwargs):
        self.menu = menu
        self.name = name
        self.size = size
        self.pos = pos
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

    def draw(self):
        font = self.menu.game.font.get(self.font, self.size[1])
        render = font.render(self.text, 0, self.color)
        if self.backdrop:
            surf = Surface(render.get_size())
            surf.blit(render, (0, 0))
            self.menu.surface.blit(surf, self.pos)
        else:
            self.menu.surface.blit(render, self.pos)

    def __del__(self):
        self.menu.remove(self.name)

class ObjRectElement():
    def __init__(self, menu, name: str, size: tuple, pos=(0, 0), **kwargs):
        self.menu = menu
        self.name = name
        self.size = size
        self.pos = pos
        if True:
            try:
                self.color = kwargs['color']
            except KeyError:
                self.color = (255, 255, 255)
        menu.add(self)

    def draw(self):
        draw.rect(self.menu.surface, self.color, Rect(self.pos, self.size))

    def __del__(self):
        self.menu.remove(self.name)
