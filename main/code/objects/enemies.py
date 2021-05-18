# Local imports
from ..engine.types.vector import vec2d
from ..engine.engine import Engine
from .game_objects import GameObject, Damageable

class Enemy(GameObject, Damageable):
    def __init__(self, engine: Engine, key: int, name: str, data: dict,
                 pos: vec2d, size: vec2d):
        super().__init__(engine, key, name, data, pos, size)
        self.hp: int = 1

    def update(self, pause: bool):
        if pause:
            pass
        else:
            if self.hp <= 0:
                self._die()

    def _die(self):
        self.engine.obj.delete(self.key)

class ObjWalkingEnemy(Enemy):
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        super().__init__(engine, key, name, data, pos, size)
        self.data = data

        # Sprite
        self.set_frames('walking-enemy.png')

        # Health
        self.hp = 6

    def update(self, pause: bool):
        super().update(pause)
