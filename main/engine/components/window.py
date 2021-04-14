from pygame import display, Surface, font, Rect, draw
font.init()

# Handles graphics
class ObjWindow():
    """Handles graphics."""
    def __init__(self, game, screen_size: tuple):
        self.game = game
        self.display = display.set_mode(screen_size)
        self.size = screen_size

    def render(self, camera):
        """Called when self.surface needs to be rendered to the screen."""
        surface = camera.surface
        self.display.blit(surface, (0, 0))
        display.update()

    def blank(self):
        """Blanks the screen in-between frames."""
        self.display.fill((255, 255, 255))
