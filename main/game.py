"""game.py dev project."""
# pylint: disable=no-member
# pylint: disable=no-name-in-module
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=unnecessary-pass
# pylint: disable=too-many-branches

# Imports
import os
from math import floor
import ast

import pygame
import numpy as np
from pygame.locals import (QUIT, KEYUP, KEYDOWN, MOUSEBUTTONDOWN,
                           MOUSEBUTTONUP, MOUSEMOTION)

from Helper_Functions.inputs import ObjKeyboard, ObjMouse
from Helper_Functions.tuple_functions import f_tupadd, f_tupmult, f_tupround
from Helper_Functions.file_system import ObjFile
from Helper_Functions.collisions import f_col_rects

from engine import Game
from engine import f_swatch, f_loop, f_limit

# initialize pygame modules
pygame.font.init()


# Constants variables
FULLTILE = 32
HALFTILE = int(FULLTILE/2)
LEVEL_SIZE = (32, 24)
SIZE = f_tupmult(LEVEL_SIZE, FULLTILE)
FPS = 60

# File paths
PATH = {}
PATH['DEFAULT'] = __file__[:-len(os.path.basename(__file__))]
PATH['ASSETS'] = os.path.join(PATH['DEFAULT'], 'Assets')
PATH['SPRITES'] = os.path.join(PATH['ASSETS'], 'Sprites')
PATH['LEVELS'] = os.path.join(PATH['ASSETS'], 'Levels')
PATH['TILEMAPS'] = os.path.join(PATH['ASSETS'], 'Tilemaps')


# Object creator
def f_create_object(name: str, pos: tuple, key: int, data: list):
    if name != 'null':
        # Object creation
        if name == 'wall':
            GAME.STCOL.add_wall(pos)

        elif name == 'player':
            key = GAME.OBJ.instantiate_key(key)
            obj = Player(key, pos, (FULLTILE, FULLTILE), name, data)
            GAME.OBJ.instantiate_object(key, obj)

        elif name == 'button':
            key = GAME.OBJ.instantiate_key(key)
            obj = Button(key, pos, (FULLTILE, FULLTILE/8), name, data)
            GAME.OBJ.instantiate_object(key, obj)

        elif name == 'door':
            key = GAME.OBJ.instantiate_key(key)
            obj = Door(key, pos, (FULLTILE, FULLTILE), name, data)
            GAME.OBJ.instantiate_object(key, obj)

        elif name == 'grav-orb':
            key = GAME.OBJ.instantiate_key(key)
            obj = GravOrb(key, pos, (FULLTILE, FULLTILE), name, data)
            GAME.OBJ.instantiate_object(key, obj)

        elif name == 'spike':
            key = GAME.OBJ.instantiate_key(key)
            obj = Spike(key, pos, (FULLTILE, FULLTILE/8), name, data)
            GAME.OBJ.instantiate_object(key, obj)

# Gameplay objects
class GameObject():
    """Class which all game objects inherit from."""
    def __init__(self, key, pos, size, relative=(0, 0)):
        self.key = key
        self.pos = pos
        self.size = size
        origin = relative
        width, height = f_tupadd(size, -1)
        self.cpoints = ((origin[0], origin[1]),
                        (origin[0]+width, origin[1]),
                        (origin[0]+width, origin[1]+height),
                        (origin[0], origin[1]+height))
        self.crect = ((origin[0], origin[0]+width),
                      (origin[1], origin[1]+height))
        self._frame = 0
        self._frames = []

    def get_frame(self):
        """Get frame property."""
        return self._frame
    def set_frame(self, frame: int):
        """Set frame property."""
        if frame > len(self.frames):
            frame = f_loop(frame, 0, len(self.frames))
        self._frame = frame
    frame = property(get_frame, set_frame)

    def get_frames(self):
        """Get frames property."""
        return self._frames
    def set_frames(self, overwrite: bool, *fnames):
        """Set frame property."""
        if overwrite:
            self._frames = []
        for file in fnames:
            file_path = os.path.join(GAME.SPRITE_PATH, file)
            self._frames.append(pygame.image.load(file_path).convert_alpha())
    frames = property(get_frames)

    def scollide(self, pos=None, cpoints=None):
        """Check to see if any of the colpoints instersect with STCOL."""
        # Match unspecified arguments
        if pos is None:
            pos = self.pos
        if cpoints is None:
            cpoints = self.cpoints

        # Check for collisions
        for point in cpoints:
            if GAME.STCOL.get_col(f_tupadd(pos, point)):
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
        return GAME.DYCOL.get_collision(pos, crect, key)

    def render_early(self, window):
        """Rendering before the background layer."""
        pass

    def render(self, window):
        """Rendering at the same time as other objects."""
        pos = self.pos
        window.draw_image(self.frames[self.frame], pos)

    def render_late(self, window):
        """Rendering after foreground layer."""
        pass

    def delete(self):
        """Called when object is deleted from Objects dictionary."""
        GAME.OBJ.delete(self.key)
        GAME.DYCOL.remove_collider(self.key)

class Player(GameObject):
    """Player game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data

        # Dynamic collision
        GAME.DYCOL.add_collider(self.key, self)

        # Color
        self.color = f_swatch((2, 5, 5))

        # Keys
        self.jump_keys = (44, 26, 82)
        self.jump_key = 0
        self.left_keys = (4, 80)
        self.left_key = 0
        self.right_keys = (7, 79)
        self.right_key = 0
        self.run_keys =  (225, 224)

        # Ground
        self.hspd, self.vspd = 0, 0
        self.walk_speed = 0.60
        self.run_speed = 1.25
        self.ground_fric_static = 0.48
        self.ground_fric_dynamic = 0.88

        # Jumping
        self.air_fric_retro = 0.88
        self.air_fric_pro = 0.98
        self.air_speed = 0.4
        self.jump_speed = 10
        self.default_grav = 1.2
        self.grav = self.default_grav
        self.fallgrav = 0.6
        self.jumpgrav = 0.35
        self.grounded = 0
        self.coyote = 10
        self.jump_lenience = 5
        self.jump_delay = 0

        # State Machine
        self.mode = 0

        # Rendering
        self.set_frames(0, 'player.png')

    def update(self, dt):
        """Called every frame for each game object."""
        self.get_inputs()
        if self.mode == 0:
            self.movement()

    def render(self, window):
        """Rendering at the same time as other objects."""
        pass

    def render_late(self, window):
        """Called every frame to render each game object."""
        super().render(window)
        text = 'Grounded: {}'.format(self.grounded)
        window.draw_text((FULLTILE, 1.5*FULLTILE), text, color=f_swatch((7, 7, 7)))
        text = 'speed: ({:.3f}, {:.3f})'.format(self.hspd, self.vspd)
        window.draw_text((FULLTILE, 2*FULLTILE), text, color=f_swatch((7, 7, 7)))

    def get_inputs(self):
        """Get all of the inputs read before moving."""
        # Grounded
        self.grounded -= np.sign(self.grounded)
        if self.grav >= 0 and self.scollide(f_tupadd(self.pos, (0, 1))):
            if self.grav != 0:
                self.grounded = self.coyote # Normal Gravity
            else:
                self.grounded = 1
        if self.grav <= 0 and self.scollide(f_tupadd(self.pos, (0, -1))):
            if self.grav != 0:
                self.grounded = -self.coyote # Normal Gravity
            else:
                self.grounded = -1

        # Jumping
        self.jump_key -= 1
        if (GAME.KEYBOARD.get_key_pressed(*self.jump_keys)
            and self.jump_key <= 0):
            self.jump_key = self.jump_lenience
        self.jump_hold_key = GAME.KEYBOARD.get_key_held(*self.jump_keys)
        self.jump_key = f_limit(self.jump_key, 0, self.jump_lenience)

        # Horizontal controls
        self.left_key = GAME.KEYBOARD.get_key_held(*self.left_keys)
        self.right_key = GAME.KEYBOARD.get_key_held(*self.right_keys)
        self.run_key = GAME.KEYBOARD.get_key_held(*self.run_keys)

    def movement(self):
        """Handle player movement."""
        # Horizontal speed
        move = (self.right_key - self.left_key)
        if self.grounded and self.grav != 0:
            if move != 0:
                # Dynamic grounded
                self.hspd *= self.ground_fric_dynamic

                # Running
                if self.run_key:
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
        if self.grounded != 0 and self.jump_key > 0 and self.jump_delay == 0:
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
        elif self.jump_hold_key:
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

        # Rendering
        self.set_frames(0, 'button0.png', 'button1.png')

    def update(self, dt):
        """Called every frame for each game object."""
        if self.frame == 0:
            col = self.dcollide()
            for obj in col:
                if obj.name == 'player':
                    self.frame = 1
                    GAME.OBJ.obj[self.door].frame = 1

    def get_collision_self(self, pos, size):
        """See if object is pressing button."""
        bdom = [self.pos[0], self.pos[0] + self.size[0]-1]
        bran = [self.pos[1], self.pos[1] + self.size[1]-1]
        cdom = [pos[0], pos[0] + size[0]-1]
        cran = [pos[1], pos[1] + size[1]-1]
        return f_col_rects(bdom, bran, cdom, cran)

class Door(GameObject):
    """Door game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data
        self.next_level = data[0]

        # Images
        self.set_frames(0, 'door0.png', 'door1.png')

    def update(self, dt):
        """Called every frame for each game object."""
        if self.frame == 1:
            col = self.dcollide()
            for obj in col:
                if obj.name == 'player':
                    GAME.LEVEL.load_level(self.next_level)

    def get_collision_self(self, pos, size):
        """See if object is pressing button."""
        bdom = [self.pos[0], self.pos[0] + self.size[0]-1]
        bran = [self.pos[1], self.pos[1] + self.size[1]-1]
        cdom = [pos[0], pos[0] + size[0]-1]
        cran = [pos[1], pos[1] + size[1]-1]
        return f_col_rects(bdom, bran, cdom, cran)

class GravOrb(GameObject):
    """GravOrb game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data

        # Images
        self.set_frames(0, 'grav-orb.png')

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
        self.set_frames(0, 'spike0.png')

    def update(self, dt):
        """Called every frame for each game object."""
        col = self.dcollide()
        for obj in col:
            if obj.name == 'player':
                GAME.LEVEL.reset()


# Main code section
def main():
    """Main game loop."""
    clock = pygame.time.Clock()
    run = True
    dt = 1

    # Gameplay loop
    while GAME.run:
        GAME.input_reset()

        # Event Handler
        for event in pygame.event.get():
            # Exit game
            if event.type == QUIT:
                GAME.end()
            else:
                GAME.handle_events(event)

        # Quit by escape
        if GAME.KEYBOARD.get_key_pressed(41):
            GAME.end()

        # Update objects
        GAME.update(dt)

        # Render
        GAME.render()

        # FPS display
        fps = 'fps: {:3f}'.format(clock.get_fps())
        GAME.WIN.draw_text((FULLTILE, FULLTILE), fps, color=f_swatch((7, 7, 7)))

        # Update display
        pygame.display.update()

        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)

    pygame.quit()

if __name__ == "__main__":
    # Constant objects
    GAME = Game(SIZE, LEVEL_SIZE, FULLTILE, PATH, f_create_object)

    # Setup program
    pygame.event.set_allowed([QUIT, KEYUP, KEYDOWN, MOUSEBUTTONDOWN,
                        MOUSEBUTTONUP, MOUSEMOTION])
    pygame.display.set_caption("Game X")
    GAME.TILE.load()

    GAME.load_level('level0')

    main()
