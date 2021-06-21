"""All game objects."""

from os import path

from numpy import sign
from pygame import image
from pygame.event import Event, post
from pygame.surface import Surface

from main.code.constants import FULLTILE
from main.code.engine.components.maths import f_loop
from main.code.engine.components.output_handler import Draw
from main.code.engine.constants import (
    LEVEL_LOAD,
    LEVEL_RESET,
    colorize,
    cprint,
)
from main.code.engine.engine import Engine
from main.code.engine.types import vec2d
from main.code.objects.entities import Entity, ObjPauseMenu


def rect_overlap(pos: vec2d, size: vec2d, opos: vec2d, osize: vec2d) -> bool:
    if (
        pos.x < opos.x + osize.x
        and pos.x + size.x > opos.x
        and pos.y < opos.y + osize.y
        and pos.y + size.y > opos.y
    ):
        return True
    return False


# Game objects
class GameObject(Entity):
    """Class which all game objects inherit from."""

    def __init__(
        self,
        engine: Engine,
        key: int,
        name: str,
        data: dict,
        pos: vec2d,
        size: vec2d = vec2d(32, 32),
        offset: vec2d = vec2d(0, 0),
    ):
        super().__init__(engine, key, name, data)
        self.engine = engine
        self.origin = offset
        self.col = Collider(engine, pos, size, offset)

        self.depth = 1
        rel = offset
        w, h = size - vec2d(1, 1)
        self.cpoints = (
            vec2d(rel.x, rel.y),
            vec2d(rel.x + w, rel.y),
            vec2d(rel.x + w, rel.y + h),
            vec2d(rel.x, rel.y + h),
        )
        self._frame = 0
        self.frames: list[Surface] = []

    # Position
    @property
    def pos(self) -> vec2d:
        return self.col.pos

    @pos.setter
    def pos(self, pos: vec2d):
        self.col.pos = pos

    # Size
    @property
    def size(self) -> vec2d:
        return self.col.size

    @size.setter
    def size(self, size: vec2d):
        self.col.size = size

    # Set current frames
    def set_frames(self, *fnames, alpha: bool = False):
        """Frames setter."""
        self.frames = []
        sprite_path = self.engine.paths["sprites"]
        for file in fnames:
            file_path = path.join(sprite_path, file)
            try:
                if alpha:
                    self.frames.append(image.load(file_path).convert_alpha())
                else:
                    self.frames.append(image.load(file_path).convert())

            except FileNotFoundError as error:
                msg = (
                    "Sprite image not found."
                    f"Images path: {file_path}"
                    f"Engine sprite path: {sprite_path}"
                )
                msg = "\n\t" + "\t".join(msg)
                msg = colorize(msg, "red")
                raise FileNotFoundError(msg) from error

    @property
    def frame(self) -> int:
        """Frame getter."""
        return self._frame

    @frame.setter
    def frame(self, frame: int):
        """Frame setter."""
        if frame > len(self.frames):
            frame = f_loop(frame, 0, len(self.frames))
        self._frame = frame

    # Collision
    def scollide(self, pos: vec2d = None) -> bool:
        """Check for static collisions."""
        return self.col.scollide(pos)

    def dcollide(self, pos: vec2d = None, key: int = None) -> list:
        """Check for dynamic collisions.
        Set key to -1 if you want to include self in collision"""
        # Match unspecified arguments
        if key is None:
            key = self.key
        if pos is None:
            pos = self.pos
        size = self.size
        pos += self.origin

        # Get colliders
        colliders = self.engine.objects.col.dy.get_colliders()
        collide: list[object] = []

        # Check for collisions
        for cobj in colliders:
            if cobj.key != key:
                if issubclass(cobj.__class__, GameObject):
                    # Get other's pos and size
                    opos = cobj.pos + cobj.origin
                    osize = cobj.size

                    # Check for overlap
                    if rect_overlap(pos, size, opos, osize):
                        collide.append(cobj)

        return collide

    # Drawing sprites
    def draw(self, draw: Draw):
        """Draw called inbetween back and foreground."""
        pos = self.pos
        surface = self.frames[self.frame]
        draw.add(depth=self.depth, pos=pos, surface=surface)

    # Removing index in object handler
    def delete(self):
        """Called when object is deleted from Objects dictionary."""
        self.engine.objects.ent.delete(self.key)
        self.engine.objects.col.dy.remove(self.key)


class Collider:
    def __init__(
        self,
        engine: Engine,
        pos: vec2d,
        size: vec2d,
        offset: vec2d = vec2d(0, 0),
    ):
        self.engine = engine
        self.pos = pos
        self.size = size
        self.offset = offset
        dpos = 1e-6  # Used to keep all points just before the size
        w, h = size - dpos

        self.cpoints = (
            vec2d(offset.x, offset.y),
            vec2d(offset.x + w, offset.y),
            vec2d(offset.x + w, offset.y + h),
            vec2d(offset.x, offset.y + h),
        )

    def scollide(self, pos: vec2d = None) -> bool:
        if pos is None:
            pos = self.pos
        for point in self.cpoints:
            if self.engine.objects.col.st.get(pos + point):
                return True
        return False


class Damageable:
    def __init__(self):
        self._hp: int = 1

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, hp: int):
        self._hp = hp


class ObjPlayer(GameObject, Damageable):
    """Player game object."""

    def __init__(
        self, engine: Engine, key: int, name: str, data: dict, pos: vec2d
    ):
        # Game object initialization
        super().__init__(engine, key, name, data, pos, vec2d(32, 32))

        # Add dynamic collider
        engine.objects.col.dy.add(key, self)

        # Controls
        self.kkeys = {
            "jump": (44, 26, 82),
            "left": (4, 80),
            "right": (7, 79),
            "run": (225, 224),
            "reset": (21,),
            "pause": (41,),
        }

        # Key vars
        self.kkey = {
            "jump": False,
            "Hjump": False,
            "Hleft": False,
            "Hright": False,
            "Hrun": False,
            "reset": False,
            "pause": False,
        }

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

        # State machine
        self.mode = 0
        self.campos = (0, 0)
        self.camspeed = 0.25

        # Sprite
        self.set_frames("player.png")
        self.trail: list[vec2d] = []

        # Health
        self.iframes = 45
        self.iframe = 0
        self.hp = 5
        self.damage = 4
        self.iframe = 0

        # Audio
        engine.output.audio.sfx.add("boop.wav")

        # Pause menu
        self.pause_menu = ObjPauseMenu(self.engine, 0, "", {})
        self.engine.objects.ent.sobj["pause-menu"] = self.pause_menu
        self.pause_menu.menu.visible = False

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, hp: int):
        if self.iframe == 0:
            self._hp = hp
            self.iframe = self.iframes

    def update(self, paused: bool):
        """Called every frame for each game object."""
        self._get_inputs()
        if self.kkey["pause"]:
            self.engine.pause()
            v = self.pause_menu.menu.visible
            self.pause_menu.menu.visible = not v
        if paused:
            pass
        else:
            self.iframe -= sign(self.iframe)
            if self.hp <= 0:
                self._die()

            if self.mode == 0:
                # Reset room
                if self.kkey["reset"] == 1:
                    post(Event(LEVEL_RESET))

                # Dynamic collision
                self._dcol()

                # Move player
                self._movement()

                self.trail.insert(0, self.pos)
                if len(self.trail) > 4:
                    self.trail = self.trail[0:3]

                # Update camera position
                self._move_cam()

    def draw(self, draw: Draw):
        """Called every frame to draw each game object."""
        # Get player sprite
        image = self.frames[self.frame]

        # Blinking when invulnerable
        if self.iframe % 6 == 0:
            image.set_alpha(255)
        else:
            image.set_alpha(63)

        # Draw sprites
        alpha = image.get_alpha()
        if alpha is not None:
            # Draw player
            draw.add(4, pos=self.pos, surface=image.copy())

            # Draw trail
            for item in range(1, len(self.trail)):
                alpha = ((alpha + 1) // 2) - 1
                image.set_alpha(alpha)
                draw.add(3, pos=self.trail[item], surface=image.copy())

    def _jump(self):
        if self.grounded > 0:
            if self.grav != 0:
                self.vspd = -((self.hspd / 8) ** 2)
            self.jump_delay = self.coyote
            self.vspd -= self.jump_speed
        elif self.grounded < 0:
            if self.grav != 0:
                self.vspd = (self.hspd / 8) ** 2
            self.jump_delay = self.coyote
            self.vspd += self.jump_speed

    def _die(self):
        post(Event(LEVEL_RESET))
        self.engine.output.audio.sfx.play("boop.wav")

    def _get_inputs(self):
        for key in self.kkey:
            if key[0] != "H":
                self.kkey[key] = self.engine.input.kb.get_key_pressed(
                    *self.kkeys[key]
                )
            else:
                self.kkey[key] = self.engine.input.kb.get_key_held(
                    *self.kkeys[key[1:]]
                )

    def _movement(self):
        """Handle player movement."""
        # Veritcal controls
        self.jump -= sign(self.jump)
        if self.kkey["jump"] and self.jump <= 0:
            self.jump = self.jump_lenience

        # Grounded
        self.grounded -= sign(self.grounded)

        # Floor
        if self.grav >= 0 and self.scollide(self.pos + vec2d(0, 1)):
            self.jump_delay = 0
            if self.grav != 0:
                self.grounded = self.coyote  # Normal Gravity
            else:
                self.grounded = 1  # Zero Gravity

        # Ceiling
        if self.grav <= 0 and self.scollide(self.pos + vec2d(0, -1)):
            self.jump_delay = 0
            if self.grav != 0:
                self.grounded = -self.coyote  # Normal Gravity
            else:
                self.grounded = -1  # Zero Gravity

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
        move = self.kkey["Hright"] - self.kkey["Hleft"]
        if self.grounded and self.grav != 0:
            if move != 0:
                # Dynamic grounded
                self.hspd *= self.ground_fric_dynamic

                # Running
                if self.kkey["Hrun"]:
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
        if (
            self.grounded != 0
            and self.kkey["jump"] > 0
            and self.jump_delay == 0
        ):
            self._jump()
        else:
            self.jump_delay -= sign(self.jump_delay)

        # Jump gravity
        if sign(self.vspd) == sign(self.grav):
            self.vspd += self.grav * self.fallgrav
        elif self.kkey["Hjump"]:
            self.vspd += self.grav * self.jumpgrav
        else:
            self.vspd += self.grav

    def _main_collision(self):
        """Check for player collisions and correct for them."""
        pos = self.pos
        hspd, vspd = self.hspd, self.vspd
        svspd, shspd = sign(vspd), sign(hspd)

        # Horizontal collision
        if self.scollide(pos + vec2d(hspd, 0)):
            pos = vec2d((pos.x // FULLTILE) * FULLTILE, pos.y)
            while not self.scollide(pos):
                pos += vec2d(FULLTILE * shspd, 0)
            pos -= vec2d(FULLTILE * shspd, 0)
            hspd = 0

        # Dynamic collision
        self._dcol(pos)

        # Vertical collision
        if self.scollide(pos + vec2d(0, vspd)):
            pos = vec2d(pos.x, (pos.y // FULLTILE) * FULLTILE)
            if svspd == 1:
                pos += vec2d(0, FULLTILE)
            while not self.scollide(pos):
                pos += vec2d(0, FULLTILE * svspd)
            pos -= vec2d(0, FULLTILE * svspd)
            vspd = 0

        # Dynamic collision
        self._dcol(pos)
        self.pos = pos
        self.hspd = hspd
        self.vspd = vspd

    def _dcol(self, pos=None):
        col = self.dcollide(pos)
        for obj in col:
            try:
                return obj.collide(self)
            except AttributeError:
                pass

    def _move_cam(self):
        """Move Camera."""
        self.campos = self.pos + self.engine.cam.size * -1 / 2
        dcam = (self.campos - self.engine.cam.pos) * self.camspeed
        self.engine.cam.pos = self.engine.cam.pos + dcam

    def delete(self):
        super().delete()
        del self.engine.objects.ent.sobj["pause-menu"]


class ObjButton(GameObject):
    """Button game object."""

    def __init__(
        self, engine: Engine, key: int, name: str, data: dict, pos: vec2d
    ):
        # GameObject initialization
        super().__init__(
            engine,
            key,
            name,
            data,
            pos,
            vec2d(32, 8),
            offset=vec2d(0, FULLTILE - 8),
        )
        engine.objects.col.dy.add(key, self)
        try:
            self.door_id = self.data["door"]
        except KeyError:
            cprint("Door object not set for button!", "red")
        self.set_frames("button0.png", "button1.png", alpha=True)

    def collide(self, obj: GameObject):
        """When collided with by player, open the door."""
        if isinstance(obj, ObjPlayer):
            if self.frame == 0:
                try:
                    self.engine.objects.ent.obj[self.door_id].frame = 1
                except AttributeError:
                    cprint("Unable to find door!", "red")
                self.frame = 1


class ObjDoor(GameObject):
    """Door game object."""

    def __init__(
        self, engine: Engine, key: int, name: str, data: dict, pos: vec2d
    ):
        # GameObject initialization
        super().__init__(engine, key, name, data, pos, vec2d(32, 32))
        engine.objects.col.dy.add(key, self)
        try:
            self.next_level = self.data["level"]
        except KeyError:
            cprint("Door has no next level set!", "red")

        # Images
        self.set_frames("door0.png", "door1.png")

    def collide(self, obj: GameObject):
        if isinstance(obj, ObjPlayer):
            if self.frame == 1:
                try:
                    post(Event(LEVEL_LOAD, {"level": self.next_level}))
                except AttributeError:
                    cprint("Unable to load level!", "red")


class ObjGravOrb(GameObject):
    """GravOrb game object."""

    def __init__(
        self, engine: Engine, key: int, name: str, data: dict, pos: vec2d
    ):
        # GameObject initialization
        super().__init__(engine, key, name, data, pos, vec2d(32, 32))
        engine.objects.col.dy.add(key, self)
        self.grav = self.data["grav"]

        # Images
        if self.grav > 0:
            self.set_frames("grav-orb0.png", alpha=True)
        elif self.grav == 0:
            self.set_frames("grav-orb1.png", alpha=True)
        elif self.grav < 1:
            self.set_frames("grav-orb2.png", alpha=True)

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

    def __init__(
        self, engine: Engine, key: int, name: str, data: dict, pos: vec2d
    ):
        # GameObject initialization
        super().__init__(
            engine,
            key,
            name,
            data,
            pos,
            vec2d(32, 4),
            offset=vec2d(0, FULLTILE - 4),
        )
        engine.objects.col.dy.add(key, self)
        self.damage = 5

        # Images
        self.set_frames("spike.png", alpha=True)

    def collide(self, obj: ObjPlayer):
        if isinstance(obj, ObjPlayer):
            if obj.vspd <= 0:
                obj.hp -= self.damage


class ObjSpikeInv(GameObject):
    """Spike game object, but upside down."""

    def __init__(
        self, engine: Engine, key: int, name: str, data: dict, pos: vec2d
    ):
        # GameObject initialization
        super().__init__(engine, key, name, data, pos, vec2d(32, 4))
        engine.objects.col.dy.add(key, self)
        self.damage = 5

        # Images
        self.set_frames("spike-inv.png", alpha=True)

    def collide(self, obj: GameObject):
        if isinstance(obj, ObjPlayer):
            if obj.vspd >= 0:
                obj.hp -= self.damage
