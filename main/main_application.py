"""Game-X."""
# OS import
from os import path, system, name as osname, getpid, getcwd
import sys
from psutil import Process

# Clear terminal
if osname == 'nt':
    system('cls')
else:
    system('clear')
print('################') # sepperator


# Base imports
from math import floor
import numpy as np
from time import time

# Library Imports
from pygame import image, event as pyevent#, Surface
from pygame.time import Clock
from pygame.locals import QUIT

# Custom imports
if __name__ == '__main__': # If main file
    from engine.components.camera import ObjCamera
    from engine.engine import ObjGameHandler, f_loop, f_limit
    from engine.components.vector import vec2d
    from engine.components.menu import (
        ObjMenu, ObjTextElement, ObjButtonElement)
else: # If being called as a module
    from .engine.components.camera import ObjCamera
    from .engine.engine import ObjGameHandler, f_loop, f_limit
    from .engine.components.vector import vec2d
    from .engine.components.menu import (
        ObjMenu, ObjTextElement, ObjButtonElement)

print('################') # sepperator



# Constants
if True:
    SIZE = vec2d(1024, 768)
    FULLTILE = 32
    FPS = 60
    PROCESS = Process(getpid())

    PATH = {}
    if getattr(sys, 'frozen', False):
        PATH['MAIN'] = path.dirname(sys.executable)
    else:
        PATH['MAIN'] = getcwd()
    PATH['DEBUGLOG'] = path.join(PATH['MAIN'], 'debug')
    PATH['ASSETS'] = path.join(PATH['MAIN'], 'assets')
    PATH['SPRITES'] = path.join(PATH['ASSETS'], 'sprites')
    PATH['LEVELS'] = path.join(PATH['ASSETS'], 'levels')
    PATH['TILEMAPS'] = path.join(PATH['ASSETS'], 'tilemaps')
    PATH['MUSIC'] = path.join(PATH['ASSETS'], 'music')
    PATH['SFX'] = path.join(PATH['ASSETS'], 'sfx')


# Object Creation functions # NOTE # Very Hard Coded
def object_creator(**kwargs):
    """Takes in a set of keywords and uses them to make an object.
        Required kwargs:
        name: name of the object being created.
        game: game handler used to instantiate the objects.

        Dependent kwargs:
        key: id of the key when created
        pos: position of the created object.
        data: dictionary containing kwargs for __init__."""
    name = kwargs['name']
    game = kwargs['game']
    if name == 'player':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjPlayer(game, key, pos, vec2d(FULLTILE, FULLTILE),
                  name, data)

    elif name == 'grav-orb':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjGravOrb(game, key, pos, vec2d(FULLTILE, FULLTILE),
                   name, data)

    elif name == 'door':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjDoor(game, key, pos, vec2d(FULLTILE, FULLTILE),
                name, data)

    elif name == 'button':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjButton(game, key, pos, vec2d(FULLTILE, FULLTILE/8),
                  name, data)

    elif name == 'spike':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjSpike(game, key, pos, vec2d(FULLTILE, FULLTILE/4),
                 name, data)

    elif name == 'spike-inv':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjSpikeInv(game, key, pos, vec2d(FULLTILE, FULLTILE/4),
                    name, data)

    elif name == 'juke-box':
        key = kwargs['key']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjJukeBox(game, key, name, data)

    elif name == 'main-menu':
        key = kwargs['key']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjMainMenu(game, key, name, data)


# Special classes
class ObjView(ObjCamera):
    """Camera like object which is limited to the inside of the level."""
    @property
    def pos(self):
        """Position getter."""
        return self._pos

    @pos.setter
    def pos(self, pos: tuple):
        """Position setter."""
        level_size0, level_size1 = self.level_size
        size0, size1 = self.size
        value0 = f_limit(pos[0], 0, level_size0 - size0)
        value1 = f_limit(pos[1], 0, level_size1 - size1)
        self._pos = vec2d(value0, value1).floor()


# Entities
class Entity():
    """Base class for all game entities."""
    def update_early(self, dt: float):
        """Update called first."""
        pass

    def update(self, dt: float):
        """Update called second."""
        pass

    def update_late(self, dt: float):
        """Update called last."""
        pass

    def draw(self):
        """Draw called in between back and foreground."""
        pass

class ObjJukeBox(Entity):
    """Responsible for sick beats."""
    def __init__(self, game: object, key: int, name: str, data: dict):
        game.obj.instantiate_object(key, self)
        self.game = game
        self.key = key
        self.name = name
        self.data = data

        # Music vars
        current_music = game.audio.music.get_current()
        self.music = data['name']
        self.loops = data['loops']
        self.volume = data['volume']

        if self.music is not None: # Add new music
            if current_music is None: # Start playing music
                game.audio.music.load(self.music)
                game.audio.music.set_volume(self.volume)
                game.audio.music.play(self.loops)

            elif current_music != self.music: # Queue up music
                game.audio.music.stop(1500)
                game.audio.music.queue(self.music, self.loops, self.volume)

        elif current_music is not None: # Fade music
            game.audio.music.stop(1000)

class ObjMainMenu(Entity):
    def __init__(self, game, key, name, data):
        game.obj.instantiate_object(key, self)
        self.game = game
        self.key = key
        self.name = name
        self.data = data

        self.menu = ObjMenu(game, SIZE)
        # TITLE
        title = ObjTextElement(self.menu, 'title')
        size = 36
        color = (144, 240, 240)
        text = 'Game-X: Now with depth!'
        pos = SIZE / 2
        font = 'consolas'
        title.set_vars(size=size, color=color, text=text,
                       pos=pos, font=font, center=True)

        # CAPTION
        caption = ObjTextElement(self.menu, 'caption')
        size = 16
        color = (128, 200, 200)
        text = 'Press enter to continue...'
        pos = SIZE / 2 + vec2d(0, 18 + 8)
        font = 'consolas'
        caption.set_vars(size=size, color=color, text=text,
                         pos=pos, font=font, center=True)

        # Button
        button = ObjButtonElement(self.menu, 'button')
        size = vec2d(128, 16)
        button.set_vars(size=size, pos=pos, call=self.pressed, center=True)

    def draw(self):
        self.menu.draw()

    def update(self, dt: float):
        if self.game.input.kb.get_key_pressed(40):
            self.game.level.load('level1')
        self.menu.get('button').update()

    def pressed(self, name: str):
        if name == 'button':
            self.game.level.load('level-1')


# Gameplay objects
class GameObject(Entity):
    """Class which all game objects inherit from."""
    def __init__(self, game: object, key: int, pos: vec2d,
                 size: vec2d, origin: vec2d = vec2d(0, 0)):
        self.game = game
        self.key = key
        self.pos = pos
        self.size = size
        self.origin = origin
        self.depth = 8
        game.obj.instantiate_object(key, self)
        rel = origin
        w, h = size - vec2d(1, 1)
        self.cpoints = (vec2d(rel.x, rel.y),
                        vec2d(rel.x+w, rel.y),
                        vec2d(rel.x+w, rel.y+h),
                        vec2d(rel.x, rel.y+h))
        self._frame = 0
        self.frames = []

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

    # Set current frames
    def set_frames(self, *fnames, alpha=0):
        """Frames setter."""
        self.frames = []
        for file in fnames:
            file_path = path.join(PATH['SPRITES'], file)
            if alpha == 0:
                self.frames.append(image.load(file_path).convert())
            elif alpha == 1:
                self.frames.append(image.load(file_path).convert_alpha())

    # Collision
    def scollide(self, pos=None, cpoints=None):
        """Check for static collisions."""
        # Match unspecified arguments
        if pos is None:
            pos = self.pos
        if cpoints is None:
            cpoints = self.cpoints

        # Check for collisions
        for point in cpoints:
            point += pos
            if self.game.collider.st.get(point):
                return 1
        return 0

    def dcollide(self, pos=None, key=None):
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
        return self.game.collider.dy.get_collision(pos, size, origin, key)

    # Drawing sprites
    def draw(self):
        """Draw called inbetween back and foreground."""
        pos = self.pos
        surface = self.frames[self.frame]
        self.game.draw.add(depth=self.depth, pos=pos, surface=surface)

    # Removing index in object handler
    def delete(self):
        """Called when object is deleted from Objects dictionary."""
        self.game.obj.delete(self.key)
        self.game.collider.dy.remove(self.key)

class ObjPlayer(GameObject):
    """Player game object."""
    def __init__(self, game, key, pos, size, name, data):
        # Game object initialization
        super().__init__(game, key, pos, size)
        self.name = name
        self.data = data

        # Add dynamic collider
        game.collider.dy.add(key, self)

        # Controls
        self.keys = {
            'jump': (44, 26, 82),
            'left': (4, 80),
            'right': (7, 79),
            'run':(225, 224),
            'reset':(21,)}

        # Key vars
        self.key = {
            'jump': 0,
            'Hjump': 0,
            'Hleft': 0,
            'Hright': 0,
            'Hrun': 0,
            'reset': 0}

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

        # Audio
        try:
            game.audio.sfx.tracks['boop.wav']
        except KeyError:
            game.audio.sfx.add('boop.wav')

    def update(self, dt):
        """Called every frame for each game object."""
        self._get_inputs()
        if self.mode == 0:
            # Reset room
            if self.key['reset'] == 1:
                self.game.level.reset()

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

    def draw(self):
        """Called every frame to draw each game object."""
        image = self.frames[self.frame]
        image.set_alpha(255)
        self.game.draw.add(16, pos=self.pos, surface=image.copy())
        for item in range(1, len(self.trail)):
            image.set_alpha(((image.get_alpha() + 1) // 2) - 1)
            self.game.draw.add(15, pos=self.trail[item], surface=image.copy())

    def die(self):
        self.game.audio.sfx.play('boop.wav')
        self.game.level.reset()
        return 'return'

    def _get_inputs(self):
        for key in self.key:
            if key[0] != 'H':
                self.key[key] = self.game.input.kb.get_key_pressed(
                    *self.keys[key])
            else:
                self.key[key] = self.game.input.kb.get_key_held(
                    *self.keys[key[1:]])

    def _movement(self):
        """Handle player movement."""
        # Veritcal controls
        self.jump -= np.sign(self.jump)
        if (self.key['jump'] and self.jump <= 0):
            self.jump = self.jump_lenience

        # Grounded
        self.grounded -= np.sign(self.grounded)

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
            if np.sign(move) != np.sign(self.hspd):
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
            self.jump_delay -= np.sign(self.jump_delay)

        # Jump gravity
        if np.sign(self.vspd) == np.sign(self.grav):
            self.vspd += self.grav * self.fallgrav
        elif self.key['Hjump']:
            self.vspd += self.grav * self.jumpgrav
        else:
            self.vspd += self.grav

    def _main_collision(self):
        """Check for player collisions and correct for them."""
        pos = self.pos
        hspd, vspd = self.hspd, self.vspd
        svspd, shspd = np.sign(vspd), np.sign(hspd)

        # Horizontal collision
        if self.scollide((pos.x + hspd, pos.y)):
            while self.scollide((pos.x + hspd, pos.y)):
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
        if self.scollide((pos.x, pos.y + vspd)):
            while self.scollide((pos.x, pos.y + vspd)):
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
        self.campos = self.pos + self.game.cam.size * -1/2
        dcam = (self.campos - self.game.cam.pos) * self.camspeed
        self.game.cam.pos = self.game.cam.pos + dcam

class ObjButton(GameObject):
    """Button game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size,
                         origin=vec2d(0, FULLTILE-size[1]))
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data
        self.door_id = data['door']
        self.set_frames('button0.png', 'button1.png', alpha=1)

    def collide(self, obj: object):
        """When collided with by player, open the door."""
        if obj.name == 'player' and self.frame == 0:
            self.game.obj.obj[self.door_id].frame = 1
            self.frame = 1

class ObjDoor(GameObject):
    """Door game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size)
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data
        self.next_level = data['level']

        # Images
        self.set_frames('door0.png', 'door1.png')

    def collide(self, obj: object) -> str:
        if obj.name == 'player':
            if self.frame == 1:
                self.game.level.load(self.next_level)
                return 'return'

class ObjGravOrb(GameObject):
    """GravOrb game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size)
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data
        self.grav = data['grav']

        # Images
        if self.grav > 0:
            self.set_frames('grav-orb0.png', alpha=1)
        elif self.grav == 0:
            self.set_frames('grav-orb1.png', alpha=1)
        elif self.grav < 1:
            self.set_frames('grav-orb2.png', alpha=1)

    def collide(self, obj: object):
        if obj.name == 'player':
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
                if np.sign(obj.grav) in (0, 1):
                    obj.grav = obj.default_grav * grav_mult
                else:
                    obj.grav = obj.default_grav * -grav_mult

            # Remove self after collision with player
            self.delete()

class ObjSpike(GameObject):
    """Spike game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size,
                         origin=vec2d(0, FULLTILE-size[1]))
        self.name = name
        self.data = data
        game.collider.dy.add(key, self)

        # Images
        self.set_frames('spike.png', alpha=1)

    def collide(self, obj: object) -> str:
        if obj.name == 'player' and obj.vspd <= 0:
            return obj.die()

class ObjSpikeInv(GameObject):
    """Spike game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size)
        self.name = name
        self.data = data
        game.collider.dy.add(key, self)

        # Images
        self.set_frames('spike-inv.png', alpha=1)

    def collide(self, obj: object) -> str:
        if obj.name == 'player' and obj.vspd >= 0:
            return obj.die()



# Main application method
def main(debug: bool = False):
    """Main game loop."""
    GAME = ObjGameHandler(SIZE, FULLTILE, PATH, object_creator,
                          fps=FPS, debug=debug)
    GAME.cam = ObjView(SIZE)
    GAME.level.load('mainmenu')
    GAME.parallax = 1
    if GAME.debug:
        GAME.debug.time_record = {
            'Update': 0,
            'DrawAdd': 0,
            'DrawParse': 0,
            'Render': 0}

    # Timing info
    clock = Clock()
    dt = 1

    # Gameplay loop
    while GAME.run:
        # Start debug timing
        if GAME.debug:
            t = time()


        # Reset inputs for held keys
        GAME.input.reset()

        # Event Handler
        for event in pyevent.get():
            # Exit GAME
            if event.type == QUIT:
                return
            else:
                GAME.input.handle_events(event)
        if GAME.input.kb.get_key_pressed(41):
            GAME.end()
            return

        # Update calls
        update(GAME, dt)
        if GAME.debug:
            GAME.debug.time_record['Update'] += (time() - t)
            t = time()

        # Draw calls
        if dt > 0.9:
            # Debug Display
            if GAME.debug:
                fps = GAME.debug.menu.get('fps')
                text = 'fps: {:.0f}'.format(clock.get_fps())
                fps.set_vars(text=text)

                campos = GAME.debug.menu.get('campos')
                text = 'cam pos: {}'.format(GAME.cam.pos)
                campos.set_vars(text=text)

                memory = GAME.debug.menu.get('memory')
                mem = PROCESS.memory_info().rss
                mb = mem // (10**6)
                kb = (mem - (mb * 10**6)) // 10**3
                text = 'memory: {} MB, {} KB'.format(mb, kb)
                memory.set_vars(text=text)

            drawadd(GAME)
            if GAME.debug:
                GAME.debug.time_record['DrawAdd'] += time() - t
                t = time()

            drawparse(GAME)
            if GAME.debug:
                GAME.debug.time_record['DrawParse'] += time() - t
                t = time()

            # Render to screen
            render(GAME)
            if GAME.debug:
                GAME.debug.time_record['Render'] += (time() - t)

        # Tick clock
        dt = clock.tick(FPS) * (FPS/1000)
        if GAME.debug:
            GAME.debug.tick()

def update(game: object, dt: float):
    """Update call."""
    game.obj.update_early(dt)
    game.obj.update(dt)
    game.obj.update_late(dt)

def drawadd(game: object):
    """Draw call."""
    game.draw.draw()
    if game.debug:
        game.debug.menu.draw()

def drawparse(game: object):
    # Blank screen
    game.cam.blank()
    game.draw.render(game.cam)

def render(game: object):
    """Render textures to screen."""
    game.window.render(game.cam)


# If main file
if __name__ == '__main__':
    main(True)
