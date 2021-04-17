import sys
from os import path, getcwd
from math import floor
import numpy as np
from time import time

from pygame import image, event as pyevent
from pygame.time import Clock
from pygame.locals import QUIT

from .engine.components.camera import ObjCamera
from .engine.engine import GameHandler, f_loop, f_limit
from .engine.helper_functions.tuple_functions import (
    f_tupadd, f_tupgrid, f_tupmult)
from .engine.helper_functions.file_system import ObjFile

FULLTILE = 32
FPS = 60
SIZE = (1024, 768)

PATH = {}
PATH['MAIN'] = getcwd()
PATH['ASSETS'] = path.join(PATH['MAIN'], 'assets')
PATH['SPRITES'] = path.join(PATH['ASSETS'], 'sprites')
PATH['LEVELS'] = path.join(PATH['ASSETS'], 'levels')
PATH['TILEMAPS'] = path.join(PATH['ASSETS'], 'tilemaps')

def object_creator(**kwargs):
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

class ObjView(ObjCamera):
    def __init__(self, size):
        super().__init__(size)

    def set_level_size(self, size):
        self.level_size = size

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        level_size0, level_size1 = self.level_size
        size0, size1 = self._size
        value0 = f_limit(value[0], 0, level_size0 - size0)
        value1 = f_limit(value[1], 0, level_size1 - size1)
        self._pos = (value0, value1)

# Gameplay objects
class GameObject():
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

    def set_frames(self, *fnames, alpha=0):
        """Set frame property."""
        self._frames = []
        for file in fnames:
            file_path = path.join(PATH['SPRITES'], file)
            if alpha == 0:
                self._frames.append(image.load(file_path).convert())
            elif alpha == 1:
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
            if self.game.collider.st.get(f_tupadd(pos, point)):
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
        return self.game.collider.dy.get_collision(pos, crect, key)

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
        self.game.obj.delete(self.key)
        self.game.collider.dy.remove(self.key)

class ObjPlayer(GameObject):
    """Player game object."""
    def __init__(self, game, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(game, key, pos, size)
        self.name = name
        self.data = data
        self.game = game
        game.collider.dy.add(key, self)

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
        self.campos = (0, 0)

        # Sprite
        self.set_frames('player.png')

    def update(self, dt, **kwargs):
        """Called every frame for each game object."""
        self.get_inputs()
        if self.mode == 0:
            self.movement()
            self.campos = f_tupadd(self.pos, f_tupmult(self.game.cam._size, -1/2))
            self.game.cam.pos = self.campos
            col = self.dcollide()
            for obj in col:
                try:
                    obj.collide(self)
                except AttributeError:
                    pass

    def draw(self, window):
        """Drawing at the same time as other objects."""
        pass

    def draw_late(self, window):
        """Called every frame to draw each game object."""
        super().draw(window)
        text = 'Grounded: {}'.format(self.grounded)
        color = (255, 255, 255)
        font = self.game.font.get('arial', 12)
        window.draw_text((FULLTILE, 1.5*FULLTILE), text, font, color, gui = 1)
        text = 'speed: ({:.3f}, {:.3f})'.format(self.hspd, self.vspd)
        window.draw_text((FULLTILE, 2*FULLTILE), text, font, color, gui = 1)

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

class ObjButton(GameObject):
    """Button game object."""
    def __init__(self, game, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(game, key, pos, size, relative=(0, FULLTILE-size[1]))
        self.game = game
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data
        self.set_frames('button0.png', 'button1.png', alpha=1)

    def update(self, dt, **kwargs):
        """Called every frame for each game object."""
        pass

    def collide(self, obj):
        self.door = self.game.obj.obj[self.data[0]]
        self.frame = 1
        self.door.frame = 1

class ObjDoor(GameObject):
    """Door game object."""
    def __init__(self, game, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(game, key, pos, size)
        self.game = game
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data
        self.next_level = data[0]

        # Images
        self.set_frames('door0.png', 'door1.png')

    def update(self, dt, **kwargs):
        """Called every frame for each game object."""
        pass

    def collide(self, obj):
        if obj.name == 'player':
            if self.frame == 1:
                self.game.level.load(self.next_level)

class ObjGravOrb(GameObject):
    """GravOrb game object."""
    def __init__(self, game, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(game, key, pos, size)
        self.game = game
        game.collider.dy.add(key, self)
        self.name = name
        self.data = data

        # Images
        if self.data[0] > 0:
            self.set_frames('grav-orb0.png', alpha=1)
        elif self.data[0] == 0:
            self.set_frames('grav-orb1.png', alpha=1)
        elif self.data[0] < 1:
            self.set_frames('grav-orb2.png', alpha=1)

    def update(self, dt, **kwargs):
        """Called every frame for each game object."""
        pass

    def collide(self, obj):
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

class ObjSpike(GameObject):
    """Spike game object."""
    def __init__(self, game, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(game, key, pos, size, relative=(0, FULLTILE-size[1]))
        self.game = game
        self.name = name
        self.data = data
        game.collider.dy.add(key, self)

        # Images
        self.set_frames('spike.png', alpha=1)

    def update(self, dt, **kwargs):
        pass

    def collide(self, obj):
        if obj.name == 'player':
            self.game.level.reset()

class ObjSpikeInv(GameObject):
    """Spike game object."""
    def __init__(self, game, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(game, key, pos, size, relative=(0, 0))
        self.game = game
        self.name = name
        self.data = data
        game.collider.dy.add(key, self)

        # Images
        self.set_frames('spike-inv.png', alpha=1)

    def update(self, dt, **kwargs):
        pass

    def collide(self, obj):
        if obj.name == 'player':
            self.game.level.reset()


def main():
    """Main game loop."""
    camera = ObjView(SIZE)
    GAME = GameHandler(SIZE, FULLTILE, PATH, object_creator)
    GAME.cam = camera
    GAME.tile.add_tilemap('0-tileset0.png')
    GAME.tile.add_tilemap('1-background0.png')
    GAME.level.load('level1')

    # Timing info
    clock = Clock()
    dt = 1
    #STARTTIME = time()
    #TIME = []

    # Append new line to debug file
    #debug = ObjFile(path.join(PATH['MAIN'], 'debug'), 'debug.txt')
    #debug.append()
    #debug.file.write('\n\n\n')
    #debug.close
    #del debug

    while GAME.run:
        GAME.input.reset()

        # Event Handler
        for event in pyevent.get():
            # Exit GAME
            if event.type == QUIT:
                return
            else:
                GAME.input.handle_events(event)

        # Quit by escape
        if GAME.input.kb.get_key_pressed(41):
            GAME.end()
            return

        # Update objects
        t = time()
        GAME.obj.update(dt)
        #TIME.append(round((time() - t), 3))

        # Draw all
        t = time()
        # Draw background layers
        GAME.obj.draw_early(GAME.cam)
        GAME.tile.layers['background'].draw(GAME.cam)

        # Draw objects
        GAME.obj.draw(GAME.cam)

        # Draw foreground layers
        GAME.tile.layers['foreground'].draw(GAME.cam)
        GAME.obj.draw_late(GAME.cam)

        # FPS display
        fps = 'fps: {:3f}'.format(clock.get_fps())
        font = GAME.font.get('arial', 12)
        GAME.cam.draw_text((FULLTILE, FULLTILE), fps, font, (255, 255, 255), gui = 1)

        # Render to screen
        GAME.window.render(GAME.cam)
        #TIME.append(round((time() - t), 3))

        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)

        # Write render data to disk
        #if len(TIME) >= 5*2*FPS:
        #    #print('writing time data to disk')
        #    debug = ObjFile(path.join(PATH['MAIN'], 'debug'), 'debug.txt')
        #    debug.append()
        #    t0 = 0
        #    t1 = 1
        #    for i in range(200):
        #        t0 += TIME[2*i]
        #        t1 += TIME[2*i+1]
        #    debug.file.write('###\n')
        #    debug.file.write('time: {:.3f}\n'.format(time()-STARTTIME))
        #    debug.file.write('update: {:.3f}\n'.format(t0))
        #    debug.file.write('render: {:.3f}\n'.format(t1))
        #    debug.close()
        #    TIME.clear()


if __name__ == '__main__':
    main()
