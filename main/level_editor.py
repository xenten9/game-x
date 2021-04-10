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
from engine import (Game, f_swatch, f_cinverse, f_make_grid, f_loop, f_limit)

# initialize pygame modules
pygame.font.init()

def f_create_object(name: str, pos: tuple, data: list, entid: int, key=None):
    """Creates entities."""
    color = GAME.OBJ.get_id_info(entid)[1]
    color = f_swatch(color)
    size = (FULLTILE, FULLTILE)
    if key is None:
        key = GAME.OBJ.instantiate_key()
    else:
        key = GAME.OBJ.instantiate_key(key)
    obj = Entity(pos, name, size, color, key, entid, data)
    GAME.OBJ.instantiate_object(key, obj)

# Handles object instances
#class Objects():
#    """Handles game objects."""
#    def __init__(self):
#        self.visible = True
#
#    def toggle_visibility(self):
#        """Toggle Entity visibility."""
#        self.visible = not self.visible

# Adds objects to level
class Cursor():
    """Edits level."""
    def __init__(self, pos):
        # Default variables
        self.pos = pos
        self.color = f_swatch((6, 6, 6))
        self.speed = 0

        # Modes
        self.mode = 0

        self.obj_select = 0

        self.tile_select = 0
        self.tile_map = 0
        self.layer = 0

        # Inputs
        # State machine saving and loading
        self.key_save = 0
        self.key_load = 0
        self.key_modeup = 0
        self.key_modedown = 0

        # Keyboard object
        self.key_place = 0
        self.key_remove = 0
        self.key_selup = 0
        self.key_seldown = 0
        self.key_toggle = 0
        self.key_tab = 0
        self.key_shift = 0

        # Keyboard tile
        self.key_tileup = 0
        self.key_tiledown = 0

        # Keyboard movement
        self.key_up = 0
        self.key_down = 0
        self.key_left = 0
        self.key_right = 0

        # Mouse
        self.mkey_place = 0
        self.mkey_remove = 0
        self.mpkey_place = 0
        self.mpkey_remove = 0

    def update(self, dt):
        """Update cursor pos and level changes."""
        # Get inputs
        self.get_inputs()

        # Change modes
        if self.key_modeup or self.key_modedown:
            self.mode += self.key_modeup - self.key_modedown
            self.pos = f_tupgrid(self.pos, FULLTILE)
        self.mode = f_loop(self.mode, 0, 1)

        # Saving and loading
        if self.key_save:
            GAME.save_level()
        elif self.key_load:
            GAME.load_level()

        # State machine
        if self.mode == 0: # Object mode
            self.speed = FULLTILE
            self.mode0()
        elif self.mode == 1: # Tile mode
            self.speed = HALFTILE
            self.mode1()

    def get_inputs(self):
        # State machine saving and loading
        self.key_save = GAME.KEYBOARD.get_key_combo(22, 224) # S + Ctrl
        self.key_load = GAME.KEYBOARD.get_key_combo(15, 224) # L + Ctrl
        self.key_modeup = GAME.KEYBOARD.get_key_pressed(16) # M
        self.key_modedown = GAME.KEYBOARD.get_key_pressed(17) # N

        # Keyboard object
        self.key_place = GAME.KEYBOARD.get_key_pressed(44) # Space
        self.key_remove = GAME.KEYBOARD.get_key_pressed(76) # Del
        self.key_selup = GAME.KEYBOARD.get_key_pressed(8) # E
        self.key_seldown = GAME.KEYBOARD.get_key_pressed(20) # Q
        self.key_toggle = GAME.KEYBOARD.get_key_pressed(58) # F1
        self.key_tab = GAME.KEYBOARD.get_key_pressed(43) # Tab
        self.key_shift = GAME.KEYBOARD.get_key_held(225) # Shift

        # Keyboard tile
        self.key_tileup = GAME.KEYBOARD.get_key_pressed(29) # Z
        self.key_tiledown = GAME.KEYBOARD.get_key_pressed(27) # X

        # Keyboard movement
        self.key_up = GAME.KEYBOARD.get_key_pressed(26, 82) # W or UpArrow
        self.key_down = GAME.KEYBOARD.get_key_pressed(22, 81) # S or DownArrow
        self.key_left = GAME.KEYBOARD.get_key_pressed(4, 80) # A or LeftArrow
        self.key_right = GAME.KEYBOARD.get_key_pressed(7, 79) # D or RightArrow

        # Mouse
        self.mkey_place = GAME.MOUSE.get_button_held(1) # Left mouse
        self.mkey_remove = GAME.MOUSE.get_button_held(3) # Right mouse
        self.mpkey_place = GAME.MOUSE.get_button_pressed(1) # Left mouse
        self.mpkey_remove = GAME.MOUSE.get_button_pressed(3) # Right mouse

    def mode0(self):
        """Object mode."""
        # Keyboard
        # Changing selection
        self.obj_select += (self.key_selup - self.key_seldown)
        self.obj_select = f_loop(self.obj_select, 0,
                                 len(GAME.OBJ.object_names) - 1)

        # Movement
        self.movement()

        # Toggling objects
        if self.key_toggle:
            GAME.OBJ.toggle_visibility()

        # Place and remove objects with cursor
        if self.key_place:
            self.place_object()
        if self.key_remove:
            self.remove_object()

        # View/Edit data
        if self.key_tab:
            self.view_object_data()

        # Mouse
        # Place object
        if self.mkey_place:
            pos = GAME.MOUSE.get_pos()
            pos = f_tupgrid(pos, FULLTILE)
            if self.pos != pos or self.mpkey_place:
                self.pos = pos
                self.place_object()

        # Remove object
        if self.mkey_remove:
            pos = GAME.MOUSE.get_pos()
            pos = f_tupgrid(pos, FULLTILE)
            if self.pos != pos or self.mpkey_remove:
                self.pos = pos
                self.remove_object()

    def mode1(self):
        """Tile mode."""
        # Keyboard
        # Layer selection
        if self.key_tab:
            if self.key_shift:
                self.layer -= 1
            else:
                self.layer += 1
            layer_len = len(GAME.TILE.layers)-1
            self.layer = f_loop(self.layer, 0, layer_len)

        # Tilemap selection
        if self.key_tileup:
            self.tile_map += 1
            self.tile_select = 0
        if self.key_tiledown:
            self.tile_map -= 1
            self.tile_select = 0
        tile_map_len = len(GAME.TILE.tile_maps)-1
        self.tile_map = f_loop(self.tile_map, 0, tile_map_len)

        # Changing selection
        self.tile_select += (self.key_selup - self.key_seldown)
        tile_maps_len = len(GAME.TILE.tile_maps[self.tile_map][1])-1
        self.tile_select = f_loop(self.tile_select, 0, tile_maps_len)

        # Movement
        self.movement()

        # Toggling tile maps
        if self.key_toggle:
            GAME.TILE.layers[layer].toggle_visibility()

        # Place tiles with cursor
        if self.key_place:
            self.place_tile()
        # Remove tiles with cursor
        if self.key_remove:
            self.remove_tile()

        # Mouse
        # Place tile
        if self.mkey_place:
            # Update position
            pos = GAME.MOUSE.get_pos()
            pos = f_tupgrid(pos, HALFTILE)
            if self.pos != pos or self.mpkey_place:
                self.pos = pos
                self.place_tile()

        # Remove tile
        if self.mkey_remove:
            # Update position
            pos = GAME.MOUSE.get_pos()
            pos = f_tupgrid(pos, HALFTILE)
            if self.pos != pos or self.mpkey_remove:
                self.pos = pos
                self.remove_tile()

    def movement(self):
        """Move cursor."""
        hspd = (self.key_right - self.key_left)
        vspd = (self.key_down - self.key_up)
        self.pos = f_tupadd(self.pos, f_tupmult((hspd, vspd), self.speed))

    def place_object(self):
        """Places object under cursor."""
        self.remove_object()
        name = GAME.OBJ.get_id_info(self.obj_select)[0]
        size = (FULLTILE, FULLTILE)
        entid = self.obj_select
        data = []
        GAME.OBJ.create_object(name, self.pos, data, entid)

    def remove_object(self):
        """Removes object under cursor."""
        obj_copy = GAME.OBJ.obj.copy()
        for element in obj_copy:
            obj = GAME.OBJ.obj[element]
            if obj.pos == self.pos:
                GAME.OBJ.delete(element)

    def place_tile(self):
        layer = list(GAME.TILE.layers.keys())[self.layer]
        pos = f_tupround(f_tupmult(self.pos, 1/HALFTILE), -1)
        GAME.TILE.add_tile(layer, pos, self.tile_map, self.tile_select)

    def remove_tile(self):
        layer = list(GAME.TILE.layers.keys())[self.layer]
        pos = f_tupround(f_tupmult(self.pos, 1/HALFTILE), -1)
        GAME.TILE.remove_tile(layer, pos)

    def view_object_data(self):
        """Print object data or edit it if shift is held."""
        objcopy = GAME.OBJ.obj.copy()
        for element in objcopy:
            obj = GAME.OBJ.obj[element]
            datatype = None
            if obj.pos == self.pos:
                if self.key_shift:
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
        color = f_swatch((7, 0, 7))
        font = 'arial12'

        if self.mode == 0:
            obj = GAME.OBJ.object_names[self.obj_select]
            size = GAME.WIN.fonts[font].size(obj)
            GAME.WIN.draw_rect(self.pos, size, self.color)
            GAME.WIN.draw_text(self.pos, obj, font)
        elif self.mode == 1:

            # Tile
            tile = GAME.TILE.tile_maps[self.tile_map][1][self.tile_select]
            GAME.WIN.draw_image(self.pos, tile)

            # Tilemap name
            tilemap = GAME.TILE.tile_maps[self.tile_map][0]
            GAME.WIN.draw_text((0, HALFTILE), tilemap, font, color)

            # Layer name
            layer = list(GAME.TILE.layers.keys())[self.layer]
            GAME.WIN.draw_text((0, FULLTILE), layer, font, color)
        GAME.WIN.draw_text((0, 0), str(self.pos), font, color)

# Sample of game object (level editor)
class Entity():
    """Sample game object (level editor)."""
    def __init__(self, pos, name, size, color, key, entid, data):
        self.pos = pos
        self.name = name
        self.size = size
        self.color = color
        self.key = key
        self.entid = entid
        self.data = []

    def update(self, dt):
        """Entity update call."""
        pass

    def render_early(self, window):
        """Entity render call."""
        pass

    def render(self, window):
        """Entity render call."""
        window.draw_rect(self.pos, self.size, self.color)

    def render_late(self, window):
        """Entity render call."""
        color = f_cinverse(self.color)
        window.draw_text(self.pos, self.name, 'arial8', color)

# File paths
PATH = {}
PATH['DEFAULT'] = __file__[:-len(os.path.basename(__file__))]
PATH['ASSETS'] = os.path.join(PATH['DEFAULT'], 'Assets')
PATH['SPRITES'] = os.path.join(PATH['ASSETS'], 'Sprites')
PATH['LEVELS'] = os.path.join(PATH['ASSETS'], 'Levels')
PATH['TILEMAPS'] = os.path.join(PATH['ASSETS'], 'Tilemaps')


# main code section
def main():
    """Main level editing loop."""
    clock = pygame.time.Clock()
    dt = 1

    # Gameplay loop
    while GAME.run:
        clock.tick(FPS)
        GAME.input_reset()

        # Event Handler
        events = pygame.event.get()
        for event in events:
            # Exit game
            if event.type == pygame.QUIT:
                GAME.end()
            else:
                GAME.handle_events(event)

        # Quit by escape
        if GAME.KEYBOARD.get_key_pressed(41):
            GAME.end

        # Update
        CUR.update(dt)
        GAME.update(dt)

        # Clear frame
        GAME.WIN.blank()
        GAME.render()
        CUR.render_late()

        # Update display
        pygame.display.update()

        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)

    # Quit pygame
    pygame.quit()

# only run if this file is executed
if __name__ == "__main__":
    # Constant variables
    # Constants variables
    FULLTILE = 32
    HALFTILE = int(FULLTILE/2)
    FPS = 60
    LEVEL_SIZE = (32, 24)
    SIZE = f_tupmult(LEVEL_SIZE, FULLTILE)


    # Game controller
    GAME = Game(SIZE, LEVEL_SIZE, FULLTILE, PATH, f_create_object)

    # Level editing tool
    CUR = Cursor((0, 0))


    # Setup program
    pygame.display.set_caption("Game X - Level Editor")
    GAME.WIN.add_font('arial', 8)


    # Load tilemaps into TILE
    GAME.TILE.load()
    GAME.TILE.add_layer('background', f_tupmult(LEVEL_SIZE, 2))
    GAME.TILE.add_layer('foreground', f_tupmult(LEVEL_SIZE, 2))

    main()
