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

pygame.font.init()

# Constants variables
FULLTILE = 32
HALFTILE = int(FULLTILE/2)
WIDTH, HEIGHT = 32 * FULLTILE, 24 * FULLTILE
FPS = 60

# File paths
DEFAULT_PATH = __file__[:-8]
ASSET_PATH = os.path.join(DEFAULT_PATH, 'Assets')
SPRITE_PATH = os.path.join(ASSET_PATH, 'Sprites')
LEVEL_PATH = os.path.join(ASSET_PATH, 'Levels')
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

# Creates a grid
def f_make_grid(width, height, default_value):
    """Makes a grid populated with some default value."""
    grid = []
    for _ in range(width):
        grid.append([default_value] * height)
    return grid

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
    if event.type == KEYDOWN:
        KEYBOARD.set_key(event.scancode, 1)

    # Key released
    elif event.type == KEYUP:
        KEYBOARD.set_key(event.scancode, 0)

    # Mouse movement
    elif event.type == MOUSEMOTION:
        MOUSE.pos = event.pos
        MOUSE.rel = f_tupadd(MOUSE.rel, event.rel)

    # Mouse pressed
    elif event.type == MOUSEBUTTONDOWN:
        MOUSE.button_pressed[event.button] = 1
        MOUSE.button_held[event.button] = 1
        MOUSE.button_pressed_pos[event.button] = event.pos

    # Mouse released
    elif event.type == MOUSEBUTTONUP:
        MOUSE.button_pressed[event.button] = 0
        MOUSE.button_held[event.button] = 0


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

    def draw_rect(self, pos: tuple, size=(FULLTILE, FULLTILE), color=(0, 0, 0)):
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
    """Object which contains all levels in the game."""
    def __init__(self):
        self.levels = {}
        self.current_level = ''

    def load(self):
        """Load all levels in levels directory."""
        for file in os.listdir(LEVEL_PATH):
            if file[-4:] == '.lvl':
                self.add_level(file)

    def add_level(self, name: str):
        """Add level to dictionary of levels."""
        if os.path.exists(os.path.join(LEVEL_PATH, name)):
            self.levels[name] = name

    def load_level(self, level_name: str):
        """Load level parts such as GameObjects and Tiles."""
        level = ObjFile(LEVEL_PATH, level_name + '.lvl')
        level.read()
        self.current_level = level_name
        obj_list = level.file.readlines()

        # Convert types
        for count in enumerate(obj_list):
            obj_list[count[0]] = (ast.literal_eval(obj_list[count[0]][:-1]))
            if not isinstance(obj_list[count[0]], list):
                obj_list[count[0]] = []

        # Close file
        level.close()

        # Clear entities
        OBJ.clear()
        STCOL.clear()
        DYCOL.clear()

        # Create objects
        for arg in obj_list:
            # Interpret object info
            name = arg[0]
            if name != 'tile-layer':
                pos, key, data = arg[1:4]
                OBJ.create_object(name, pos, key, data)
            else:
                # Interpret layer info
                layer_name, grid = arg[1:3]
                size = (len(grid), len(grid[0]))
                TILE.add_layer(layer_name, size, grid)

    def reset(self):
        """Restart current level."""
        self.load_level(self.current_level)

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

    def update(self, dt):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            try:
                self.obj[key].update(dt)
            except KeyError:
                print('key {key} does not exist'.format(key=key))

    def render_early(self):
        """Render that occurs before the background."""
        for key in self.obj:
            self.obj[key].render_early()

    def render(self):
        """Render that occurs between background and foreground."""
        for key in self.obj:
            self.obj[key].render()

    def render_late(self):
        """Render that occurs after the foreground."""
        for key in self.obj:
            self.obj[key].render_late()

    def instantiate_key(self, key=None):
        """Add a ref. to a game object in the self.obj dictionary."""
        if key is None:
            key = self.pool.popitem()[0]
        else:
            try:
                self.pool[key]
            except IndexError:
                print(self.pool)
                print('key {key} is not in pool'.format(key=key))
                key = self.pool.popitem()[0]
        return key

    def instantiate_object(self, key, obj):
        """Add a ref. to a game object in the self.obj dictionary."""
        self.obj[key] = obj

    def delete(self, key):
        """Removes a ref. of a game object from the self.obj dictionary."""
        self.obj[key].delete()
        del self.obj[key]
        self.pool[key] = 1

    def create_object(self, name, pos, key, data):
        """Loads a level into the self.obj dictioanry."""
        # Object creation
        if name == 'wall':
            STCOL.add_wall((int(pos[0] / FULLTILE), int(pos[1] / FULLTILE)))

        elif name == 'player':
            key = self.instantiate_key(key)
            obj = Player(key, pos, (FULLTILE, FULLTILE), name, data)
            self.instantiate_object(key, obj)

        elif name == 'button':
            key = self.instantiate_key(key)
            obj = Button(key, pos, (FULLTILE, FULLTILE/8), name, data)
            self.instantiate_object(key, obj)

        elif name == 'door':
            key = self.instantiate_key(key)
            obj = Door(key, pos, (FULLTILE, FULLTILE), name, data)
            self.instantiate_object(key, obj)

        elif name == 'grav-orb':
            key = self.instantiate_key(key)
            obj = GravOrb(key, pos, (FULLTILE, FULLTILE), name, data)
            self.instantiate_object(key, obj)

        elif name == 'spike':
            key = self.instantiate_key(key)
            obj = Spike(key, pos, (FULLTILE, FULLTILE/8), name, data)
            self.instantiate_object(key, obj)

    def clear(self):
        """Clear all GameObjects."""
        objcopy = self.obj.copy()
        for obj in objcopy:
            self.delete(obj)

# Handles static collision
class StaticCollider():
    """Handles static collisions aligned to a grid."""
    def __init__(self, size: tuple):
        self.size = size
        self.grid = f_make_grid(*self.size, 0)
        #self.image = pygame.image.load(os.path.join(SPRITE_PATH, 'wall.png'))

    def add_wall(self, pos: tuple):
        """Add a wall at a given position."""
        self.grid[pos[0]][pos[1]] = 1

    def remove_wall(self, pos: tuple):
        """Remove a wall at a given position."""
        self.grid[pos[0]][pos[1]] = 0

    def get_col(self, pos) -> bool:
        """Check for a wall at a given position."""
        pos = (floor(pos[0]/FULLTILE), floor(pos[1]/FULLTILE))
        try:
            return self.grid[pos[0]][pos[1]]
        except IndexError:
            return 0

    def clear(self):
        """Clear all Static collision points off of grid"""
        self.grid = f_make_grid(*self.size, 0)

# Handles Dynamic collisions
class DynamicCollider():
    """Handles collisions with moving objects."""
    def __init__(self):
        self.colliders = {}

    def add_collider(self, key, obj):
        """Adds a collider to self.colliders."""
        self.colliders[key] = obj

    def remove_collider(self, key):
        """Removes a collider to self.colliders."""
        try:
            del self.colliders[key]
        except KeyError:
            pass

    def get_collision(self, pos, rect, key=-1) -> list:
        """Checks each collider to see if they overlap a rectangle."""
        collide = []
        dom = f_tupadd(rect[0], pos[0])
        ran = f_tupadd(rect[1], pos[1])
        for col in self.colliders:
            if col != key:
                cobj = self.colliders[col]
                crect = cobj.crect
                cpos = cobj.pos
                cdom = f_tupadd(crect[0], cpos[0])
                cran = f_tupadd(crect[1], cpos[1])
                if f_col_rects(dom, ran, cdom, cran):
                    collide.append(cobj)
        return collide

    def clear(self):
        """Remove all colliders."""
        self.colliders = {}

# Tile map
class TileMap():
    """Handles background and foreground graphics."""
    def __init__(self):
        self.layers = {}
        self.tile_maps = []

    def render(self, layer: str):
        """Render tiles at a specific layer."""
        self.layers[layer].render()

    def load(self):
        """Add Tilemap to list of tilemaps."""
        for file in os.listdir(TILEMAP_PATH):
            if file[-4:] == '.png':
                self.add_tile_map(file[:-4], file)

    def add_tile_map(self, name: str, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        tile_set = pygame.image.load(os.path.join(TILEMAP_PATH, fname)).convert()
        new_tile_map = []
        for xpos in range(int((tile_set.get_width() / HALFTILE))):
            surface = pygame.Surface((HALFTILE, HALFTILE)) # pylint: disable=too-many-function-args
            surface.blit(tile_set, (0, 0), area=pygame.Rect(
                (xpos * (HALFTILE), 0), (HALFTILE, HALFTILE)))
            new_tile_map.append(surface)
        self.tile_maps.append((name, new_tile_map))

    def remove_tile_map(self, name: str):
        """Removes a tilemap from the tile_maps dictionary."""
        try:
            del self.tile_maps[name]
        except KeyError:
            print('tilemap {} does not exist'.format(name))

    def add_layer(self, layer: str, size: tuple, grid=None):
        """Creates a layer."""
        if grid is None:
            self.layers[layer] = TileLayer(layer, size)
        else:
            self.layers[layer] = TileLayer(layer, size, grid)

    def remove_layer(self, layer: str):
        """Removes an existing layer."""
        try:
            del self.layers[layer]
        except KeyError:
            print('layer {} does not exist'.format(layer))

    def add_tile(self, layer: str, pos: tuple, tilemap_id: int, tile_id: int):
        """Places a tile."""
        self.layers[layer].add_tile(pos, (tilemap_id, tile_id))

    def remove_tile(self, layer: str, pos: tuple):
        """Removes a tile."""
        self.layers[layer].remove_tile(pos)

    def get_tile(self, tile_mapid, tile_id):
        """Gets tile image."""
        return self.tile_maps[tile_mapid][1][tile_id]

# Layer with tiles
class TileLayer():
    """Layer containing all of the tiles in a lookup form."""
    def __init__(self, name, size, grid=None):
        self.name = name
        width, height = size[0], size[1]
        self.visible = True
        if grid is None:
            grid = f_make_grid(width, height, None)
        self.grid = grid

    def render(self):
        """Draw tiles."""
        if self.visible:
            for column in enumerate(self.grid):
                for row in enumerate(self.grid[column[0]]):
                    tile_info = self.grid[column[0]][row[0]]
                    if tile_info is not None:
                        tile = TILE.get_tile(*tile_info)
                        pos = f_tupmult((column[0], row[0]), HALFTILE)
                        WIN.draw_image(tile, pos)

    def toggle_visibility(self):
        """Turn layer invisible."""
        self.visible = not self.visible

    def add_tile(self, pos, tile_info):
        """Add tiles to grid on the layer."""
        self.grid[pos[0]][pos[1]] = tile_info

    def remove_tile(self, pos):
        """Remove tiles from the grid on the grid."""
        self.grid[pos[0]][pos[1]] = None


# Constant objects
WIN = Window(WIDTH, HEIGHT)
OBJ = Objects()
LEVEL = Level()
level_size = f_tupmult((WIDTH, HEIGHT), 1/FULLTILE)
level_size = f_tupround(level_size, 0)
STCOL = StaticCollider(level_size)
DYCOL = DynamicCollider()
KEYBOARD = ObjKeyboard()
MOUSE = ObjMouse()
TILE = TileMap()


# Setup program
pygame.event.set_allowed([QUIT, KEYUP, KEYDOWN, MOUSEBUTTONDOWN,
                      MOUSEBUTTONUP, MOUSEMOTION])
pygame.display.set_caption("Game X")
TILE.load()
LEVEL.load()


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
            file_path = os.path.join(SPRITE_PATH, file)
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
            if STCOL.get_col(f_tupadd(pos, point)):
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
        return DYCOL.get_collision(pos, crect, key)

    def render_early(self):
        """Rendering before the background layer."""
        pass

    def render(self):
        """Rendering at the same time as other objects."""
        pos = self.pos
        WIN.draw_image(self.frames[self.frame], pos)

    def render_late(self):
        """Rendering after foreground layer."""
        pass

    def delete(self):
        """Called when object is deleted from Objects dictionary."""
        DYCOL.remove_collider(self.key)

class Player(GameObject):
    """Player game object."""
    def __init__(self, key, pos, size, name, data):
        # GameObject initialization
        super().__init__(key, pos, size)
        self.name = name
        self.data = data

        # Dynamic collision
        DYCOL.add_collider(self.key, self)

        # Color
        self.color = f_swatch((2, 5, 5))

        # Keys
        self.jump_keys = (44, 26, 82)
        self.jump_key = 0
        self.left_keys = (4, 80)
        self.left_key = 0
        self.right_keys = (7, 79)
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

    def render(self):
        """Rendering at the same time as other objects."""
        pass

    def render_late(self):
        """Called every frame to render each game object."""
        super().render()
        text = 'Grounded: {}'.format(self.grounded)
        WIN.draw_text((FULLTILE, 1.5*FULLTILE), text, color=f_swatch((7, 7, 7)))
        text = 'speed: ({:.3f}, {:.3f})'.format(self.hspd, self.vspd)
        WIN.draw_text((FULLTILE, 2*FULLTILE), text, color=f_swatch((7, 7, 7)))

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
        if KEYBOARD.get_key_pressed(*self.jump_keys) and self.jump_key <= 0:
            self.jump_key = self.jump_lenience
        self.jump_key = f_limit(self.jump_key, 0, self.jump_lenience)

        # Horizontal controls
        self.left_key = KEYBOARD.get_key_held(*self.left_keys)
        self.right_key = KEYBOARD.get_key_held(*self.right_keys)

    def movement(self):
        """Handle player movement."""
        # Horizontal speed
        move = (self.right_key - self.left_key)
        if self.grounded and self.grav != 0:
            if move != 0:
                # Dynamic grounded
                self.hspd *= self.ground_fric_dynamic

                # Running
                if KEYBOARD.get_key_held(225):
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
                self.jump_delay = self.coyote
                self.vspd = -(self.jump_speed + (self.hspd/8)**2)
            elif self.grounded < 0:
                self.jump_delay = self.coyote
                self.vspd = (self.jump_speed + (self.hspd/8)**2)
        else:
            self.jump_delay -= np.sign(self.jump_delay)

        # Jump gravity
        if np.sign(self.vspd) == np.sign(self.grav):
            self.vspd += self.grav * self.fallgrav
        elif KEYBOARD.get_key_held(*self.jump_keys):
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
                    OBJ.obj[self.door].frame = 1

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
                    LEVEL.load_level(self.next_level)

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
                OBJ.delete(self.key)

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
                LEVEL.reset()


# Starting level
LEVEL.load_level('level0')


# Main code section
def main():
    """Main game loop."""
    clock = pygame.time.Clock()
    run = True

    # Gameplay loop
    while run:
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)
        KEYBOARD.reset()
        MOUSE.reset()

        # Event Handler
        for event in pygame.event.get():
            # Exit game
            if event.type == QUIT:
                run = False
            else:
                f_event_handler(event)

        # Quit by escape
        if KEYBOARD.get_key_pressed(41):
            run = False

        # Update objects
        OBJ.update(dt)

        # clear frame
        WIN.blank()

        # Render background layers
        OBJ.render_early()
        TILE.render('background')

        # Render objects
        OBJ.render()

        # Render foreground layers
        TILE.render('foreground')
        OBJ.render_late()

        # FPS display
        fps = 'fps: {:3f}'.format(clock.get_fps())
        WIN.draw_text((FULLTILE, FULLTILE), fps, color=f_swatch((7, 7, 7)))

        # update display
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()