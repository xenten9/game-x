"""game.py dev project level editor."""
# pylint: disable=no-member
# pylint: disable=too-many-function-args
# pylint: disable=unnecessary-pass

# Imports
import os
import ast
import pygame
#import numpy as np

from inputs import ObjKeyboard, ObjMouse
from tuple_functions import f_tupadd, f_tupmult, f_tupgrid, f_tupround
from file_system import ObjFile
#from easygui import multenterbox
#from random import choice

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
        self.object_names = [
            'null',
            'player',
            'wall',
            'button',
            'door'
        ]
        self.object_colors = [
            (0, 0, 0),
            (2, 5, 5),
            (1, 1, 1),
            (1, 6, 1),
            (2, 2, 2)
        ]

    def instantiate(self, obj, key=None):
        """Add a ref. to a game object in the OBJ.obj dictionary."""
        if key is None:
            key = self.pool.popitem()[0]
        else:
            try:
                self.pool[key]
                del self.pool[key]
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

    def get_id_info(self, objid: int) -> tuple:
        """Returns the (name, color) of a given objectid."""
        return (self.object_names[objid], self.object_colors[objid])

    def save_to_file(self, filename=''):
        """Save level to disk."""
        # Get file name
        if filename in (None, ''):
            filename = input('level name: ')
        if filename in (None, ''):
            return None

        # Create file object and open it to writing
        level = ObjFile(LEVEL_PATH, filename + '.lvl')
        level.create(1) # Overwrite file if it exists
        level.write()

        # Write each object to file
        for key in self.obj:
            obj = self.obj[key]
            info = [obj.name, obj.pos, obj.entid, obj.key, obj.data]
            level.file.write(str(info) + '\n')

        # Close file
        level.close()
        print('successful level save!')
        return None

    def load_from_file(self, filename=''):
        """Load level from disk."""
        # Get file name
        if filename in (None, ''):
            filename = input('level name: ')
        if filename in (None, ''):
            return None

        # Create file object and read it
        level = ObjFile(LEVEL_PATH, filename + '.lvl')
        level.read()
        obj_list = level.file.readlines()

        # Convert types to literal
        for count in enumerate(obj_list):
            obj_list[count[0]] = (ast.literal_eval(obj_list[count[0]][:-1]))

        # Close file
        level.close()

        # Clear entities
        objects = OBJ.obj.copy()
        for obj in objects:
            OBJ.delete(obj)

        # Create objects
        for arg in obj_list:
            print(arg)
            # Interpret object info
            name, pos, entid, key, data = arg[0:5]
            color = f_swatch(self.get_id_info(entid)[1])

            # Create object and set variables
            obj = Entity(pos, name, color=color)
            obj.entid, obj.data = entid, data

            # Instantiate object
            obj.key = self.instantiate(obj, key)
        return None

# Adds objects to level
class Cursor():
    """Edits level."""
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.color = f_swatch((6, 6, 6))
        self.speed = TILESIZE
        self.select = 0
        self.tile_map = 0
        self.layer = 0
        self.mode = 0

    def update(self):
        """Update cursor pos and level changes."""
        # Change modes
        if KEYBOARD.get_key_pressed(50):
            self.mode += 1
            self.select = 0
        if KEYBOARD.get_key_pressed(49):
            self.mode -= 1
            self.select = 0
        self.mode = f_loop(self.mode, 0, 1)

        # Saving and loading
        if KEYBOARD.get_key_held(29):
            if KEYBOARD.get_key_pressed(31):
                OBJ.save_to_file()
            elif KEYBOARD.get_key_pressed(38):
                OBJ.load_from_file()

        # State machine
        if self.mode == 0: # Object mode
            self.mode0()
        elif self.mode == 1: # Tile mode
            self.mode1()

    def mode0(self):
        """Object mode."""
        # Keyboard
        # Changing selection
        self.select += (KEYBOARD.get_key_pressed(18) -
                        KEYBOARD.get_key_pressed(16))
        self.select = f_loop(self.select, 0, len(OBJ.object_names) - 1)

        # Movement
        self.movement()

        # Place and remove objects with cursor
        if KEYBOARD.get_key_pressed(57):
            self.place_object()
        elif KEYBOARD.get_key_pressed(83):
            self.remove_object()

        # Edit data
        if KEYBOARD.get_key_pressed(15):
            self.edit_object_data()

        # Mouse
        # Place object
        elif MOUSE.get_button_held(1):
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, TILESIZE)
            if self.pos != pos or MOUSE.get_button_pressed(1):
                self.pos = pos
                self.place_object()

        # Remove object
        elif MOUSE.get_button_held(3):
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, TILESIZE)
            if self.pos != pos or MOUSE.get_button_pressed(3):
                self.pos = pos
                self.remove_object()

    def mode1(self):
        """Tile mode."""
        # Keyboard
        # Layer selection
        self.layer += (KEYBOARD.get_key_pressed(45) -
                        KEYBOARD.get_key_pressed(44))
        self.layer = f_loop(self.layer, 0, len(TILE.layers) - 1)

        # Tilemap selection
        if KEYBOARD.get_key_pressed(15):
            if KEYBOARD.get_key_held(42):
                self.tile_map -= 1
            else:
                self.tile_map += 1
        self.tile_map = f_loop(self.tile_map, 0, len(TILE.tile_maps)-1)

        # Changing selection
        self.select += (KEYBOARD.get_key_pressed(18) -
                        KEYBOARD.get_key_pressed(16))
        self.select = f_loop(self.select, 0, len(TILE.tile_maps[self.tile_map][1]) - 1)

        # Movement
        self.movement()

        # Place and remove tiles with cursor
        if KEYBOARD.get_key_pressed(57):
            layer = list(TILE.layers.keys())[self.layer]
            pos = f_tupround(f_tupmult(self.pos, 1/TILESIZE), -1)
            tile = TILE.tile_maps[self.tile_map][1][self.select]
            # Create tile
            TILE.add_tile(layer, pos, tile)

        elif KEYBOARD.get_key_pressed(83):
            layer = list(TILE.layers.keys())[self.layer]
            pos = f_tupround(f_tupmult(self.pos, 1/TILESIZE), -1)
            # Remove tile
            TILE.remove_tile(layer, pos)

        # Mouse
        # Place tile
        if MOUSE.get_button_held(1):
            # Update position
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, TILESIZE)
            if self.pos != pos or MOUSE.get_button_pressed(1):
                self.pos = pos

                # Get arguments
                layer = list(TILE.layers.keys())[self.layer]
                pos = f_tupround(f_tupmult(self.pos, 1/TILESIZE), -1)
                tile = TILE.tile_maps[self.tile_map][1][self.select]

                # Create tile
                TILE.add_tile(layer, pos, tile)

        # Remove object
        elif MOUSE.get_button_held(3):
            # Update position
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, TILESIZE)
            if self.pos != pos or MOUSE.get_button_pressed(3):
                self.pos = pos

                # Get arguments
                layer = list(TILE.layers.keys())[self.layer]
                pos = f_tupround(f_tupmult(self.pos, 1/TILESIZE), -1)

                # Remove tile
                TILE.remove_tile(layer, pos)

    def movement(self):
        """Move cursor."""
        hspd = (KEYBOARD.get_key_pressed(32, 77) -
                KEYBOARD.get_key_pressed(30, 75))
        vspd = (KEYBOARD.get_key_pressed(31, 80) -
                KEYBOARD.get_key_pressed(17, 72))
        self.pos = f_tupadd(self.pos, f_tupmult((hspd, vspd), self.speed))

    def place_object(self):
        """Places object under cursor."""
        self.remove_object()
        name, color = OBJ.get_id_info(self.select)
        color = f_swatch(color)
        obj = Entity(self.pos, name, color=color)
        obj.key = OBJ.instantiate(obj)
        obj.entid = self.select
        obj.data = []

    def remove_object(self):
        """Removes object under cursor."""
        obj_copy = OBJ.obj.copy()
        for element in obj_copy:
            obj = OBJ.obj[element]
            if obj.pos == self.pos:
                OBJ.delete(element)

    def edit_object_data(self):
        """Print object data or edit it if shift is held."""
        objcopy = OBJ.obj.copy()
        for element in objcopy:
            obj = OBJ.obj[element]
            datatype = None
            if obj.pos == self.pos:
                if KEYBOARD.get_key_held(42):
                    while datatype != list:
                        data = input('enter data list: ')
                        try:
                            data = ast.literal_eval(data)
                        except (ValueError, SyntaxError):
                            pass
                        else:
                            datatype = type(data)

                        if datatype != list:
                            print('input must be a list')
                    obj.data = data
                    print('successful data write.')
                else:
                    print(obj.name)
                    print(element)
                    print(obj.data)

    def render(self):
        """Render cursor and debug text."""
        WIN.draw_text((0, 0), str(self.pos), 'arial12',
                      f_cinverse(self.color))
        if self.mode == 0:
            WIN.draw_rect(self.pos, self.size, self.color)
            WIN.draw_text(self.pos, OBJ.object_names[self.select])
        elif self.mode == 1:
            WIN.draw_text((0, TILESIZE/2), TILE.tile_maps[self.tile_map][0])
            WIN.draw_image(TILE.tile_maps[self.tile_map][1][self.select], self.pos)

# Sample of game object (level editor)
class Entity():
    """Sample game object (level editor)."""
    def __init__(self, pos, name, size=(TILESIZE, TILESIZE), color=(0, 0, 0)):
        self.pos = pos
        self.name = name
        self.size = size
        self.color = color
        self.entid = 0
        self.data = []
        self.key = 0

    def update(self):
        """Entity update call."""
        pass

    def render(self):
        """Entity render call."""
        WIN.draw_rect(self.pos, self.size, self.color)
        WIN.draw_text(self.pos, self.name, 'arial8', f_cinverse(self.color))

# Tile map
class TileMap():
    """Handles background and foreground graphics."""
    def __init__(self):
        self.layers = {}
        self.tile_maps = []

    def add_tile_map(self, name: str, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        tile_set = pygame.image.load(os.path.join(TILEMAP_PATH, fname))
        new_tile_map = []
        for xpos in range(int((tile_set.get_width() / TILESIZE))):
            print(xpos*TILESIZE)
            surface = pygame.Surface((TILESIZE, TILESIZE))
            surface.blit(tile_set, (0, 0), area=pygame.Rect(
                (xpos * (TILESIZE), 0), (TILESIZE, TILESIZE)))
            new_tile_map.append(surface)
        self.tile_maps.append((name, new_tile_map))

    def remove_tile_map(self, name: str):
        """Removes a tilemap from the tile_maps dictionary."""
        try:
            del self.tile_maps[name]
        except KeyError:
            print('tilemap ' + str(name) + ' does not exist')

    def add_layer(self, layer: str, size):
        """Creates a layer."""
        self.layers[layer] = TileLayer(layer, size)

    def remove_layer(self, layer: str):
        """Removes an existing layer."""
        try:
            del self.layers[layer]
        except KeyError:
            print('layer ' + str(layer) + ' does not exist')

    def add_tile(self, layer: str, pos: tuple, tile):
        """Places a tile."""
        self.layers[layer].add_tile(pos, tile)

    def remove_tile(self, layer: str, pos: tuple):
        """Removes a tile."""
        self.layers[layer].remove_tile(pos)

    def render(self, layer: str):
        """Render tiles at a specific layer."""
        for layer in self.layers:
            self.layers[layer].render()

# Layer with tiles
class TileLayer():
    def __init__(self, name, size):
        self.name = name
        w, h = size[0], size[1]
        self.grid = [None] * w
        for column in range(size[0]):
            self.grid[column] = [None] * h

    def add_tile(self, pos, tile):
        self.grid[pos[0]][pos[1]] = tile

    def remove_tile(self, pos):
        self.grid[pos[0]][pos[1]] = None

    def render(self):
        for column in enumerate(self.grid):
            for row in enumerate(self.grid[column[0]]):
                tile = self.grid[column[0]][row[0]]
                if tile is not None:
                    pos = f_tupmult((column[0], row[0]), TILESIZE)
                    WIN.draw_image(tile, pos)


# Constant objects
WIN = Window(WIDTH, HEIGHT)
KEYBOARD = ObjKeyboard()
MOUSE = ObjMouse()
OBJ = Objects()
CUR = Cursor((0, 0), (TILESIZE, TILESIZE/2))
TILE = TileMap()


# Setup
pygame.display.set_caption("Game.py")
WIN.add_font('arial', 8)
TILE.add_tile_map('tilemap0', 'Tileset0.png')
TILE.add_layer('background', (32, 32))
TILE.add_layer('foreground', (32, 32))


# main code section
def main():
    """Main level editing loop."""
    clock = pygame.time.Clock()
    run = True

    # Gameplay loop
    while run:
        clock.tick(FPS)
        KEYBOARD.reset()
        MOUSE.reset()

        # Event Handler
        events = pygame.event.get()
        for event in events:
            # Exit game
            if event.type == pygame.QUIT:
                run = False
            else:
                f_event_handler(event)

        # Quit by escape
        if KEYBOARD.get_key_pressed(1):
            run = False

        # Update
        CUR.update()
        for key in OBJ.obj:
            OBJ.obj[key].update()

        # Clear frame
        WIN.blank()

        # Render background layers
        TILE.render('background')

        # Render objects
        for key in OBJ.obj:
            OBJ.obj[key].render()

        # Render foreground layers
        TILE.render('foreground')

        # Render on top
        CUR.render()

        # Update display
        pygame.display.update()

    # Quit pygame
    pygame.quit()

# only run if this file is executed
if __name__ == "__main__":
    main()
