# Standard library
from os import execlp, path, system, name as osname, getpid
from typing import Optional, Tuple
from math import floor
from time import time

# External libraries
from numpy import sign
from psutil import Process
from pygame.constants import KEYDOWN, QUIT
from pygame.time import Clock
from pygame.event import get as get_events
from pygame import image

# Package imports
if __name__ == '__main__':
    # If ran directly
    from engine.types.vector import vec2d
    from engine.engine import Engine
    from engine.components.grid import f_loop, f_limit
    from engine.components.camera import Camera
    from engine.components.draw import Draw
    from engine.components.menu import (
        Menu, MenuText, MenuButtonFull, MenuElement)
else:
    # If imported as module
    from .engine.types.vector import vec2d
    from .engine.engine import Engine
    from .engine.components.grid import f_loop, f_limit
    from .engine.components.camera import Camera
    from .engine.components.draw import Draw
    from .engine.components.menu import (
        Menu, MenuText, MenuButtonFull, MenuElement)



# Clear the terminal
def clear_terminal():
    if osname == 'nt':
        system('cls')
    else:
        system('clear')

clear_terminal()
print('All imports finished.')

# Constants
if True:
    FULLTILE = 32
    FPS = 60
    SIZE = vec2d(1024, 768)
    PROCESS = Process(getpid())

# Object creation function
def create_objects(engine: Engine, **kwargs):
    """Takes in a set of keywords and uses them to make an object.
        Required kwargs:
        name: name of the object being created.
        engine: engine which contains game components.

        Dependent kwargs:
        key: id of the key when created
        pos: position of the created object.
        data: dictionary containing kwargs for __init__."""
    name = kwargs['name']
    if name == 'player':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE)
        ObjPlayer(engine, key, pos, size, name, data)

    elif name == 'grav-orb':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE)
        ObjGravOrb(engine, key, pos, size, name, data)

    elif name == 'door':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE)
        ObjDoor(engine, key, pos, size, name, data)

    elif name == 'button':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE//8)
        ObjButton(engine, key, pos, size, name, data)

    elif name == 'spike':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE//4)
        ObjSpike(engine, key, pos, size, name, data)

    elif name == 'spike-inv':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE//4)
        ObjSpikeInv(engine, key, pos, size, name, data)

    elif name == 'juke-box':
        key = kwargs['key']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        ObjJukeBox(engine, key, name, data)

    elif name == 'main-menu':
        key = kwargs['key']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        ObjMainMenu(engine, key, name, data)



# Special
class View(Camera):# type: ignore
    """Camera like object which is limited to the inside of the level."""
    def __init__(self, size: vec2d):
        super().__init__(size)
        self.level_size = size

    def pos_get(self) -> vec2d:
        return self._pos

    def pos_set(self, pos: vec2d):
        """Position setter."""
        size0 = self.size
        size1 = self.level_size
        x = f_limit(pos.x, 0, size1.x - size0.x)
        y = f_limit(pos.y, 0, size1.y - size0.y)
        self._pos = vec2d(x, y).floor()

    pos = property(pos_get, pos_set)


# Entities
class Entity():
    """Base class for all game entities."""
    def __init__(self, engine: Engine):
        self.engine = engine

    def update_early(self, pause: bool):
        """Update called first."""
        pass

    def update(self, pause: bool):
        """Update called second."""
        pass

    def update_late(self, pause: bool):
        """Update called last."""
        pass

    def draw(self, draw: Draw):
        """Draw called in between back and foreground."""
        pass

class ObjJukeBox(Entity):
    """Responsible for sick beats."""
    def __init__(self, engine: Engine, key: int, name: str, data: dict):
        super().__init__(engine)
        engine.obj.instantiate_object(key, self)
        self.key = key
        self.name = name
        self.data = data

        # Music vars
        current_music = engine.aud.music.get_current()
        self.music = data['name']
        self.loops = data['loops']
        self.volume = data['volume']

        if self.music is not None: # Add new music
            if current_music is None: # Start playing music
                engine.aud.music.load(self.music)
                engine.aud.music.set_volume(self.volume)
                engine.aud.music.play(self.loops)

            elif current_music != self.music: # Queue up music
                engine.aud.music.stop(1500)
                engine.aud.music.queue(self.music, self.loops, self.volume)

        elif current_music is not None: # Fade music
            engine.aud.music.stop(1000)

    def update(self, paused: bool):
        if paused:
            if not self.engine.aud.music.paused:
                self.engine.aud.music.pause()
        else:
            if self.engine.aud.music.paused:
                self.engine.aud.music.resume()

class ObjMainMenu(Entity):
    def __init__(self, engine: Engine, key: int, name: str, data: dict):
        engine.obj.instantiate_object(key, self)
        super().__init__(engine)
        self.key = key
        self.name = name
        self.data = data

        # Title menu
        self.title_menu = Menu(engine, SIZE)

        # TITLE
        title = MenuText(engine, self.title_menu, 'title')
        title.size = 36
        title.color = (144, 240, 240)
        title.text = 'Game-X: Now with depth!'
        title.pos = SIZE / 2
        title.font = 'consolas'
        title.center = 5

        # START BUTTON
        start_button = MenuButtonFull(engine, self.title_menu, 'start-button')
        start_button.size = vec2d(128, 32)
        start_button.pos = SIZE / 2 + vec2d(0, 32)
        start_button.center = 5

        start_button.text.color = (128, 200, 200)
        start_button.text.text = 'Start'
        start_button.text.font = 'consolas'
        start_button.text.depth = 16

        start_button.button.call = self.pressed

        # OPTION BUTTON
        option_button = MenuButtonFull(engine, self.title_menu, 'option-button')
        option_button.size = vec2d(128, 32)
        option_button.pos = SIZE/2 + vec2d(0, 64)
        option_button.center = 5

        option_button.text.color = (128, 200, 200)
        option_button.text.text = 'Options'
        start_button.text.font = 'consolas'
        option_button.text.depth = 16

        option_button.button.call = self.pressed

        # QUIT BUTTON
        quit_button = MenuButtonFull(engine, self.title_menu, 'quit-button')
        quit_button.size = vec2d(128, 32)
        quit_button.pos = SIZE/2 + vec2d(0, 96)
        quit_button.center = 5

        quit_button.text.color = (128, 200, 200)
        quit_button.text.text = 'Quit'
        quit_button.text.font = 'consolas'
        quit_button.text.depth = 16

        quit_button.button.call = self.pressed

        # Option menu
        self.option_menu = Menu(self.engine, SIZE)
        self.option_menu.visible = False

        # TITLE
        title = MenuText(engine, self.option_menu, 'title')
        title.size = 24
        title.pos = SIZE / 2
        title.text = 'Options:'
        title.center = 5

        # VOLUME SLIDER
        #slider_rect = MenuRect(self.option_menu, 'slider-rect')
        #size = vec2d(100, 24)
        #pos += vec2d(-50, 12)
        #color = (64, 64, 64)
        #slider_rect.set_vars(size=size, pos=pos, color=color)

        #slider_button = MenuButton(self.option_menu, 'slider-button')
        #slider_button.set_vars(size=size, pos=pos, call=call, held=True)

        # RETURN Button
        return_button = MenuButtonFull(engine, self.option_menu, 'return-button')
        return_button.pos = SIZE/2 + vec2d(0, 128)
        return_button.center = 5
        return_button.size = vec2d(128, 24)

        return_button.text.text = 'Return'
        return_button.text.color = (128, 128, 128)
        return_button.text.depth = 16

        return_button.button.call = self.pressed

    def update(self, pause: bool):
        self.title_menu.get('start-button').update()
        self.title_menu.get('option-button').update()
        self.title_menu.get('quit-button').update()
        #self.option_menu.get('slider-button').update()
        self.option_menu.get('return-button').update()

    def draw(self, draw: Draw):
        self.title_menu.draw(draw)
        self.option_menu.draw(draw)

    def pressed(self, element: MenuElement, pos: vec2d):
        if element.name == 'start-button-button':
            self.engine.lvl.load('level1')
        elif element.name == 'option-button-button':
            self.title_menu.visible = False
            self.option_menu.visible = True
        elif element.name == 'return-button-button':
            self.title_menu.visible = True
            self.option_menu.visible = False
        elif element.name == 'quit-button-button':
            self.engine.end()
        if element.name == 'slider-button':
            x = floor(pos.x)
            x = f_limit(x, 0, 100)
            size = vec2d(x, 24)
            self.option_menu.get('slider-rect').set_vars(size=size)


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
    def __init__(self, game: Engine, key: int, pos: vec2d,
                 size: vec2d, name: str, data: dict):
        # Game object initialization
        super().__init__(game, key, pos, size, name)
        self.data = data

        # Add dynamic collider
        game.col.dy.add(key, self)

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

        # Audio
        try:
            game.aud.sfx.tracks['boop.wav']
        except KeyError:
            game.aud.sfx.add('boop.wav')

    def update(self, paused: bool):
        """Called every frame for each game object."""
        self._get_inputs()
        if self.key['pause']:
            self.engine.pause()
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
        draw.add(16, pos=self.pos, surface=image.copy())
        for item in range(1, len(self.trail)):
            image.set_alpha(((image.get_alpha() + 1) // 2) - 1)
            draw.add(15, pos=self.trail[item], surface=image.copy())

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



# Main application functions
def main(debug: bool = False):
    # Create engine object
    engine = Engine(FULLTILE, FPS, SIZE, debug)
    engine.init_obj(create_objects)#, 255)
    cam = View(SIZE)
    engine.set_cam(cam)

    # Load main menu
    engine.lvl.load('mainmenu')
    gameplay_mode(engine)

def gameplay_mode(engine: Engine):
    clock = Clock()
    if engine.debug:
        engine.debug.time_record = {
            'Update': 0.0,
            'Draw': 0.0,
            'Render': 0.0}

    while engine.run:
        # Event handler
        event_handle(engine)

        # Updating
        update(engine)
        update_debug(engine, clock)

        # Drawing
        draw(engine)

        # Rendering
        render(engine)

        # Maintain FPS
        clock.tick(FPS)
        if engine.debug:
            engine.debug.tick()

def event_handle(engine: Engine):
    """Handles events."""
    engine.inp.reset()
    events = get_events()
    for event in events:
        if event.type == KEYDOWN:
            #print(event.scancode)
            pass
        engine.inp.handle_events(event)
        if event.type == QUIT:
            engine.end()
            return
    #if engine.inp.kb.get_key_pressed(41):
    #    engine.end()
    #    return

def update(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.obj.update_early()
    engine.obj.update()
    engine.obj.update_late()
    if engine.debug:
        engine.debug.time_record['Update'] += (time() - t)

def update_debug(engine: Engine, clock: Clock):
    debug = engine.debug
    if debug:
        fps = debug.menu.get('fps')
        fps.text = 'fps: {:.0f}'.format(clock.get_fps())

        campos = debug.menu.get('campos')
        campos.text = 'cam pos: {}'.format(engine.cam.pos)

        memory = debug.menu.get('memory')
        mem = PROCESS.memory_info().rss
        mb = mem // (10**6)
        kb = (mem - (mb * 10**6)) // 10**3
        memory.text = 'memory: {} MB, {} KB'.format(mb, kb)

def draw(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.draw.draw()
    if engine.debug:
        engine.debug.menu.draw(engine.draw)
        engine.debug.time_record['Draw'] += (time() - t)

def render(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.win.blank()
    engine.cam.blank()
    engine.draw.render(engine.cam)
    engine.win.render(engine.cam)
    engine.win.update()
    if engine.debug:
        engine.debug.time_record['Render'] += (time() - t)



# Run main
if __name__ == '__main__':
    main(debug=True)
