##############################################################################
from os import path, getcwd, system, name as osname

# Clear terminal
if osname == 'nt':
    system('cls')
else:
    system('clear')

from math import floor
import numpy as np
from time import time
import datetime

from pygame import image, event as pyevent, Surface
from pygame.time import Clock
from pygame.locals import QUIT

# If main file
if __name__ == '__main__':
    from engine.components.camera import ObjCamera
    from engine.engine import ObjGameHandler, f_loop, f_limit
    from engine.helper_functions.tuple_functions import (
        f_tupadd, f_tupgrid, f_tupmult)
    from engine.helper_functions.file_system import ObjFile
    from engine.components.menu import (
        ObjMenu, ObjTextElement)

# If being called as a module
else:
    from .engine.components.camera import ObjCamera
    from .engine.engine import ObjGameHandler, f_loop, f_limit
    from .engine.helper_functions.tuple_functions import (
        f_tupadd, f_tupgrid, f_tupmult)
    from .engine.helper_functions.file_system import ObjFile
    from .engine.components.menu import (
        ObjMenu, ObjTextElement)

print('################')

# Constants
if True:
    SIZE = (1024, 768)
    FULLTILE = 32
    FPS = 60
    DEBUG = 0

    PATH = {}
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
        ObjPlayer(game, key, pos, (FULLTILE, FULLTILE), name, data)

    elif name == 'grav-orb':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjGravOrb(game, key, pos, (FULLTILE, FULLTILE), name, data)

    elif name == 'door':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjDoor(game, key, pos, (FULLTILE, FULLTILE), name, data)

    elif name == 'button':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjButton(game, key, pos, (FULLTILE, FULLTILE/8), name, data)

    elif name == 'spike':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjSpike(game, key, pos, (FULLTILE, FULLTILE/8), name, data)

    elif name == 'spike-inv':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjSpikeInv(game, key, pos, (FULLTILE, FULLTILE/8), name, data)

    elif name == 'juke-box':
        key = kwargs['key']
        data = kwargs['data']
        key = game.obj.instantiate_key(key)
        ObjJukeBox(game, key, name, data)



# Special classes
class ObjView(ObjCamera):
    """Camera like object which is limited to the inside of the level."""
    def set_level_size(self, size: tuple):
        """Set's the bounds of the camera."""
        self.level_size = size

    @property
    def pos(self):
        """Position getter."""
        return self._pos

    @pos.setter
    def pos(self, pos: tuple):
        """Position setter."""
        level_size0, level_size1 = self.level_size
        size0, size1 = self._size
        value0 = f_limit(pos[0], 0, level_size0 - size0)
        value1 = f_limit(pos[1], 0, level_size1 - size1)
        self._pos = f_tupgrid((value0, value1), 1)


# Entities
class Entity():
    """Base class for all game entities."""
    def draw_early(self, window: object):
        """Draw called before background."""
        pass

    def draw(self, window: object):
        """Draw called in between back and foreground."""
        pass

    def draw_late(self, window: object):
        """Draw called after foreground."""
        pass

    def update_early(self, dt: float):
        """Update called first."""
        pass

    def update(self, dt: float):
        """Update called second."""
        pass

    def update_late(self, dt: float):
        """Update called last."""
        pass

class ObjJukeBox(Entity):
    """Responsible for sick beats."""
    def __init__(self, game: object, key: int, name: str, data: dict):
        game.obj.instantiate_object(key, self)
        self.game = game
        self.key = key
        self.name = name
        self.data = data

        current_music = game.audio.music.get_current()
        self.music = data['name']
        self.loops = data['loops']
        self.volume = data['volume']

        if self.music is not None:
            if current_music is None:
                # No current music
                game.audio.music.load(self.music)
                game.audio.music.set_volume(self.volume)
                game.audio.music.play(self.loops)

            elif current_music != self.music:
                # Fade current music.
                game.audio.music.stop(1500)
                game.audio.music.queue(self.music, self.loops, self.volume)
        elif current_music != None:
            game.audio.music.stop(1000)


# Gameplay objects
class GameObject(Entity):
    """Class which all game objects inherit from."""
    def __init__(self, game, key, pos, size, relative=(0, 0)):
        self.game = game
        self.key = key
        self.pos = pos
        self.size = size
        origin = relative
        game.obj.instantiate_object(key, self)
        width, height = f_tupadd(size, -1)
        self.cpoints = ((origin[0], origin[1]),
                        (origin[0]+width, origin[1]),
                        (origin[0]+width, origin[1]+height),
                        (origin[0], origin[1]+height))
        self.crect = ((origin[0], origin[0]+width),
                      (origin[1], origin[1]+height))
        self._frame = 0
        self._frames = []

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

    @property
    def frames(self):
        """Franes getter."""
        return self._frames

    def set_frames(self, *fnames, alpha=0):
        """Frames setter."""
        self._frames = []
        for file in fnames:
            file_path = path.join(PATH['SPRITES'], file)
            if alpha == 0:
                self._frames.append(image.load(file_path).convert())
            elif alpha == 1:
                self._frames.append(image.load(file_path).convert_alpha())

    def scollide(self, pos=None, cpoints=None):
        """Check for static collisions."""
        # Match unspecified arguments
        if pos is None:
            pos = self.pos
        if cpoints is None:
            cpoints = self.cpoints

        # Check for collisions
        for point in cpoints:
            if self.game.collider.st.get(f_tupadd(pos, point)):
                return 1
        return 0

    def dcollide(self, key=None):
        """Check for dynamic collisions.
           Set key to -1 if you want to include self in collision"""
        # Match unspecified arguments
        if key is None:
            key = self.key
        pos = self.pos
        crect = self.crect

        # Check for collision
        return self.game.collider.dy.get_collision(pos, crect, key)

    def draw(self, window):
        """Draw called inbetween back and foreground."""
        pos = self.pos
        window.draw_image(pos, self.frames[self.frame])

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

        # Audio
        #try:
        #    game.audio.sfx.tracks['boop.wav']
        #except KeyError:
        #    game.audio.sfx.add('boop.wav')

    def update(self, dt):
        """Called every frame for each game object."""
        self.get_inputs()
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
            self.movement()

            # Update camera position
            cam_center = f_tupmult(self.game.cam._size, -1/2)
            self.campos = f_tupadd(self.pos, cam_center)
            dcam = f_tupadd(self.campos, f_tupmult(self.game.cam.pos, -1))
            dcam = f_tupmult(dcam, self.camspeed)
            self.game.cam.pos = f_tupadd(self.game.cam.pos, dcam)

    def draw(self, window):
        """Drawing at the same time as other objects."""
        pass

    def draw_late(self, window):
        """Called every frame to draw each game object."""
        super().draw(window)
        color = (255, 255, 255)
        font = self.game.font.get('arial', 12)
        #text = 'Grounded: {}'.format(self.grounded)
        #window.draw_text((FULLTILE, 1.5*FULLTILE), text, font, color, gui = 1)
        #text = 'speed: ({:.3f}, {:.3f})'.format(self.hspd, self.vspd)
        #window.draw_text((FULLTILE, 2*FULLTILE), text, font, color, gui = 1)
        gui = Surface(self.game.window.size)
        gui.get_width

    def get_inputs(self):
        for key in self.key:
            if key[0] != 'H':
                self.key[key] = self.game.input.kb.get_key_pressed(
                    *self.keys[key])
            else:
                self.key[key] = self.game.input.kb.get_key_held(
                    *self.keys[key[1:]])

    def movement(self):
        """Handle player movement."""
        # Veritcal controls
        self.jump -= np.sign(self.jump)
        if (self.key['jump'] and self.jump <= 0):
            self.jump = self.jump_lenience

        # Grounded
        self.grounded -= np.sign(self.grounded)

        # Floor
        if self.grav >= 0 and self.scollide(f_tupadd(self.pos, (0, 1))):
            self.jump_delay = 0
            if self.grav != 0:
                self.grounded = self.coyote # Normal Gravity
            else:
                self.grounded = 1 # Zero Gravity

        # Ceiling
        if self.grav <= 0 and self.scollide(f_tupadd(self.pos, (0, -1))):
            self.jump_delay = 0
            if self.grav != 0:
                self.grounded = -self.coyote # Normal Gravity
            else:
                self.grounded = -1 # Zero Gravity

        # Horizontal and vertical movement
        self.hmove()
        self.vmove()

        # Collision
        self.main_collision()

        # Update position
        self.pos = f_tupadd(self.pos, (self.hspd, self.vspd))

    def hmove(self):
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

    def vmove(self):
        # Vertical speed
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

    def main_collision(self):
        """Check for player collisions and correct for them."""
        pos = self.pos
        hspd, vspd = self.hspd, self.vspd
        xpos, ypos = pos[0], pos[1]
        svspd, shspd = np.sign(vspd), np.sign(hspd)

        # Horizontal collision
        if self.scollide((xpos + hspd, ypos)):
            while self.scollide((xpos + hspd, ypos)):
                hspd -= shspd
            pos = (floor(xpos + hspd), ypos)
            hspd = 0

        # Vertical collision
        if self.scollide((xpos, ypos + vspd)):
            while self.scollide((xpos, ypos + vspd)):
                vspd -= svspd
            pos = (xpos, floor(ypos + vspd))
            vspd = 0

        self.pos = pos
        self.hspd = hspd
        self.vspd = vspd

class ObjButton(GameObject):
    """Button game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size, relative=(0, FULLTILE-size[1]))
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data
        self.door_id = data['door']
        self.set_frames('button0.png', 'button1.png', alpha=1)

    def collide(self, obj: object):
        """When collided with by player, open the door."""
        if obj.name == 'player' and self.frame == 0:
            self.door = self.game.obj.obj[self.door_id]
            self.frame = 1
            self.door.frame = 1

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
        super().__init__(game, key, pos, size, relative=(0, FULLTILE-size[1]))
        self.name = name
        self.data = data
        game.collider.dy.add(key, self)

        # Images
        self.set_frames('spike.png', alpha=1)

    def collide(self, obj: object) -> str:
        if obj.name == 'player':
            self.game.level.reset()
            return 'return'

class ObjSpikeInv(GameObject):
    """Spike game object."""
    def __init__(self, game: object, key: int, pos: tuple,
                 size: tuple, name: str, data: dict):
        # GameObject initialization
        super().__init__(game, key, pos, size, relative=(0, 0))
        self.name = name
        self.data = data
        game.collider.dy.add(key, self)

        # Images
        self.set_frames('spike-inv.png', alpha=1)

    def collide(self, obj: object) -> str:
        if obj.name == 'player':
            self.game.level.reset()
            return 'return'



# Main application method
def main():
    """Main game loop."""
    GAME = ObjGameHandler(SIZE, FULLTILE, PATH, object_creator)
    GAME.cam = ObjView(SIZE)
    GAME.tile.add_tilemap('0-tileset0.png')
    GAME.tile.add_tilemap('1-background0.png')
    GAME.level.load('level1')
    GAME.parallax = 1

    # Timing info
    clock = Clock()
    dt = 1
    if DEBUG:
        STARTTIME = time()
        TIME = []

        # Debug menu
        DEBUGMENU = ObjMenu(GAME, (128, 32))
        #box = ObjRectElement(DEBUGMENU, 'back', (128, 32))
        #box.color = (0, 0, 0)
        text = ObjTextElement(DEBUGMENU, 'fps', (128, 12), backdrop=1)
        text = ObjTextElement(DEBUGMENU, 'campos', (128, 12), backdrop=1)
        text.pos = (0, 0.5*FULLTILE)

        debug = ObjFile(PATH['DEBUGLOG'], 'debug.txt')
        debug.append()
        time_date = datetime.datetime.now()
        time_date = time_date.strftime('%Y-%m-%d %Hh%M')
        debug.file.write('\n\n###### {}\n'.format(time_date))
        debug.close()
        del debug

    # Gameplay loop
    while GAME.run:
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
        if DEBUG:
            t = time()
        update(GAME, dt)
        if DEBUG:
            TIME.append(round((time() - t), 3))


        # Draw calls
        if DEBUG:
            t = time()
        draw(GAME)


        # Debug menu
        if DEBUG:
            DEBUGMENU.blank()
            element = DEBUGMENU.get('fps')
            element.text = 'fps: {:.1f}'.format(clock.get_fps())
            element = DEBUGMENU.get('campos')
            element.text = 'cam pos: ({}, {})'.format(*GAME.cam.pos)
            DEBUGMENU.draw()
            DEBUGMENU.render(GAME.cam)


        # Render to screen
        render(GAME)
        if DEBUG:
            TIME.append(round((time() - t), 3))


        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)

        # Write debug data to disk
        if DEBUG:
            if len(TIME) >= 5*2*FPS:
                #print('writing time data to disk')
                debug = ObjFile(PATH['DEBUGLOG'], 'debug.txt')
                debug.append()
                t0 = 0
                t1 = 1
                for i in range(200):
                    t0 += TIME[2*i]
                    t1 += TIME[2*i+1]
                debug.file.write('###\n')
                debug.file.write('time: {:.3f}\n'.format(time()-STARTTIME))
                debug.file.write('update: {:.3f}\n'.format(t0))
                debug.file.write('render: {:.3f}\n'.format(t1))
                debug.close()
                TIME.clear()

def update(game: object, dt: float):
    """Update call."""
    game.obj.update_early(dt)
    game.obj.update(dt)
    game.obj.update_late(dt)

def draw(game: object):
    """Draw call."""
    cam = game.cam

    # Blank screen
    game.cam.blank()
    game.obj.draw_early(cam)
    game.tile.layers['background'].draw(cam)
    game.obj.draw(game.cam)
    game.tile.layers['foreground'].draw(cam)
    game.obj.draw_late(game.cam)

def render(game: object):
    """Render textures to screen."""
    game.window.render(game.cam)


# If main file
if __name__ == '__main__':
    main()
