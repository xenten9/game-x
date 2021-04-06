"""game.py dev project."""
# pylint: disable=no-member

# Imports
import os
from math import floor, ceil
import ast

import pygame
import numpy as np

from inputs import ObjKeyboard, ObjMouse
from tuple_functions import f_tupadd, f_tupmult
from file_system import ObjFile
from collisions import f_col_rects

pygame.init()


# Constants variables
TILESIZE = 32
WIDTH, HEIGHT = 32 * TILESIZE, 24 * TILESIZE
FPS = 60

# File paths
DEFAULT_PATH = os.getcwd()
GAME_PATH = os.path.join(DEFAULT_PATH, 'game-x')
LEVEL_PATH = os.path.join(GAME_PATH, 'Levels')
ASSET_PATH = os.path.join(GAME_PATH, 'Assets')
TILEMAP_PATH = os.path.join(ASSET_PATH, 'Tilemaps')


# Helper functions
# Convert (4 bit tuples to 8 bit tuples)
def f_swatch(rgb=(0, 0, 0)) -> tuple:
    """Convers 8 bit tuple to 16 bit tuple(RGB)."""
    return f_tupadd(f_tupmult(f_tupadd(rgb, 1), 32), -1)

# Flip color
def f_cinverse(rgb=(0, 0, 0)) -> tuple:
    """Converts 16 bit tuple to its 16 bit inverse(RGB)."""
    return f_tupmult(f_tupadd((-255, -255, -255), rgb), -1)

# Return a value following packman logic
def f_loop(val, minval, maxval):
    """Returns a number that loops between the min and max
    Ex. n = 8, minval = 3, maxval = 5;
        8 is 3 more then 5
        minval + 3 = 6
        6 is 1 more then 5
        minval + 1 = 4
        minval < 4 < maxval
        return 4
    """
    if minval <= val <= maxval:
        return val
    if val <= minval:
        return maxval - (minval - val) + 1
    return minval + (val - maxval) - 1

# Return the value closest to the range min to max
def f_limit(val, minval, maxval):
    """Reutrns value n
    limits/clamps the value n between the min and max
    """
    if val < minval:
        return minval
    if val > maxval:
        return maxval
    return val

# Handle events
def f_event_handler(event):
    """Handles inputs and events."""
    # Key pressed
    if event.type == pygame.KEYDOWN:
        KEYBOARD.set_key(event.scancode, 1)

    # Key released
    elif event.type == pygame.KEYUP:
        KEYBOARD.set_key(event.scancode, 0)

    # Mouse movement
    elif event.type == pygame.MOUSEMOTION:
        MOUSE.pos = event.pos
        MOUSE.rel = f_tupadd(MOUSE.rel, event.rel)

    # Mouse pressed
    elif event.type == pygame.MOUSEBUTTONDOWN:
        MOUSE.button_pressed[event.button] = 1
        MOUSE.button_held[event.button] = 1
        MOUSE.button_pressed_pos[event.button] = event.pos

    # Mouse released
    elif event.type == pygame.MOUSEBUTTONUP:
        MOUSE.button_pressed[event.button] = 0
        MOUSE.button_held[event.button] = 0

    # Unknown event
    else:
        pass


# Handles graphics
class Window():
    """Handles graphics."""
    def __init__(self, width: int, height: int):
        self.display = pygame.display.set_mode((width, height))
        self.height, self.height = width, height
        self.fonts = {'arial12': pygame.font.SysFont('arial', 12)}

    def add_font(self, name: str, size):
        """Adds a font to WIN.fonts."""
        try:
            self.fonts[name + str(size)]
        except KeyError:
            self.fonts[name + str(size)] = pygame.font.SysFont(name, size)
            return None
        return None

    def draw_text(self, pos: tuple, text: str, font='arial12', color=(0, 0, 0)):
        """Draws text at a position in a given font and color."""
        self.display.blit(self.fonts[font].render(text, 0, color), pos)

    def draw_rect(self, pos: tuple, size=(TILESIZE, TILESIZE), color=(0, 0, 0)):
        """Draws a rectangle at a position in a given color."""
        pygame.draw.rect(self.display, color, pygame.Rect(pos, size))

    def draw_image(self, image, pos=(0, 0)):
        """Draws an image at a position."""
        self.display.blit(image, pos)

    def blank(self):
        """Blanks the screen in-between frames."""
        self.display.fill(f_swatch((7, 7, 7)))

# Handles level loading
class Level():
    def __init__(self):
        self.levels = {}

    def add_level(self, name: str):
        if os.path.exists(os.path.join(LEVEL_PATH, name)):
            self.levels[name] = name

    def load_level(self, level_name: str):
        level = ObjFile(LEVEL_PATH, level_name + '.lvl')
        level.read()
        obj_list = level.file.readlines()

        # Convert types
        for count in enumerate(obj_list):
            obj_list[count[0]] = (ast.literal_eval(obj_list[count[0]][:-1]))
            if type(obj_list[count[0]]) != list:
                obj_list[count[0]] = []

        # Close file
        level.close()

        # Clear entities
        objcopy = OBJ.obj.copy()
        for obj in objcopy:
            OBJ.delete(obj)
        STCOL.clear()

        # Create objects
        for arg in obj_list:
            # Interpret object info
            name, pos, key, data = arg[0:2] + arg[3:5]
            OBJ.create_object(name, pos, key, data)

# Handles object instances
class Objects():
    """Handles game objects."""
    def __init__(self):
        # 65535 tacked objects max
        self.pool_size = 2**16 - 1
        self.pool = {}
        for item in range(self.pool_size):
            self.pool[item] = 1
        self.obj = {}

    def instantiate(self, obj, key=None):
        """Add a ref. to a game object in the OBJ.obj dictionary."""
        if key is None:
            key = self.pool.popitem()[0]
        else:
            try:
                self.pool[key]
            except IndexError:
                print(self.pool)
                print('key ' + str(key) + ' is not in pool')
                key = self.pool.popitem()[0]
        self.obj[key] = obj
        return key

    def delete(self, key):
        """Removes a ref. of a game object from the OBJ.obj dictionary."""
        del self.obj[key]
        self.pool[key] = 1

    def create_object(self, name, pos, key=None, data=[]):
        """Loads a level into the OBJ.obj dictioanry."""
        # Object creation
        if name == 'player':
            obj = Player(pos, (TILESIZE, TILESIZE))
            self.instantiate(obj, key)

        elif name == 'wall':
            STCOL.add_wall((int(pos[0] / TILESIZE),
                            int(pos[1] / TILESIZE)))

        elif name == 'button':
            obj = Button(pos)
            self.instantiate(obj, key)
            obj.data = data

        elif name == 'door':
            obj = Door(pos)
            self.instantiate(obj, key)
            obj.data = data

# Handles static collision
class StaticCollider():
    """Handles static collisions aligned to a grid."""
    def __init__(self):
        self.grid = [[0]*32 for n in range(32)]
        self.color = f_swatch((1, 1, 1))

    def add_wall(self, pos: tuple):
        """Add a wall at a given position."""
        self.grid[pos[0]][pos[1]] = 1

    def remove_wall(self, pos: tuple):
        """Remove a wall at a given position."""
        self.grid[pos[0]][pos[1]] = 0

    def get_col(self, pos) -> bool:
        """Check for a wall at a given position."""
        pos = (floor(pos[0]/TILESIZE), floor(pos[1]/TILESIZE))
        try:
            return self.grid[pos[0]][pos[1]]
        except IndexError:
            return 0

    def clear(self):
        self.grid = [[0]*32 for n in range(32)]

    def debug_render(self):
        """Draw walls for debug purposes"""
        for column in range(len(self.grid)):
            for row in range(len(self.grid[column])):
                if self.grid[column][row]:
                    WIN.draw_rect(f_tupmult((column, row), TILESIZE),
                                  color=self.color)


# Constant objects
WIN = Window(WIDTH, HEIGHT)
OBJ = Objects()
LEVEL = Level()
STCOL = StaticCollider()
#DYCOL = DynamicCollider()
KEYBOARD = ObjKeyboard()
MOUSE = ObjMouse()
pygame.display.set_caption("Game X")

for file in os.listdir(LEVEL_PATH):
    if file[-4:] == '.lvl':
        LEVEL.add_level(file)


# Gameplay objects
class GameObject():
    """Class which all game objects inherit from."""
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        w, h = f_tupadd(size, -1)
        self.colpoints = [(0, 0),
                          (w, 0),
                          (w, h),
                          (0, h)]
        self._frame = 0
        self._frames = []

    def get_frame(self):
        return self._frame

    def set_frame(self, frame):
        if type(frame) != int:
            raise ValueError('frame ' + str(frame) + ' is not an int')
        if frame > len(self.frames):
            frame = f_loop(frame, 0, len(self.frames))
        self._frame = frame

    frame = property(get_frame, set_frame)

    def get_frames(self):
        return self._frames

    frames = property(get_frames)

    def set_frames(self, overwrite: bool, *fnames):
        if overwrite:
            self._frames = []
        for file in fnames:
            file_path = os.path.join(ASSET_PATH, file)
            self._frames.append(pygame.image.load(file_path))

    def collide(self, pos=None, colpoints=None):
        """Check to see if any of the colpoints instersect with STCOL."""
        # Match unspecified arguments
        if pos is None:
            pos = self.pos
        if colpoints is None:
            colpoints = self.colpoints

        # Check for collisions
        for point in colpoints:
            if STCOL.get_col(f_tupadd(pos, point)):
                return 1
        return 0

    def render(self, pos=None):
        if pos is None:
            pos = self.pos
        WIN.draw_image(self.frames[self.frame], pos)

# pylint: disable=too-many-instance-attributes
class Player(GameObject):
    """Player game object."""
    def __init__(self, pos, size):
        super().__init__(pos, size)

        # Color
        self.color = f_swatch((2, 5, 5))

        # Keys
        self.jump_key = 0
        self.left_key = 0
        self.right_key = 0

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
        self.grav = 1.2
        self.fallgrav = 0.6
        self.jumpgrav = 0.35
        self.grounded = 0
        self.coyote = 4

        # State Machine
        self.mode = 0

        # Rendering
        self.set_frames(0, 'player.png')

    def update(self):
        """Called every frame for each game object."""
        self.get_inputs()
        if self.mode == 0:
            self.movement()

    def render(self):
        """Called every frame to render each game object."""
        super().render()
        spd = (round(self.hspd, 1), round(self.vspd, 1))
        WIN.draw_text((TILESIZE, TILESIZE), str(spd))

    def get_inputs(self):
        """Get all of the inputs read before moving."""
        # Grounded
        self.grounded -= 1
        if self.grav >= 0 and self.collide(f_tupadd(self.pos, (0, 1))):
            self.grounded = self.coyote # Normal Gravity

        if self.grav <= 0 and self.collide(f_tupadd(self.pos, (0, -1))):
            self.grounded = self.coyote # Inverted Gravity

        # Coyote timing
        self.grounded = f_limit(self.grounded, 0, self.coyote)

        # Jumping
        self.jump_key -= 1
        if KEYBOARD.get_key_pressed(17, 72, 57) and self.jump_key <= 0:
            self.jump_key = self.coyote

        # Loose input timing
        self.jump_key = f_limit(self.jump_key, 0, self.coyote)

        # Horizontal controls
        self.left_key = KEYBOARD.get_key_held(30, 75)
        self.right_key = KEYBOARD.get_key_held(32, 77)

    def movement(self):
        """Handle player movement."""
        # Horizontal speed
        move = (self.right_key - self.left_key)
        if self.grounded and self.grav != 0:
            if move != 0:
                # Dynamic grounded
                self.hspd *= self.ground_fric_dynamic

                # Running
                if KEYBOARD.get_key_held(42):
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
        if self.jump_key > 0 and self.grounded:
            if self.collide(f_tupadd(self.pos, (0, 1))):
                self.vspd = -self.jump_speed
            elif self.collide(f_tupadd(self.pos, (0, -1))):
                self.vspd = self.jump_speed

        # Jump gravity
        if np.sign(self.vspd) == np.sign(self.grav):
            self.vspd += self.grav * self.fallgrav
        elif KEYBOARD.get_key_held(17, 72, 57):
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
        if self.collide((xpos + hspd, ypos)) == 1:
            while self.collide((xpos + hspd, ypos)) == 1:
                hspd -= shspd
            pos = (floor(xpos + hspd), ypos)
            hspd = 0

        # Vertical collision
        if self.collide((xpos, ypos + vspd)) == 1:
            while self.collide((xpos, ypos + vspd)) == 1:
                vspd -= svspd
            pos = (xpos, floor(ypos + vspd))
            vspd = 0

        self.pos = pos
        self.hspd = hspd
        self.vspd = vspd

class Button(GameObject):
    """Button game object."""
    def __init__(self, pos):
        # Dimensions
        super().__init__(pos, (TILESIZE, TILESIZE / 8))

        # Data
        self.data = []

        # Rendering
        self.set_frames(0, 'button_unpressed.png', 'button_pressed.png')

    def update(self):
        """Called every frame for each game object."""
        ply = OBJ.obj[self.data[1]]
        if self.frame == 0:
            if self.get_collision_self(ply.pos, ply.size):
                self.frame = 1
                OBJ.obj[self.data[0]].frame = 1

    def get_collision_self(self, pos, size):
        """See if object is pressing button."""
        bdom = [self.pos[0], self.pos[0] + self.size[0]-1]
        bran = [self.pos[1], self.pos[1] + self.size[1]-1]
        cdom = [pos[0], pos[0] + size[0]-1]
        cran = [pos[1], pos[1] + size[1]-1]
        return f_col_rects(bdom, bran, cdom, cran)

class Door(GameObject):
    """Door game object."""
    def __init__(self, pos):
        # Dimensions
        super().__init__(pos, (TILESIZE, TILESIZE))

        # Data
        self.data = []

        # Images
        self.set_frames(0, 'door_closed.png', 'door_open.png')

    def update(self):
        """Called every frame for each game object."""
        ply = OBJ.obj[self.data[1]]
        if self.frame == 1 and self.get_collision_self(ply.pos, ply.size):
            LEVEL.load_level(self.data[0])

    def get_collision_self(self, pos, size):
        """See if object is pressing button."""
        bdom = [self.pos[0], self.pos[0] + self.size[0]-1]
        bran = [self.pos[1], self.pos[1] + self.size[1]-1]
        cdom = [pos[0], pos[0] + size[0]-1]
        cran = [pos[1], pos[1] + size[1]-1]
        return f_col_rects(bdom, bran, cdom, cran)


# main code section
def main():
    """Main game loop."""
    clock = pygame.time.Clock()
    LEVEL.load_level('level-1')
    run = True

    # Gameplay loop
    while run:
        clock.tick(FPS)
        KEYBOARD.reset()
        MOUSE.reset()

        # Event Handler
        for event in pygame.event.get():
            # Exit game
            if event.type == pygame.QUIT:
                run = False
            else:
                f_event_handler(event)

        # Quit by escape
        if KEYBOARD.get_key_pressed(1):
            run = False

        # Update objects
        objcopy = OBJ.obj.copy()
        for key in objcopy:
            try:
                OBJ.obj[key].update()
            except KeyError:
                print('key ' + str(key) + ' does not exist')

        # clear frame
        WIN.blank()

        # Render objects
        for key in OBJ.obj:
            OBJ.obj[key].render()
        STCOL.debug_render()

        # update display
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
