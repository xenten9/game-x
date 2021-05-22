# Standard library
from math import floor

# Local imports
from ..engine.types.vector import vec2d
from ..engine.engine import Engine
from .game_objects import GameObject, Damageable, ObjPlayer

class Enemy(GameObject, Damageable):
    def __init__(self, engine: Engine, key: int, name: str, data: dict,
                 pos: vec2d, size: vec2d = vec2d(32, 32),
                 origin: vec2d = vec2d(0, 0)):
        super().__init__(engine, key, name, data, pos, size, origin)
        self.hp: int = 1
        self.damage = 1

    def update(self, paused: bool):
        if paused:
            pass
        else:
            if self.hp <= 0:
                self._die()

    def _die(self):
        self.engine.obj.delete(self.key)

class ObjWalkingEnemy(Enemy):
    def __init__(self, engine: Engine, key: int,
                 name: str, data: dict, pos: vec2d):
        super().__init__(engine, key, name, data, pos, vec2d(32, 32))
        self.data = data
        self.speed = vec2d(2, 0)
        self.dir: bool = False
        self.engine.col.dy.add(self.key, self)

        # Sprite
        self.set_frames('walking-enemy.png')

        # Health
        self.hp = 6
        self.damage = 1

        # Add sound
        self.engine.aud.sfx.add('beep.ogg')

        # Check for ground
        if not self.scollide(pos + vec2d(0, 1)):
            raise RuntimeError('Enemy not on ground')

    def update(self, paused: bool):
        super().update(paused)
        if paused:
            pass
        else:
            self._move()

    def collide(self, obj):
        if issubclass(obj.__class__, Damageable):
            if isinstance(obj, ObjPlayer):
                if obj.vspd > 2.0:
                    self.hp -= obj.damage
                    obj.vspd = -obj.jump_speed
                    obj.jump_delay = obj.coyote // 2
                    self.delete()
                elif obj.jump_delay == 0:
                    obj.hp -= self.damage
            else:
                obj.hp -= self.damage

    def _move(self):
        mspd = 1 if self.dir else -1
        self.pos += mspd * self.speed
        if not self.scollide(self.pos + vec2d(32 * mspd, 1)):
            self.pos.x -= mspd
            while not self.scollide(self.pos + vec2d(32 * mspd, 1)):
                self.pos.x -= mspd
            self.dir = not self.dir
            self.pos.x = floor(self.pos.x)
        if self.scollide(self.pos):
            self.pos.x -= mspd
            while self.scollide(self.pos):
                self.pos.x -= mspd
            self.dir = not self.dir
            self.pos.x = floor(self.pos.x)
