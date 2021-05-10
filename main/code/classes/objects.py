from os import path
from math import floor
from typing import Optional

from numpy import sign
from pygame import image

from .constants import *
from .entities import Entity, ObjPauseMenu
from ..engine.engine import Engine
from ..engine.components.draw import Draw
from ..engine.components.menu import *
from ..engine.components.maths import f_loop

# Game objects
class GameObject(Entity):
    """Class which all game objects inherit from."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, origin: vec2d = vec2d(0, 0)):
        super().__init__(engine)
        self.key = key
        self.pos = pos
        self.size = size
        self.name = name
        self.origin = origin
        self.depth = 8
        engine.obj.instantiate_object(key, self)
        rel = origin
        w, h = size - vec2d(1, 1)
        self.cpoints = (vec2d(rel.x, rel.y),
                        vec2d(rel.x+w, rel.y),
                        vec2d(rel.x+w, rel.y+h),
                        vec2d(rel.x, rel.y+h))
        self._frame = 0
        self.frames = []

    # Set current frames
    def set_frames(self, *fnames, alpha=0):
        """Frames setter."""
        self.frames = []
        sprite_path = self.engine.paths['sprites']
        for file in fnames:
            file_path = path.join(sprite_path, file)
            try:
                if alpha == 0:
                    self.frames.append(image.load(file_path).convert())
                elif alpha == 1:
                    self.frames.append(image.load(file_path).convert_alpha())
            except FileNotFoundError as error:
                code = ['Sprite image not found.',
                        'Images path: {}'.format(file_path),
                        'Engine sprite path: {}'.format(sprite_path)]
                raise FileNotFoundError('\n  ' + '\n  '.join(code)) from error

    @property
    def frame(self):
        """Frame getter."""
        return self._frame

    @frame.setter
    def frame(self, frame: int):
        """Frame setter."""
        if frame > len(self.frames):
            frame = f_loop(frame, 0, len(self.frames))
        self._frame = frame

    # Collision
    def scollide(self, pos: vec2d = None,
                 cpoints: Tuple[vec2d, vec2d, vec2d, vec2d] = None) -> bool:
        """Check for static collisions."""
        # Match unspecified arguments
        if pos is None:
            pos = self.pos
        if cpoints is None:
            cpoints = self.cpoints

        # Check for collisions
        for point in cpoints:
            point += pos
            if self.engine.col.st.get(point):
                return True
        return False

    def dcollide(self, pos: vec2d = None, key: int = None) -> list:
        """Check for dynamic collisions.
           Set key to -1 if you want to include self in collision"""
        # Match unspecified arguments
        if key is None:
            key = self.key
        if pos is None:
            pos = self.pos
        size = self.size
        origin = self.origin

        # Check for collision
        return self.engine.col.dy.get_collision(pos, size, origin, key)

    # Drawing sprites
    def draw(self, draw: Draw):
        """Draw called inbetween back and foreground."""
        pos = self.pos
        surface = self.frames[self.frame]
        draw.add(depth=self.depth, pos=pos, surface=surface)

    # Removing index in object handler
    def delete(self):
        """Called when object is deleted from Objects dictionary."""
        self.engine.obj.delete(self.key)
        self.engine.col.dy.remove(self.key)

class ObjPlayer(GameObject):
    """Player game object."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # Game object initialization
        super().__init__(engine, key, pos, size, name)
        self.data = data

        # Add dynamic collider
        engine.col.dy.add(key, self)

        # Controls
        self.keys = {
            'jump': (44, 26, 82),
            'left': (4, 80),
            'right': (7, 79),
            'run': (225, 224),
            'reset': (21,),
            'pause': (41,)}

        # Key vars
        self.key = {
            'jump': 0,
            'Hjump': 0,
            'Hleft': 0,
            'Hright': 0,
            'Hrun': 0,
            'reset': 0,
            'pause': 0}

        # Ground
        self.hspd, self.vspd = 0, 0
        self.walk_speed = 0.60
        self.run_speed = 1.25
        self.ground_fric_static = 0.48
        self.ground_fric_dynamic = 0.88

        # Air
        self.air_fric_retro = 0.88
        self.air_fric_pro = 0.98
        self.air_speed = 0.4
        self.default_grav = 1.2
        self.grav = self.default_grav
        self.fallgrav = 0.6

        # Jump
        self.jump = 0
        self.jump_speed = 10
        self.jumpgrav = 0.35
        self.grounded = 0
        self.coyote = 8
        self.jump_lenience = 6
        self.jump_delay = 0

        # State Machine
        self.mode = 0
        self.campos = (0, 0)
        self.camspeed = (0.25, 0.25)

        # Sprite
        self.set_frames('player.png')
        self.trail = []
        self.pause_menu = None

        # Audio
        try:
            engine.aud.sfx.tracks['boop.wav']
        except KeyError:
            engine.aud.sfx.add('boop.wav')

    def post_init(self):
        # Pause menu
        key = self.engine.obj.instantiate_key()
        self.pause_menu = ObjPauseMenu(self.engine, key, '', {})
        self.pause_menu.menu.visible = False

    def update(self, paused: bool):
        """Called every frame for each game object."""
        self._get_inputs()
        if self.key['pause']:
            self.engine.pause()
            v = self.pause_menu.menu.visible
            self.pause_menu.menu.visible = not v
        if paused:
            pass
        else:
            if self.mode == 0:
                # Reset room
                if self.key['reset'] == 1:
                    self.engine.lvl.reset()
                    return

                # Dynamic collisions
                col = self.dcollide()
                for obj in col:
                    try:
                        if obj.collide(self) == 'return':
                            return
                    except AttributeError:
                        pass

                # Move player
                self._movement()

                self.trail.insert(0, self.pos)
                if len(self.trail) > 4:
                    self.trail = self.trail[0:3]

                # Update camera position
                self._move_cam()

    def draw(self, draw: Draw):
        """Called every frame to draw each game object."""
        image = self.frames[self.frame]
        image.set_alpha(255)
        draw.add(4, pos=self.pos, surface=image.copy())
        for item in range(1, len(self.trail)):
            image.set_alpha(((image.get_alpha() + 1) // 2) - 1)
            draw.add(3, pos=self.trail[item], surface=image.copy())

    def die(self):
        self.engine.aud.sfx.play('boop.wav')
        self.engine.lvl.reset()
        return 'return'

    def _get_inputs(self):
        for key in self.key:
            if key[0] != 'H':
                self.key[key] = self.engine.inp.kb.get_key_pressed(
                    *self.keys[key])
            else:
                self.key[key] = self.engine.inp.kb.get_key_held(
                    *self.keys[key[1:]])

    def _movement(self):
        """Handle player movement."""
        # Veritcal controls
        self.jump -= sign(self.jump)
        if (self.key['jump'] and self.jump <= 0):
            self.jump = self.jump_lenience

        # Grounded
        self.grounded -= sign(self.grounded)

        # Floor
        if self.grav >= 0 and self.scollide(self.pos + vec2d(0, 1)):
            self.jump_delay = 0
            if self.grav != 0:
                self.grounded = self.coyote # Normal Gravity
            else:
                self.grounded = 1 # Zero Gravity

        # Ceiling
        if self.grav <= 0 and self.scollide(self.pos + vec2d(0, -1)):
            self.jump_delay = 0
            if self.grav != 0:
                self.grounded = -self.coyote # Normal Gravity
            else:
                self.grounded = -1 # Zero Gravity

        # Horizontal and vertical movement
        self._horizontal_move()
        self._vertical_move()

        # Collision
        self._main_collision()

        # Update position
        self.pos += vec2d(self.hspd, self.vspd)

    def _horizontal_move(self):
        """Horizontal movement."""
        # Horizontal speed
        move = (self.key['Hright'] - self.key['Hleft'])
        if self.grounded and self.grav != 0:
            if move != 0:
                # Dynamic grounded
                self.hspd *= self.ground_fric_dynamic

                # Running
                if self.key['Hrun']:
                    self.hspd += move * self.run_speed
                else:
                    self.hspd += move * self.walk_speed
            else:
                # Static grounded
                self.hspd *= self.ground_fric_static
        else:
            if sign(move) != sign(self.hspd):
                # Retrograde aerial
                self.hspd += move * self.air_speed * 2
                self.hspd *= self.air_fric_retro
            else:
                # Prograde aerial
                self.hspd += move * self.air_speed / 2
                self.hspd *= self.air_fric_pro

    def _vertical_move(self):
        """Vertical movement."""
        # Jumping
        if (self.grounded != 0 and self.key['jump'] > 0
            and self.jump_delay == 0):
            if self.grounded > 0:
                if self.grav != 0:
                    self.vspd = -(self.hspd/8)**2
                self.jump_delay = self.coyote
                self.vspd -= self.jump_speed
            elif self.grounded < 0:
                if self.grav != 0:
                    self.vspd = (self.hspd/8)**2
                self.jump_delay = self.coyote
                self.vspd += self.jump_speed
        else:
            self.jump_delay -= sign(self.jump_delay)

        # Jump gravity
        if sign(self.vspd) == sign(self.grav):
            self.vspd += self.grav * self.fallgrav
        elif self.key['Hjump']:
            self.vspd += self.grav * self.jumpgrav
        else:
            self.vspd += self.grav

    def _main_collision(self):
        """Check for player collisions and correct for them."""
        pos = self.pos
        hspd, vspd = self.hspd, self.vspd
        svspd, shspd = sign(vspd), sign(hspd)

        # Horizontal collision
        if self.scollide(vec2d(pos.x + hspd, pos.y)):
            while self.scollide(vec2d(pos.x + hspd, pos.y)):
                hspd -= shspd
            pos = vec2d(floor(pos.x + hspd), pos.y)
            hspd = 0

        # Dynamic collisions
        col = self.dcollide(pos=pos)
        for obj in col:
            try:
                if obj.collide(self) == 'return':
                    return
            except AttributeError:
                pass

        # Vertical collision
        if self.scollide(vec2d(pos.x, pos.y + vspd)):
            while self.scollide(vec2d(pos.x, pos.y + vspd)):
                vspd -= svspd
            pos = vec2d(pos.x, floor(pos.y + vspd))
            vspd = 0

        # Dynamic collisions
        col = self.dcollide(pos=pos)
        for obj in col:
            try:
                if obj.collide(self) == 'return':
                    return
            except AttributeError:
                pass

        self.pos = pos
        self.hspd = hspd
        self.vspd = vspd

    def _move_cam(self):
        """Move Camera."""
        self.campos = self.pos + self.engine.cam.size * -1/2
        dcam = (self.campos - self.engine.cam.pos) * self.camspeed
        self.engine.cam.pos = self.engine.cam.pos + dcam

class ObjButton(GameObject):
    """Button game object."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # GameObject initialization
        super().__init__(engine, key, pos, size, name,
                         origin=vec2d(0, FULLTILE-size[1]))
        engine.col.dy.add(key, self)
        self.data = data
        self.door_id = data['door']
        self.set_frames('button0.png', 'button1.png', alpha=1)

    def collide(self, obj: GameObject):
        """When collided with by player, open the door."""
        if isinstance(obj, ObjPlayer):
            if self.frame == 0:
                self.engine.obj.obj[self.door_id].frame = 1
                self.frame = 1

class ObjDoor(GameObject):
    """Door game object."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # GameObject initialization
        super().__init__(engine, key, pos, size, name)
        engine.col.dy.add(key, self)
        self.data = data
        self.next_level = data['level']

        # Images
        self.set_frames('door0.png', 'door1.png')

    def collide(self, obj: GameObject) -> Optional[str]:
        if isinstance(obj, ObjPlayer):
            if self.frame == 1:
                self.engine.lvl.load(self.next_level)
                return 'return'

class ObjGravOrb(GameObject):
    """GravOrb game object."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # GameObject initialization
        super().__init__(engine, key, pos, size, name)
        engine.col.dy.add(key, self)
        self.data = data
        self.grav = data['grav']

        # Images
        if self.grav > 0:
            self.set_frames('grav-orb0.png', alpha=1)
        elif self.grav == 0:
            self.set_frames('grav-orb1.png', alpha=1)
        elif self.grav < 1:
            self.set_frames('grav-orb2.png', alpha=1)

    def collide(self, obj: GameObject):
        if isinstance(obj, ObjPlayer):
            grav_mult = self.grav

            # Toggle zero grav
            if grav_mult == 0:
                if obj.grav == 0:
                    obj.grav = obj.default_grav
                else:
                    obj.grav = 0

            # Change positive gravity
            elif grav_mult > 0:
                obj.grav = obj.default_grav * grav_mult

            # Flip gravity and change grav ammount
            elif grav_mult < 0:
                if sign(obj.grav) in (0, 1):
                    obj.grav = obj.default_grav * grav_mult
                else:
                    obj.grav = obj.default_grav * -grav_mult

            # Remove self after collision with player
            self.delete()

class ObjSpike(GameObject):
    """Spike game object."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # GameObject initialization
        super().__init__(engine, key, pos, size, name,
                         origin=vec2d(0, FULLTILE-size[1]))
        self.name = name
        self.data = data
        engine.col.dy.add(key, self)

        # Images
        self.set_frames('spike.png', alpha=1)

    def collide(self, obj: ObjPlayer) -> Optional[str]:
        if isinstance(obj, ObjPlayer):
            if obj.vspd <= 0:
                return obj.die()

class ObjSpikeInv(GameObject):
    """Spike game object, but upside down."""
    def __init__(self, engine: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # GameObject initialization
        super().__init__(engine, key, pos, size, name)
        self.name = name
        self.data = data
        engine.col.dy.add(key, self)

        # Images
        self.set_frames('spike-inv.png', alpha=1)

    def collide(self, obj: GameObject) -> Optional[str]:
        if isinstance(obj, ObjPlayer):
            if obj.vspd >= 0:
                return obj.die()
