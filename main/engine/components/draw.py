from ..types.component import Component
from .camera import Camera

class Draw(Component):
    def __init__(self, engine: object):
        super().__init__(engine)
        self.depths = {}

    def draw(self):
        """Tell each object to add to the draw roster."""
        obj = self.engine.obj.obj
        for key in obj:
            obj[key].draw(self)
        tile = self.engine.til.layers
        for layer in tile:
            tile[layer].draw(self)

    def add(self, depth: int, **kwargs):
        """Add an element to be drawn when called."""
        if not isinstance(depth, int):
            raise TypeError('depth must be int')
        try:
            self.depths[depth]
        except KeyError:
            self.depths[depth] = []
        self.depths[depth].append(kwargs)

    def render(self, window: Camera):
        depths = sorted(self.depths)
        for i in depths:
            depth = self.depths[i]
            for kwargs in depth:
                try:
                    gui = kwargs['gui']
                except KeyError:
                    gui = False
                try:
                    special = kwargs['special']
                except KeyError:
                    special = 0

                pos = kwargs['pos']
                surface = kwargs['surface']
                window.draw_surface(pos, surface, gui, special)
        self.depths = {}
