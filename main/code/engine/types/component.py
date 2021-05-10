class Component():
    """Base class for all engine components."""
    def __init__(self, engine):
        self.engine = engine
        self.fulltile = engine.FULLTILE
        self.paths = engine.paths
