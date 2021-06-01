from ..components.draw import Draw


class Entity:
    """Base class for all game entities."""

    def __init__(self, engine, key: int, name: str, data: dict):
        self.engine = engine
        self.key = key
        self.name = name
        self.data = data

    def post_init(self):
        pass

    def update_early(self, paused: bool):
        """Update called first."""
        pass

    def update(self, paused: bool):
        """Update called second."""
        pass

    def update_late(self, paused: bool):
        """Update called last."""
        pass

    def draw(self, draw: Draw):
        """Draw called in between back and foreground."""
        pass
