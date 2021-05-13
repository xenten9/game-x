"""Object for handling fonts."""
# External libraries
from pygame import font

# Local imports
from ..types.component import Component

# Initializing fonts
font.init()

class Font(Component):
    def __init__(self, engine):
        super().__init__(engine)
        self.fonts = {'arial12': font.SysFont('arial', 12)}

    def add(self, name: str, size: int):
        """Adds a font to self."""
        try:
            return self.fonts[name + str(size)]
        except KeyError:
            self.fonts[name + str(size)] = font.SysFont(name, size)
            return self.fonts[name + str(size)]

    def get(self, name: str, size: int):
        """Returns a font object."""
        try:
            return self.fonts[name + str(size)]
        except KeyError:
            return self.add(name, size)

    def __del__(self):
        font.quit()
