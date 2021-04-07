"""game.py dev project level editor."""
# pylint: disable=no-member
# pylint: disable=too-many-function-args
# pylint: disable=unnecessary-pass

# Imports
import os
import ast
import pygame
#import numpy as np

from Helper_Functions.inputs import ObjKeyboard, ObjMouse
from Helper_Functions.tuple_functions import f_tupadd, f_tupmult, f_tupgrid, f_tupround
from Helper_Functions.file_system import ObjFile
#from easygui import multenterbox
#import random as rand

pygame.init()


# Constants variables
TILESIZE = 32
WIDTH, HEIGHT = 32 * TILESIZE, 24 * TILESIZE
FPS = 60

# File paths
DEFAULT_PATH = os.getcwd()
GAME_PATH = os.path.join(DEFAULT_PATH, 'Game_X')
ASSET_PATH = os.path.join(GAME_PATH, 'Assets')
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
            'door',
            'grav-orb',
            'spike'
        ]
        self.object_colors = [
            (0, 0, 0),
            (2, 5, 5),
            (1, 1, 1),
            (1, 6, 1),
            (2, 2, 2),
            (2, 7, 2),
            (7, 7, 7)
        ]
        self.visible = True

    def render_early(self):
        if self.visible:
            for obj in self.obj:
                self.obj[obj].render_early()

    def render(self):
        if self.visible:
            for obj in self.obj:
                self.obj[obj].render()

    def render_late(self):
        if self.visible:
            for obj in self.obj:
                self.obj[obj].render_late()

    def update(self):
        for key in self.obj:
                OBJ.obj[key].update()

    def toggle_visibility(self):
        self.visible = not self.visible

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

    def save_level(self, filename=''):
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
            info = [obj.name, obj.pos, obj.key, obj.data, obj.entid]
            level.file.write(str(info) + '\n')

        # Write layers
        for layer_name in TILE.layers:
            info = ['tile-layer', layer_name, TILE.layers[layer_name].grid, 0, 0]
            level.file.write(str(info) + '\n')

        # Close file
        level.close()
        print('successful level save!')
        return None

    def load_level(self, filename=''):
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

        # Clear tiles
        TILE.layers = {}

        # Create objects
        for arg in obj_list:
            name = arg[0]
            if arg[0] != 'tile-layer':
                # Interpret object info
                pos, key, data, entid = arg[1:5]
                color = f_swatch(self.get_id_info(entid)[1])

                # Create object and set variables
                obj = Entity(pos, name, color=color)
                obj.entid, obj.data = entid, data

                # Instantiate object
                obj.key = self.instantiate(obj, key)
            else:
                # Interpret layer info
                layer_name, grid = arg[1:3]
                size = (len(grid), len(grid[0]))
                TILE.add_layer(layer_name, size, grid)

        # success
        print('successful level load!')

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
        if KEYBOARD.get_key_pressed(50): # M
            self.mode += 1
            self.select = 0
        if KEYBOARD.get_key_pressed(49): # N
            self.mode -= 1
            self.select = 0
        self.mode = f_loop(self.mode, 0, 1)

        # Saving and loading
        if KEYBOARD.get_key_combo(31, 29): # Ctrl + S
            OBJ.save_level()
        if KEYBOARD.get_key_combo(38, 29): # Ctrl + L
            OBJ.load_level()

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

        # Toggling objects
        if KEYBOARD.get_key_pressed(59):
            OBJ.toggle_visibility()

        # Place and remove objects with cursor
        if KEYBOARD.get_key_pressed(57):
            self.place_object()
        if KEYBOARD.get_key_pressed(83):
            self.remove_object()

        # Edit data
        if KEYBOARD.get_key_pressed(15):
            self.edit_object_data()

        # Mouse
        # Place object
        if MOUSE.get_button_held(1):
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, TILESIZE)
            if self.pos != pos or MOUSE.get_button_pressed(1):
                self.pos = pos
                self.place_object()

        # Remove object
        if MOUSE.get_button_held(3):
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
        if KEYBOARD.get_key_combo(15, 42):
            self.tile_map -= 1
            self.select = 0
        if KEYBOARD.get_key_pressed(15):
            self.tile_map += 1
            self.select = 0
        self.tile_map = f_loop(self.tile_map, 0, len(TILE.tile_maps)-1)

        # Changing selection
        self.select += (KEYBOARD.get_key_pressed(18) -
                        KEYBOARD.get_key_pressed(16))
        self.select = f_loop(self.select, 0, len(TILE.tile_maps[self.tile_map][1]) - 1)

        # Movement
        self.movement()

        # Toggling tile maps
        if KEYBOARD.get_key_pressed(59):
            layer = list(TILE.layers.keys())[self.layer]
            TILE.layers[layer].toggle_visibility()

        # Place tiles with cursor
        if KEYBOARD.get_key_pressed(57):
            # Get arguments
            layer = list(TILE.layers.keys())[self.layer]
            pos = f_tupround(f_tupmult(self.pos, 1/TILESIZE), -1)

            # Create tile
            TILE.add_tile(layer, pos, self.tile_map, self.select)

        # Remove tiles with cursor
        if KEYBOARD.get_key_pressed(83):
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

                # Create tile
                TILE.add_tile(layer, pos, self.tile_map, self.select)

        # Remove object
        if MOUSE.get_button_held(3):
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
            WIN.draw_text((0, TILESIZE), list(TILE.layers.keys())[self.layer])
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

    def render_early(self):
        """Entity render call."""
        pass

    def render(self):
        """Entity render call."""
        WIN.draw_rect(self.pos, self.size, self.color)

    def render_late(self):
        """Entity render call."""
        WIN.draw_text(self.pos, self.name, 'arial8', f_cinverse(self.color))

# Tile map
class TileMap():
    """Handles background and foreground graphics."""
    def __init__(self):
        self.layers = {}
        self.tile_maps = []

    def render(self, layer: str):
        """Render tiles at a specific layer."""
        self.layers[layer].render()

    def add_tile_map(self, name: str, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        tile_set = pygame.image.load(os.path.join(TILEMAP_PATH, fname))
        new_tile_map = []
        for xpos in range(int((tile_set.get_width() / TILESIZE))):
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
            print('layer ' + str(layer) + ' does not exist')

    def add_tile(self, layer: str, pos: tuple, tilemap_id: int, tile_id: int):
        """Places a tile."""
        self.layers[layer].add_tile(pos, (tilemap_id, tile_id))

    def remove_tile(self, layer: str, pos: tuple):
        """Removes a tile."""
        self.layers[layer].remove_tile(pos)

    def get_tile(self, tile_mapid, tile_id):
        """Gets tile image."""
        return TILE.tile_maps[tile_mapid][1][tile_id]

# Layer with tiles
class TileLayer():
    def __init__(self, name, size, grid=None):
        self.name = name
        w, h = size[0], size[1]
        self.visible = True
        if grid is None:
            self.grid = [None] * w
            for column in range(size[0]):
                self.grid[column] = [None] * h
        else:
            self.grid = grid

    def render(self):
        """Draw tiles."""
        if self.visible:
            for column in enumerate(self.grid):
                for row in enumerate(self.grid[column[0]]):
                    tile_info = self.grid[column[0]][row[0]]
                    if tile_info is not None:
                        tile = TILE.get_tile(*tile_info)
                        pos = f_tupmult((column[0], row[0]), TILESIZE)
                        WIN.draw_image(tile, pos)

    def toggle_visibility(self):
        self.visible = not self.visible

    def add_tile(self, pos, tile_info):
        """Add tiles to grid on the layer."""
        self.grid[pos[0]][pos[1]] = tile_info

    def remove_tile(self, pos):
        """Remove tiles from the grid on the grid."""
        self.grid[pos[0]][pos[1]] = None


# Constant objects
WIN = Window(WIDTH, HEIGHT)
KEYBOARD = ObjKeyboard()
MOUSE = ObjMouse()
OBJ = Objects()
CUR = Cursor((0, 0), (TILESIZE, TILESIZE/2))
TILE = TileMap()


# Setup program
pygame.display.set_caption("Game X - Level Editor")
WIN.add_font('arial', 8)


# Load tilemaps into TILE
for file in os.listdir(TILEMAP_PATH):
    if file[-4:] == '.png':
        TILE.add_tile_map(file[:-4], file)
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
        OBJ.update()

        # Clear frame
        WIN.blank()
        OBJ.render_early()

        # Render background layers
        TILE.render('background')

        # Render objects
        OBJ.render()

        # Render foreground layers
        TILE.render('foreground')

        # Render on top
        CUR.render()
        OBJ.render_late()

        # Update display
        pygame.display.update()

    # Quit pygame
    pygame.quit()

# only run if this file is executed
if __name__ == "__main__":
    main()
