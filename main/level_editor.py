from os import path, getcwd
from ast import literal_eval
from typing import Optional

from pygame import image, event as pyevent, Surface
from pygame.time import Clock
from pygame.locals import QUIT

if __name__ != '__main__':
    from .engine.components.camera import ObjCamera
    from .engine.engine import ObjGameHandler, f_loop
    from .engine.helper_functions.tuple_functions import (
        f_tupadd, f_tupgrid, f_tupmult)
else:
    from engine.components.camera import ObjCamera
    from engine.engine import ObjGameHandler, f_loop
    from engine.helper_functions.tuple_functions import (
        f_tupadd, f_tupgrid, f_tupmult)

print('################')
SIZE = (1024, 768)
FULLTILE = 32
HALFTILE = 16
FPS = 60

PATH = {}
PATH['MAIN'] = getcwd()
PATH['ASSETS'] = path.join(PATH['MAIN'], 'assets')
PATH['SPRITES'] = path.join(PATH['ASSETS'], 'sprites')
PATH['DEVSPRITES'] = path.join(PATH['ASSETS'], 'dev_sprites')
PATH['LEVELS'] = path.join(PATH['ASSETS'], 'levels')
PATH['TILEMAPS'] = path.join(PATH['ASSETS'], 'tilemaps')
PATH['MUSIC'] = path.join(PATH['ASSETS'], 'music')
PATH['SFX'] = path.join(PATH['ASSETS'], 'sfx')

def object_creator(**kwargs):
    name = kwargs['name']
    game = kwargs['game']
    pos = kwargs['pos']
    key = kwargs['key']
    data = kwargs['data']
    key = game.obj.instantiate_key(key)
    ObjEntity(game, name, key, pos, data)

class Entity():
    """Base class for all game entities."""
    def draw_early(self, window: object):
        """Draw called before background."""
        pass

    def draw(self, window: object):
        """Draw called in between back and foreground."""
        pass

    def draw_late(self, window: object):
        """Draw called after foreground."""
        pass

    def update_early(self, dt: float):
        """Update called first."""
        pass

    def update(self, dt: float):
        """Update called second."""
        pass

    def update_late(self, dt: float):
        """Update called last."""
        pass

class ObjView(ObjCamera):
    def __init__(self, game: object, size: tuple):
        super().__init__(size)
        self.game = game
        self.keys = {
            'left': (4, 80),
            'right': (7, 79),
            'up': (26, 82),
            'down': (22, 81)}

        self.key = {
            'left': 0,
            'right': 0,
            'up': 0,
            'down': 0}

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos: tuple):
        if pos[0] < 0:
            pos = (0, pos[1])
        if pos[1] < 0:
            pos = (pos[0], 0)
        self._pos = pos

    def update(self, dt: float):
        self.get_inputs()
        hspd = (self.key['right'] - self.key['left']) * FULLTILE
        vspd = (self.key['down'] - self.key['up']) * FULLTILE
        self.pos = f_tupadd(self.pos, (hspd, vspd))

    def get_inputs(self):
        for key in self.key:
                if key[0] != 'H':
                    self.key[key] = self.game.input.kb.get_key_pressed(
                        *self.keys[key])
                else:
                    self.key[key] = self.game.input.kb.get_key_held(
                        *self.keys[key[1:]])

class ObjCursor(Entity):
    def __init__(self, game: object, pos: tuple):
        # Default variables
        self.game = game
        self.pos = pos
        self.color = (192, 192, 192)
        self.name = 'cursor'

        # Modes
        self.mode = 0
        self.obj_select = 0
        self.tile_select = 0
        self.tile_map = 0
        self.layer = 0
        self.selected_object = None

        # Names
        self.object_names = [
            'player',
            'button',
            'door',
            'grav-orb',
            'spike',
            'spike-inv',
            'juke-box']

        # Input keys
        self.keys = {
            # Keyboard
            'save': (22,),
            'load': (15,),
            'modeup': (16,),
            'modedown': (17,),
            'next': (8,),
            'prev': (20,),
            'f1': (58,),
            'tab': (43,),
            'shift': (225,),
            'control': (224,),
            'nextset': (27,),
            'prevset': (29,),
            'nextlayer': (25,),
            'prevlayer': (6,),
            'reload': (21,)}

        self.mkeys = {
            'place': (1,),
            'remove': (3,)}

        # input vars
        self.key = {
            # Keyboard
            'save': 0,
            'load': 0,
            'modeup': 0,
            'modedown': 0,
            'next': 0,
            'prev': 0,
            'f1': 0,
            'tab': 0,
            'shift': 0,
            'control': 0,
            'Hcontrol': 0,
            'Hshift': 0,
            'nextset': 0,
            'prevset': 0,
            'nextlayer': 0,
            'prevlayer': 0,
            'reload': 0}

        self.mkey = {
            'place': 0,
            'Hplace': 0,
            'remove': 0,
            'Hremove': 0}

    def update(self, dt: float):
        """Update cursor pos and level changes."""
        # Get inputs
        self.get_inputs()

        # Change modes
        if self.key['modeup'] or self.key['modedown']:
            self.mode += self.key['modeup'] - self.key['modedown']
            self.pos = f_tupgrid(self.pos, FULLTILE)
        self.mode = f_loop(self.mode, 0, 2)

        # Reload # NOTE # use before saving level in order to shrink grids
        if self.key['reload'] and self.key['Hcontrol']:
            self.game.collider.st.minimize()
            for layer in self.game.tile.layers:
                layer = self.game.tile.layers[layer]
                layer.minimize()

        # Saving and loading
        if self.key['save'] and self.key['Hcontrol']:
            self.game.level.save()
        elif self.key['load'] and self.key['Hcontrol']:
            self.game.level.load()

        # State machine
        if self.mode == 0: # Object mode
            self.mode0()
        elif self.mode == 1: # Tile mode
            self.mode1()
        elif self.mode == 2: # Wall mode
            self.mode2()

    def get_inputs(self):
        """Register inputs and change variables."""
        for key in self.key:
            if key[0] != 'H':
                self.key[key] = self.game.input.kb.get_key_pressed(
                    *self.keys[key])
            else:
                self.key[key] = self.game.input.kb.get_key_held(
                    *self.keys[key[1:]])

        for key in self.mkey:
            if key[0] != 'H':
                self.mkey[key] = self.game.input.ms.get_button_pressed(
                    *self.mkeys[key])
            else:
                self.mkey[key] = self.game.input.ms.get_button_held(
                    *self.mkeys[key[1:]])

    def mode0(self):
        """Object mode."""
        # Changing selection
        dobj = self.key['next'] - self.key['prev']
        if dobj != 0:
            self.obj_select += dobj
            length = len(self.object_names) - 1
            self.obj_select = f_loop(self.obj_select, 0, length)

        # Toggling objects
        if self.key['f1']:
            self.game.obj.toggle_visibility()

        # View/Edit data
        if self.key['tab'] and self.selected_object != None:
            self.view_object_data()

        # Deselect object
        if self.mkey['place']:
            self.selected_object = None

        # Place object
        if self.mkey['Hplace'] and self.key['Hcontrol']:
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                self.place_object()
        # Select and move object
        elif self.mkey['Hplace']:
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                obj = self.selected_object
                if obj is not None:
                    if obj.pos != pos:
                        obj.pos = pos
                    self.selected_object = obj
                self.selected_object = self.get_overlaping_object()

        # Remove object
        elif self.mkey['Hremove'] and self.key['Hcontrol']:
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, FULLTILE)
            if pos != self.pos or self.mkey['remove']:
                self.pos = pos
                self.remove_object()

    def mode1(self):
        """Tile mode."""
        # Layer selection
        self.layer += self.key['nextlayer'] - self.key['prevlayer']
        length = len(self.game.tile.layers)-1
        self.layer = f_loop(self.layer, 0, length)

        # Tilemap selection
        dset = self.key['nextset'] - self.key['prevset']
        if dset != 0:
            self.tile_select = 0
            self.tile_map += dset
            length = len(self.game.tile.tile_maps)-1
            self.tile_map = f_loop(self.tile_map, 0, length)

        # Changing selection
        dtile = (self.key['next'] - self.key['prev'])
        if dtile != 0:
            self.tile_select += dtile
            length = len(self.game.tile.tile_maps[self.tile_map])-1
            self.tile_select = f_loop(self.tile_select, 0, length)

        # Toggling tile maps
        if self.key['f1']:
            layer = list(self.game.tile.layers.keys())[self.layer]
            self.game.tile.layers[layer].toggle_visibility()

        # View/Edit data
        if self.key['tab']:
            if self.key['Hshift']:
                text = ''
                while True:
                    text = input('Edit data? ')
                    try:
                        text = literal_eval(text)
                    except (SyntaxError, ValueError):
                        if text == 'exit':
                            break
                        print('input must be dictionary')
                        continue
                    if text == 'exit':
                            break
                    if not isinstance(text, dict):
                        print('input must be dictionary')
                    else:
                        break
                if text != 'exit':
                    layer = self.get_current_layer().data = text
                    print('data succesfully written.')
            else:
                layer = self.get_current_layer()
                print(layer.data)

        # Mouse
        # Place tile
        if self.mkey['Hplace'] and self.key['Hcontrol']:
            # Update position
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, HALFTILE)
            if self.pos != pos or self.mkey['place']:
                self.pos = pos
                self.place_tile()

        # Remove tile
        elif self.mkey['Hremove'] and self.key['Hcontrol']:
            # Update position
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, HALFTILE)
            if self.pos != pos or self.mkey['remove']:
                self.pos = pos
                self.remove_tile()

    def mode2(self):
        # Wall mode
        if self.key['f1']:
            self.game.collider.st.toggle_visibility()

        # Place object
        if self.mkey['Hplace']:
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                self.game.collider.st.add(pos)

        # Remove object
        elif self.mkey['Hremove']:
            pos = f_tupadd(self.game.input.ms.get_pos(), self.game.cam.pos)
            pos = f_tupgrid(pos, FULLTILE)
            if pos != self.pos or self.mkey['remove']:
                self.pos = pos
                self.game.collider.st.remove(pos)

    def get_overlaping_object(self) -> Optional[object]:
        """Find if object is under cursor."""
        for key in self.game.obj.obj:
            obj = self.game.obj.obj[key]
            if obj.pos == self.pos and obj.name != self.name:
                return obj
        return None

    def place_object(self):
        """Places object under cursor."""
        self.remove_object()
        name = self.object_names[self.obj_select]
        self.game.obj.create_object(name=name, game=self.game, key=None, pos=self.pos, data={})

    def remove_object(self):
        """Removes object under cursor."""
        obj = self.get_overlaping_object()
        while obj is not None:
            self.game.obj.delete(obj.key)
            obj = self.get_overlaping_object()

    def place_tile(self):
        """Places tile under cursor."""
        layer = self.get_current_layer()
        layer.place(self.pos, self.tile_map, self.tile_select)
        layer.generate()

    def remove_tile(self):
        """Removes tile under cursor."""
        layer = self.get_current_layer()
        layer.remove(self.pos)
        layer.generate()

    def get_current_layer(self) -> object:
        return self.game.tile.layers[list(self.game.tile.layers.keys())[self.layer]]

    def get_current_tilemap(self) -> list:
        return self.game.tile.tile_maps[self.tile_map]

    def get_current_tile(self) -> Surface:
        return self.get_current_tilemap()[self.tile_select]

    def view_object_data(self):
        """Print object data or edit it if shift is held."""
        obj = self.selected_object
        if self.key['Hshift']:
            text = ''
            while True:
                try:
                    text = literal_eval(input('Edit data? '))
                except (SyntaxError, ValueError):
                    print('input must be list')
                    continue
                if text == 'exit':
                    break
                if not isinstance(text, dict):
                    print('input must be dictionary')
                else:
                    break
            if text != 'exit':
                obj.data = text
                print('data succesfully written.')

        else:
            info = ['name: {}'.format(obj.name),
                    'id: {}'.format(obj.key),
                    'data: {}'.format(obj.data)]
            print('\n'.join(info))

    def draw_late(self, window: object):
        """Draw cursor and debug text."""
        color = (224, 128, 224)
        font = self.game.font.get('arial', 12)

        text = 'pos: ({:.0f}, {:.0f})'.format(*self.pos)
        window.draw_text((0, 0), text, font, color, gui=1)

        if self.mode == 0:
            obj = self.object_names[self.obj_select]
            size = font.size(obj)
            window.draw_text((0, HALFTILE), obj, font, color, gui=1)

        elif self.mode == 1:
            # Tile
            tile = self.get_current_tile()
            window.draw_image(f_tupadd(f_tupmult(self.game.cam.pos, -1),
                                       self.pos), tile, gui=1)

            # Layer name
            layer = self.get_current_layer()
            window.draw_text((0, HALFTILE), layer.name, font, color, gui=1)

        elif self.mode == 2:
            # Wall
            window.draw_text((0, HALFTILE), 'Wall mode', font, color, gui=1)

class ObjEntity(Entity):
    def __init__(self, game: object, name: str, key: int, pos: tuple, data: dict):
        self.game = game
        self.name = name
        self.key = key
        self.pos = pos
        self.data = data
        game.obj.instantiate_object(key, self)
        self.image = image.load(path.join(PATH['DEVSPRITES'], name + '.png'))

    def draw(self, window):
        window.draw_image(self.pos, self.image)

def main():
    """Main game loop."""
    GAME = ObjGameHandler(SIZE, FULLTILE, PATH, object_creator)
    GAME.cam = ObjView(GAME, SIZE)
    GAME.tile.add_tilemap('0-tileset0.png')
    GAME.tile.add_tilemap('1-background0.png')
    GAME.level.load('default')
    GAME.parallax = 0
    CUR = ObjCursor(GAME, (0, 0))

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
        GAME.obj.update_early(dt)
        GAME.obj.update(dt)
        GAME.obj.update_late(dt)
        CUR.update(dt)
        GAME.cam.update(dt)

        # Draw all
        GAME.cam.blank()

        # Draw background layers
        GAME.obj.draw_early(GAME.cam)
        GAME.tile.layers['background'].draw(GAME.cam)

        # Draw objects
        GAME.obj.draw(GAME.cam)
        GAME.collider.st.debug_draw(GAME.cam)

        # Draw foreground layers
        GAME.tile.layers['foreground'].draw(GAME.cam)
        GAME.obj.draw_late(GAME.cam)
        CUR.draw_late(GAME.cam)

        # FPS display
        fps = 'fps: {:3f}'.format(clock.get_fps())
        font = GAME.font.get('arial', 12)
        GAME.cam.draw_text((0, FULLTILE), fps, font, (255, 0, 255), gui=1)

        # Render to screen
        GAME.window.render(GAME.cam)

        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)


if __name__ == '__main__':
    main()

