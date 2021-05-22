"""Handles drawing objects to a camera."""
# Local imports
from ..types.component import Component
from .camera import Camera

class Draw(Component):
    def __init__(self, engine: object):
        super().__init__(engine)
        self.depths = {}

    def draw(self):
        """Tell each object to add to the draw roster."""
        # Normal objects
        obj = self.engine.obj.obj
        for key in obj:
            obj[key].draw(self)

        # Static objects
        sobj = self.engine.obj.sobj
        for key in sobj:
            sobj[key].draw(self)

        # Tile layers
        layers = self.engine.tile.layers
        for layer in layers:
            layers[layer].draw(self)


    def add(self, depth: int, **kwargs):
        """Add an element to be drawn when called."""
        if not isinstance(depth, int):
            code = ['Depth must be int',
                    'Depth: {}'.format(depth),
                    'Depth<type>:'.format(type(depth))]
            raise TypeError('\n'.join(code))
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
