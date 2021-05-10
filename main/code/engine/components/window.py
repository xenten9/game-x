"""Object for rendering to the screen."""
from pygame import display
from ..types.component import Component
from ..types.vector import vec2d
from .camera import Camera

# Handles graphics
class Window(Component):
    """Handles graphics."""
    def __init__(self, engine, size: vec2d):
        super().__init__(engine)
        size = size.floor()
        self.display = display.set_mode(size)
        self.size = size

    def render(self, camera: Camera):
        """Renders camera surface to screen."""
        surface = camera.surface
        self.display.blit(surface, (0, 0))

    def update(self):
        """Update screen."""
        display.update()

    def blank(self):
        """Blanks the screen in-between frames."""
        self.display.fill((255, 255, 255))
