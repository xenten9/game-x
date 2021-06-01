# import main.code.engine.engine as engine


class Component:
    """Base class for all engine components."""

    def __init__(self, engine):
        from main.code.engine.engine import Engine

        self.engine: Engine = engine
        self.fulltile: int = self.engine.FULLTILE
        self.paths: dict[str, str] = self.engine.paths
