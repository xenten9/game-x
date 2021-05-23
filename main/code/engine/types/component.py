class Component():
    """Base class for all engine components."""
    def __init__(self, engine):
        self.engine = engine
        self.fulltile: int = engine.FULLTILE
        self.paths: dict[str, str] = engine.paths
