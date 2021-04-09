"""game.py dev project level editor."""
# pylint: disable=no-member
# pylint: disable=too-many-function-args
# pylint: disable=unnecessary-pass
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes

# Imports
import os
import ast
import pygame

from Helper_Functions.inputs import ObjKeyboard, ObjMouse
from Helper_Functions.tuple_functions import f_tupadd, f_tupmult, f_tupgrid, f_tupround
from Helper_Functions.file_system import ObjFile
from game import (f_swatch, f_cinverse, f_make_grid,
                  f_loop, f_limit, f_event_handler)

# initialize pygame modules
pygame.font.init()

# Constants variables
FULLTILE = 32
HALFTILE = int(FULLTILE/2)
WIDTH, HEIGHT = 32 * FULLTILE, 24 * FULLTILE
FPS = 60

# File paths
DEFAULT_PATH = __file__[:-len(os.path.basename(__file__))]
ASSET_PATH = os.path.join(DEFAULT_PATH, 'Assets')
SPRITE_PATH = os.path.join(ASSET_PATH, 'Sprites')
LEVEL_PATH = os.path.join(ASSET_PATH, 'Levels')
TILEMAP_PATH = os.path.join(ASSET_PATH, 'Tilemaps')


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

    def update(self):
        """Update all Entities."""
        for key in self.obj:
            self.obj[key].update()

    def render_early(self):
        """Render that occurs before the background."""
        if self.visible:
            for obj in self.obj:
                self.obj[obj].render_early()

    def render(self):
        """Render that occurs between background and foreground."""
        if self.visible:
            for obj in self.obj:
                self.obj[obj].render()

    def render_late(self):
        """Render that occurs after the foreground."""
        if self.visible:
            for obj in self.obj:
                self.obj[obj].render_late()

    def toggle_visibility(self):
        """Toggle Entity visibility."""
        self.visible = not self.visible

    def instantiate(self, obj, key=None):
        """Add a ref. to a game object in the OBJ.obj dictionary."""
        if key is None:
            key = self.pool.popitem()[0]
        else:
            try:
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
        objects = self.obj.copy()
        for obj in objects:
            self.delete(obj)

        # Clear tiles
        TILE.clear()

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
        return None

# Adds objects to level
class Cursor():
    """Edits level."""
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.color = f_swatch((6, 6, 6))
        self.speed = FULLTILE
        self.select = 0
        self.tile_map = 0
        self.layer = 0
        self.mode = 0

    def update(self):
        """Update cursor pos and level changes."""
        # Change modes
        if KEYBOARD.get_key_pressed(16): # M
            self.mode += 1
            self.select = 0
            self.pos = f_tupgrid(self.pos, FULLTILE)
        if KEYBOARD.get_key_pressed(17): # N
            self.mode -= 1
            self.select = 0
            self.pos = f_tupgrid(self.pos, FULLTILE)
        self.mode = f_loop(self.mode, 0, 1)

        # Saving and loading
        if KEYBOARD.get_key_combo(22, 224): # Ctrl + S
            OBJ.save_level()
        if KEYBOARD.get_key_combo(15, 224): # Ctrl + L
            OBJ.load_level()

        # State machine
        if self.mode == 0: # Object mode
            self.speed = FULLTILE
            self.mode0()
        elif self.mode == 1: # Tile mode
            self.speed = HALFTILE
            self.mode1()

    def mode0(self):
        """Object mode."""
        # Keyboard
        # Changing selection
        self.select += (KEYBOARD.get_key_pressed(8) -
                        KEYBOARD.get_key_pressed(20))
        self.select = f_loop(self.select, 0, len(OBJ.object_names) - 1)

        # Movement
        self.movement()

        # Toggling objects
        if KEYBOARD.get_key_pressed(58):
            OBJ.toggle_visibility()

        # Place and remove objects with cursor
        if KEYBOARD.get_key_pressed(44):
            self.place_object()
        if KEYBOARD.get_key_pressed(76):
            self.remove_object()

        # Edit data
        if KEYBOARD.get_key_pressed(43):
            self.edit_object_data()

        # Mouse
        # Place object
        if MOUSE.get_button_held(1):
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, FULLTILE)
            if self.pos != pos or MOUSE.get_button_pressed(1):
                self.pos = pos
                self.place_object()

        # Remove object
        if MOUSE.get_button_held(3):
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, FULLTILE)
            if self.pos != pos or MOUSE.get_button_pressed(3):
                self.pos = pos
                self.remove_object()

    def mode1(self):
        """Tile mode."""
        # Keyboard
        # Layer selection
        self.layer += (KEYBOARD.get_key_pressed(27) -
                       KEYBOARD.get_key_pressed(29))
        self.layer = f_loop(self.layer, 0, len(TILE.layers) - 1)

        # Tilemap selection
        if KEYBOARD.get_key_combo(43, 225):
            self.tile_map -= 1
            self.select = 0
        if KEYBOARD.get_key_pressed(43):
            self.tile_map += 1
            self.select = 0
        self.tile_map = f_loop(self.tile_map, 0, len(TILE.tile_maps)-1)

        # Changing selection
        self.select += (KEYBOARD.get_key_pressed(8) -
                        KEYBOARD.get_key_pressed(20))
        self.select = f_loop(self.select, 0, len(TILE.tile_maps[self.tile_map][1]) - 1)

        # Movement
        self.movement()

        # Toggling tile maps
        if KEYBOARD.get_key_pressed(58):
            layer = list(TILE.layers.keys())[self.layer]
            TILE.layers[layer].toggle_visibility()

        # Place tiles with cursor
        if KEYBOARD.get_key_pressed(44):
            # Get arguments
            layer = list(TILE.layers.keys())[self.layer]
            pos = f_tupround(f_tupmult(self.pos, 1/HALFTILE), -1)

            # Create tile
            TILE.add_tile(layer, pos, self.tile_map, self.select)

        # Remove tiles with cursor
        if KEYBOARD.get_key_pressed(76):
            layer = list(TILE.layers.keys())[self.layer]
            pos = f_tupround(f_tupmult(self.pos, 1/HALFTILE), -1)

            # Remove tile
            TILE.remove_tile(layer, pos)

        # Mouse
        # Place tile
        if MOUSE.get_button_held(1):
            # Update position
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, HALFTILE)
            if self.pos != pos or MOUSE.get_button_pressed(1):
                self.pos = pos

                # Get arguments
                layer = list(TILE.layers.keys())[self.layer]
                pos = f_tupround(f_tupmult(self.pos, 1/HALFTILE), -1)

                # Create tile
                TILE.add_tile(layer, pos, self.tile_map, self.select)

        # Remove tile
        if MOUSE.get_button_held(3):
            # Update position
            pos = MOUSE.get_pos()
            pos = f_tupgrid(pos, HALFTILE)
            if self.pos != pos or MOUSE.get_button_pressed(3):
                self.pos = pos

                # Get arguments
                layer = list(TILE.layers.keys())[self.layer]
                pos = f_tupround(f_tupmult(self.pos, 1/HALFTILE), -1)

                # Remove tile
                TILE.remove_tile(layer, pos)

    def movement(self):
        """Move cursor."""
        hspd = (KEYBOARD.get_key_pressed(7, 79) -
                KEYBOARD.get_key_pressed(4, 80))
        vspd = (KEYBOARD.get_key_pressed(22, 81) -
                KEYBOARD.get_key_pressed(26, 82))
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

    def render_late(self):
        """Render cursor and debug text."""
        if self.mode == 0:
            WIN.draw_rect(self.pos, self.size, self.color)
            WIN.draw_text(self.pos, OBJ.object_names[self.select])
        elif self.mode == 1:
            # Tile
            WIN.draw_image(TILE.tile_maps[self.tile_map][1][self.select],
                           self.pos)
            # Tilemap name
            WIN.draw_text((0, HALFTILE), TILE.tile_maps[self.tile_map][0],
                          color=f_swatch((7, 0, 7)))
            # Layer name
            WIN.draw_text((0, FULLTILE), list(TILE.layers.keys())[self.layer],
                          color=f_swatch((7, 0, 7)))
        WIN.draw_text((0, 0), str(self.pos), 'arial12', f_swatch((7, 0, 7)))

# Sample of game object (level editor)
class Entity():
    """Sample game object (level editor)."""
    def __init__(self, pos, name, size=(FULLTILE, FULLTILE), color=(0, 0, 0)):
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
        tile_set = pygame.image.load(os.path.join(TILEMAP_PATH, fname)).convert()
        new_tile_map = []
        for xpos in range(int((tile_set.get_width() / HALFTILE))):
            surface = pygame.Surface((HALFTILE, HALFTILE))
            surface.blit(tile_set, (0, 0), area=pygame.Rect(
                (xpos * (HALFTILE), 0), (HALFTILE, HALFTILE)))
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
        return self.tile_maps[tile_mapid][1][tile_id]

    def clear(self):
        """Clears out all tile layers."""
        self.layers = {}

# Layer with tiles
class TileLayer():
    """Layer containing all of the tiles in a lookup form."""
    def __init__(self, name, size, grid=None):
        self.name = name
        self.visible = True
        width, height = size[0], size[1]
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
        """Make layer invisible."""
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
CUR = Cursor((0, 0), (FULLTILE, HALFTILE))
TILE = TileMap()


# Setup program
pygame.display.set_caption("Game X - Level Editor")
WIN.add_font('arial', 8)


# Load tilemaps into TILE
for file in os.listdir(TILEMAP_PATH):
    if file[-4:] == '.png':
        TILE.add_tile_map(file[:-4], file)
TILE.add_layer('background', (int(2*(WIDTH/FULLTILE)),
                              int(2*(HEIGHT/FULLTILE))))
TILE.add_layer('foreground', (int(2*(WIDTH/FULLTILE)),
                              int(2*(HEIGHT/FULLTILE))))


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
        OBJ.render_late()
        CUR.render_late()

        # Update display
        pygame.display.update()

    # Quit pygame
    pygame.quit()

# only run if this file is executed
if __name__ == "__main__":
    main()
