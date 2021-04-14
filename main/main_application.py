from os import path
from math import floor
import numpy as np

from pygame import image, event as pyevent
from pygame.time import Clock
from pygame.locals import QUIT

from engine.components.camera import ObjCamera
from engine.engine import GameHandler, f_loop
from engine.helper_functions.tuple_functions import f_tupadd, f_tupgrid

FULLTILE = 32
FPS = 60

PATH = {}
PATH['DEFAULT'] = __file__[:-len(path.basename(__file__))]
PATH['ASSETS'] = path.join(PATH['DEFAULT'], 'assets')
PATH['SPRITES'] = path.join(PATH['ASSETS'], 'sprites')
PATH['LEVELS'] = path.join(PATH['ASSETS'], 'levels')
PATH['TILEMAPS'] = path.join(PATH['ASSETS'], 'tilemaps')

def object_creator(**kwargs):
    name = kwargs['name']
    if name == 'player':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = GAME.obj.instantiate_key(key)
        ObjPlayer(key, pos, (FULLTILE, FULLTILE), name, data)

    elif name == 'grav-orb':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = GAME.obj.instantiate_key(key)
        GravOrb(key, pos, (FULLTILE, FULLTILE), name, data)

    elif name == 'door':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = GAME.obj.instantiate_key(key)
        Door(key, pos, (FULLTILE, FULLTILE), name, data)

    elif name == 'button':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = GAME.obj.instantiate_key(key)
        Button(key, pos, (FULLTILE, FULLTILE/8), name, data)

    elif name == 'spike':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = GAME.obj.instantiate_key(key)
        Spike(key, pos, (FULLTILE, FULLTILE/8), name, data)

    elif name == 'wall':
        pos = kwargs['pos']
        GAME.collider.st.add(pos)


# Gameplay objects
class GameObject():
    """Class which all game objects inherit from."""
    def __init__(self, key, pos, size, relative=(0, 0)):
        self.key = key
        self.pos = pos
        self.size = size
        origin = relative
        GAME.obj.instantiate_object(key, self)
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
        """Get frame property."""
        return self._frame

    @frame.setter
    def frame(self, frame: int):
        """Set frame property."""
        if frame > len(self.frames):
            frame = f_loop(frame, 0, len(self.frames))
        self._frame = frame

    @property
    def frames(self):
        """Get frames property."""
        return self._frames

    @frames.setter
    def frames(self, fnames):
        """Set frame property."""
        self._frames = []
        for file in fnames:
            file_path = path.join(PATH['SPRITES'], file)
            self._frames.append(image.load(file_path).convert_alpha())

    def scollide(self, pos=None, cpoints=None):
        """Check to see if any of the colpoints instersect with STCOL."""
        # Match unspecified arguments
        if pos is None:
            pos = self.pos
        if cpoints is None:
            cpoints = self.cpoints

        # Check for collisions
        for point in cpoints:
            if GAME.collider.st.get(f_tupadd(pos, point)):
                return 1
        return 0

    def dcollide(self, key=None):
        """Check to see if crect intersects with any dynamic colliders.
           Set key to -1 if you want to include self in collision"""
        # Match unspecified arguments
        if key is None:
            key = self.key
        pos = self.pos
        crect = self.crect

        # Check for collision
        return GAME.collider.dy.get_collision(pos, crect, key)

    def draw_early(self, window):
        """Drawing before the background layer."""
        pass

    def draw(self, window):
        """Drawing at the same time as other objects."""
        pos = self.pos
        window.draw_image(pos, self.frames[self.frame])

    def draw_late(self, window):
        """Drawing after foreground layer."""
        pass

    def delete(self):
        """Called when object is deleted from Objects dictionary."""
        GAME.obj.delete(self.key)
        GAME.collider.dy.remove(self.key)

class ObjPlayer(GameObject):
    """Player game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data

        # Dynamic collision
        GAME.collider.dy.add(self.key, self)

        # Color
        self.color = (64, 160, 160)

        # Keys
        self.keys = {
            'jump': (44, 26, 82),
            'left': (4, 80),
            'right': (7, 79),
            'run':(225, 224)
        }

        # Key vars
        self.key = {
            'jump': 0,
            'Hjump': 0,
            'Hleft': 0,
            'Hright': 0,
            'Hrun': 0
        }

        # Ground
        self.hspd, self.vspd = 0, 0
        self.walk_speed = 0.60
        self.run_speed = 1.25
        self.ground_fric_static = 0.48
        self.ground_fric_dynamic = 0.88

        # Jumping
        self.jump = 0
        self.air_fric_retro = 0.88
        self.air_fric_pro = 0.98
        self.air_speed = 0.4
        self.jump_speed = 10
        self.default_grav = 1.2
        self.grav = self.default_grav
        self.fallgrav = 0.6
        self.jumpgrav = 0.35
        self.grounded = 0
        self.coyote = 8
        self.jump_lenience = 6
        self.jump_delay = 0

        # State Machine
        self.mode = 0

        # Sprite
        self.frames = ('player.png',)

    def update(self, dt):
        """Called every frame for each game object."""
        self.get_inputs()
        if self.mode == 0:
            self.movement()

    def draw(self, window):
        """Drawing at the same time as other objects."""
        pass

    def draw_late(self, window):
        """Called every frame to draw each game object."""
        super().draw(window)
        text = 'Grounded: {}'.format(self.grounded)
        color = (255, 255, 255)
        font = GAME.font.get('arial', 12)
        window.draw_text((FULLTILE, 1.5*FULLTILE), text, font, color)
        text = 'speed: ({:.3f}, {:.3f})'.format(self.hspd, self.vspd)
        window.draw_text((FULLTILE, 2*FULLTILE), text, font, color)

    def get_inputs(self):
        for key in self.key:
            if key[0] != 'H':
                self.key[key] = GAME.input.kb.get_key_pressed(*self.keys[key])
            else:
                self.key[key] = GAME.input.kb.get_key_held(*self.keys[key[1:]])

        #for key in self.mkey:
        #    if key[0] != 'H':
        #        self.mkey[key] = GAME.input.ms.get_button_pressed(*self.mkeys[key])
        #    else:
        #        self.mkey[key] = GAME.input.ms.get_button_held(*self.mkeys[key[1:]])

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

        # Vertical speed
        # Jumping
        if self.grounded != 0 and self.key['jump'] > 0 and self.jump_delay == 0:
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

        # Collision
        self.main_collision()

        # Update position
        self.pos = f_tupadd(self.pos, (self.hspd, self.vspd))

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

class Button(GameObject):
    """Button game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size, relative=(0, FULLTILE-size[1]))
        self.name = name
        self.data = data
        self.door = data[0]
        self.frames = ('button0.png', 'button1.png')

    def update(self, dt):
        """Called every frame for each game object."""
        if self.frame == 0:
            col = self.dcollide()
            for obj in col:
                if obj.name == 'player':
                    self.frame = 1
                    GAME.obj.obj[self.door].frame = 1

class Door(GameObject):
    """Door game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data
        self.next_level = data[0]

        # Images
        self.frames = ('door0.png', 'door1.png')

    def update(self, dt):
        """Called every frame for each game object."""
        if self.frame == 1:
            col = self.dcollide()
            for obj in col:
                if obj.name == 'player':
                    GAME.level.load(self.next_level)

class GravOrb(GameObject):
    """GravOrb game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data

        # Images
        self.frames = ('grav-orb.png',)

    def update(self, dt):
        """Called every frame for each game object."""
        col = self.dcollide()
        for obj in col:
            if obj.name == 'player':
                grav_mult = self.data[0]

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

class Spike(GameObject):
    """Spike game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size, relative=(0, FULLTILE-size[1]))
        self.name = name
        self.data = data

        # Images
        self.frames = ('spike.png',)

    def update(self, dt):
        """Called every frame for each game object."""
        col = self.dcollide()
        for obj in col:
            if obj.name == 'player':
                GAME.level.reset()


def main():
    """Main game loop."""
    clock = Clock()
    dt = 1

    while GAME.run:
        GAME.input.reset()

        # Event Handler
        for event in pyevent.get():
            # Exit game
            if event.type == QUIT:
                return
            else:
                GAME.input.handle_events(event)

        # Quit by escape
        if GAME.input.kb.get_key_pressed(41):
            GAME.end()
            return

        # Update objects
        GAME.obj.update(dt)

        # Draw all
        CAM.blank()

        # Draw background layers
        GAME.obj.draw_early(CAM)
        GAME.tile.layers['background'].draw(CAM)

        # Draw objects
        GAME.obj.draw(CAM)
        #GAME.collider.st.debug_draw(CAM)

        # Draw foreground layers
        GAME.tile.layers['foreground'].draw(CAM)
        GAME.obj.draw_late(CAM)

        # FPS display
        fps = 'fps: {:3f}'.format(clock.get_fps())
        font = GAME.font.get('arial', 12)
        CAM.draw_text((FULLTILE, FULLTILE), fps, font, (255, 255, 255))

        # Render to screen
        GAME.window.render(CAM)

        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)


if __name__ == '__main__':
    SIZE = (1024, 768)
    CAM = ObjCamera(SIZE)
    GAME = GameHandler(SIZE, FULLTILE, PATH, object_creator)
    GAME.tile.add_tilemap('0-tileset0.png')
    GAME.tile.add_tilemap('1-background0.png')
    GAME.level.load('level1')
    main()

