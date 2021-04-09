# Imports
import os
from math import floor
import ast

from Helper_Functions.tuple_functions import f_tupadd, f_tupmult, f_tupround
from Helper_Functions.file_system import ObjFile
from Helper_Functions.collisions import f_col_rects

import pygame
from pygame.locals import (QUIT, KEYUP, KEYDOWN, MOUSEBUTTONDOWN,
                           MOUSEBUTTONUP, MOUSEMOTION)


# Methods
# Handle events
def f_event_handler(event, keyboard, mouse):
    """Handles inputs and events."""
    # Key pressed
    if event.type == KEYDOWN:
        keyboard.set_key(event.scancode, 1)

    # Key released
    elif event.type == KEYUP:
        keyboard.set_key(event.scancode, 0)

    # Mouse movement
    elif event.type == MOUSEMOTION:
        mouse.pos = event.pos
        mouse.rel = f_tupadd(mouse.rel, event.rel)

    # Mouse pressed
    elif event.type == MOUSEBUTTONDOWN:
        mouse.button_pressed[event.button] = 1
        mouse.button_held[event.button] = 1
        mouse.button_pressed_pos[event.button] = event.pos

    # Mouse released
    elif event.type == MOUSEBUTTONUP:
        mouse.button_pressed[event.button] = 0
        mouse.button_held[event.button] = 0

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


# Classes
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

    def draw_rect(self, pos: tuple, size: tuple, color=(0, 0, 0)):
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
    def __init__(self, level_path, object_handler, static_collider,
                 dynamic_collider, tile_handler):
        self.levels = {}
        self.current_level = ''
        self.level_path = level_path
        self.obj = object_handler
        self.static = static_collider
        self.dynamic = dynamic_collider
        self.tile = tile_handler

    def load_level(self, level_name: str):
        """Load level parts such as GameObjects and Tiles."""
        level = ObjFile(self.level_path, level_name + '.lvl')
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
        self.obj.clear()
        self.static.clear()
        self.dynamic.clear()

        # Create objects
        for arg in obj_list:
            # Interpret object info
            name = arg[0]
            if name != 'tile-layer':
                pos, key, data = arg[1:4]
                self.obj.create_object(name, pos, key, data)
            else:
                # Interpret layer info
                layer_name, grid = arg[1:3]
                size = (len(grid), len(grid[0]))
                self.tile.add_layer(layer_name, size, grid)

    def reset(self):
        """Restart current level."""
        self.load_level(self.current_level)

# Handles object instances
class ObjectHandler():
    """Handles game objects."""
    def __init__(self, max_objects=2**16-1):
        # 65535 tacked objects max
        self.pool_size = max_objects
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
                print('key {} does not exist'.format(key))

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
                print('key {} is not in pool'.format(key))
                key = self.pool.popitem()[0]
        return key

    def instantiate_object(self, key, obj):
        """Add a ref. to a game object in the self.obj dictionary."""
        self.obj[key] = obj

    def create_object(self, name, pos, key, data):
        """Creates instances of objects and instantiates them."""
        pass

    def delete(self, key):
        """Removes a ref. of a game object from the self.obj dictionary."""
        self.obj[key].delete()
        del self.obj[key]
        self.pool[key] = 1

    def clear(self):
        """Clear all GameObjects."""
        objcopy = self.obj.copy()
        for obj in objcopy:
            self.delete(obj)

# Handles static collision
class StaticCollider():
    """Handles static collisions aligned to a grid."""
    def __init__(self, size: tuple, full_tile: int):
        self.size = size
        self.grid = f_make_grid(*self.size, 0)
        self.full_tile = full_tile

    def add_wall(self, pos: tuple):
        """Add a wall at a given position."""
        pos = f_tupround(f_tupmult(pos, 1/self.full_tile), -1)
        self.grid[pos[0]][pos[1]] = 1

    def remove_wall(self, pos: tuple):
        """Remove a wall at a given position."""
        pos = f_tupround(f_tupmult(pos, 1/self.full_tile), -1)
        self.grid[pos[0]][pos[1]] = 0

    def get_col(self, pos) -> bool:
        """Check for a wall at a given position."""
        pos = f_tupround(f_tupmult(pos, 1/self.full_tile), -1)
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
    def __init__(self, tile_path: str, full_tile: int, window):
        self.layers = {}
        self.tile_maps = []
        self.tile_path = tile_path
        self.full_tile = full_tile
        self.half_tile = round(full_tile/2)
        self.window = window

    def render(self, layer: str):
        """Render tiles at a specific layer."""
        self.layers[layer].render()

    def load(self):
        """Add Tilemap to list of tilemaps."""
        for file in os.listdir(self.tile_path):
            if file[-4:] == '.png':
                self.add_tile_map(file[:-4], file)

    def add_tile_map(self, name: str, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        tile_set = pygame.image.load(os.path.join(self.tile_path, fname)).convert()
        new_tile_map = []
        for xpos in range(int((tile_set.get_width() / self.half_tile))):
            # new surface
            surface = pygame.Surface((self.half_tile, self.half_tile)) # pylint: disable=too-many-function-args

            # write section of image to surface
            surface.blit(tile_set, (0, 0), area=pygame.Rect(
                (xpos * (self.half_tile), 0),
                (self.half_tile, self.half_tile)))

            # add surface to tilemap
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
            self.layers[layer] = TileLayer(layer, size, self, self.window)
        else:
            self.layers[layer] = TileLayer(layer, size, self,
                                           self.window, grid)

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
    def __init__(self, name, size, tile_handler, window, grid=None):
        self.name = name
        width, height = size[0], size[1]
        self.visible = True
        self.tile = tile_handler
        self.window = window
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
                        tile = self.tile.get_tile(*tile_info)
                        pos = f_tupmult((column[0], row[0]),
                                        self.tile.half_tile)
                        self.window.draw_image(tile, pos)

    def toggle_visibility(self):
        """Turn layer invisible."""
        self.visible = not self.visible

    def add_tile(self, pos, tile_info):
        """Add tiles to grid on the layer."""
        self.grid[pos[0]][pos[1]] = tile_info

    def remove_tile(self, pos):
        """Remove tiles from the grid on the grid."""
        self.grid[pos[0]][pos[1]] = None

