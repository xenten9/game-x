from pygame import font
font.init()

class ObjFont():
    def __init__(self):
        self.fonts = {'arial12': font.SysFont('arial', 12)}

    def add(self, name: str, size: int):
        """Adds a font to self."""
        try:
            self.fonts[name + str(size)]
        except KeyError:
            self.fonts[name + str(size)] = font.SysFont(name, size)
            return None
        return None

    def get(self, name: str, size: int):
        """Returns a font object."""
        try:
            self.fonts[name + str(size)]
        except KeyError:
            self.fonts[name + str(size)] = font.SysFont(name, size)
            return self.fonts[name + str(size)]
        else:
            return self.fonts[name + str(size)]

    def __del__(self):
        font.quit()
