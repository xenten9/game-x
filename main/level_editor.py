"""Game-X level editor."""
# OS import
from os import path, getcwd, system, name as osname, getpid
import sys
from psutil import Process

# Clear terminal
if osname == 'nt':
    system('cls')
else:
    system('clear')
print('################') # sepperator

# Base imports
from ast import literal_eval
from typing import Optional
import numpy as np

# Library imports
from pygame import image, event as pyevent, Surface
from pygame.time import Clock
from pygame.locals import QUIT

# Custom imports
if __name__ != '__main__': # If main file
    from .engine.components.camera import ObjCamera
    from .engine.engine import ObjGameHandler, f_loop
    from .engine.components.vector import vec2d
    from .engine.components.menu import ObjTextElement
else: # If being called as a module
    from engine.components.camera import ObjCamera
    from engine.engine import ObjGameHandler, f_loop
    from engine.components.vector import vec2d
    from engine.components.menu import ObjTextElement

print('################')


if True:
    SIZE = vec2d(1024, 768)
    FULLTILE = 32
    HALFTILE = 16
    FPS = 60
    PROCESS = Process(getpid())

    PATH = {}
    if getattr(sys, 'frozen', False):
        PATH['MAIN'] = path.dirname(sys.executable)
    else:
        PATH['MAIN'] = getcwd()
    PATH['DEBUGLOG'] = path.join(PATH['MAIN'], 'debug')
    PATH['ASSETS'] = path.join(PATH['MAIN'], 'assets')
    PATH['SPRITES'] = path.join(PATH['ASSETS'], 'sprites')
    PATH['DEVSPRITES'] = path.join(PATH['ASSETS'], 'dev_sprites')
    PATH['LEVELS'] = path.join(PATH['ASSETS'], 'levels')
    PATH['TILEMAPS'] = path.join(PATH['ASSETS'], 'tilemaps')
    PATH['MUSIC'] = path.join(PATH['ASSETS'], 'music')
    PATH['SFX'] = path.join(PATH['ASSETS'], 'sfx')


# Object Creation functions # NOTE # Slightly hard coded
def object_creator(**kwargs):
    name = kwargs['name']
    game = kwargs['game']
    pos = kwargs['pos']
    key = kwargs['key']
    data = kwargs['data']
    key = game.obj.instantiate_key(key)
    ObjEntity(game, name, key, pos, data)


# Special classes
class ObjView(ObjCamera):
    """Movable camera like object."""
    def __init__(self, game: object, size: vec2d):
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
        self.rel = vec2d(0, 0)

    @property
    def pos(self):
        """Pos getter."""
        return self._pos

    @pos.setter
    def pos(self, pos: vec2d):
        """Pos setter."""
        if pos.x < 0:
            pos = vec2d(0, pos.y)
        if pos.y < 0:
            pos = vec2d(pos.x, 0)
        self._pos = pos

    def update(self, dt: float):
        """Move the camera."""
        self.get_inputs()
        # Keyboard movement
        hspd = (self.key['right'] - self.key['left']) * FULLTILE
        vspd = (self.key['down'] - self.key['up']) * FULLTILE

        # Mouse movement
        if self.game.input.ms.get_button_held(2):
            self.rel += self.game.input.ms.get_delta()
            dx = abs(self.rel.x) // FULLTILE * np.sign(self.rel.x) * FULLTILE
            dy = abs(self.rel.y) // FULLTILE * np.sign(self.rel.y) * FULLTILE
            if dx != 0:
                hspd -= dx
                self.rel -= vec2d(dx, 0)
            if dy != 0:
                vspd -= dy
                self.rel -= vec2d(0, dy)
        else:
            self.rel = vec2d(0, 0)

        # Move camera
        self.pos = self.pos + vec2d(hspd, vspd)

    def get_inputs(self):
        """Get inputs."""
        for key in self.key:
                if key[0] != 'H':
                    self.key[key] = self.game.input.kb.get_key_pressed(
                        *self.keys[key])
                else:
                    self.key[key] = self.game.input.kb.get_key_held(
                        *self.keys[key[1:]])


# Entities
class Entity():
    """Base class for all game entities."""
    def update_early(self, dt: float):
        """Update called first."""
        pass

    def update(self, dt: float):
        """Update called second."""
        pass

    def update_late(self, dt: float):
        """Update called last."""
        pass

    def draw(self, window: object):
        """Draw called in between back and foreground."""
        pass

class ObjCursor(Entity):
    def __init__(self, game: object, pos: vec2d):
        # Default variables
        self.game = game
        self.pos = pos
        self.color = (192, 192, 192)
        self.name = 'cursor'

        # Modes
        self.mode = 0
        self.obj_select = 0
        self.tile_select = 0
        self.tilemap_select = 0
        self.tilemap_id = game.tile.tilemaps_list[self.tilemap_select]
        self.tilemap = self._get_current_tilemap()
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
            'juke-box',
            'main-menu']

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
            'delete': (76,),
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
            'delete': 0,
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
            self.pos = self.pos.grid(FULLTILE)
        self.mode = f_loop(self.mode, 0, 2)

        # Reload # NOTE # use before saving level in order to shrink grids
        if self.key['reload'] and self.key['Hcontrol']:
            self.game.collider.st.minimize()
            for layer in self.game.tile.layers:
                layer = self.game.tile.layers[layer]
                layer.minimize()

        # Saving and loading
        if (self.key['save'] and self.key['Hcontrol']
            and not self.mkey['Hplace']):
            self.game.level.save()
            return
        elif (self.key['load'] and self.key['Hcontrol']
              and not self.mkey['Hplace']):
            self.game.level.load()
            self.game.tile.add_all()
            return

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
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                self.place_object()
        # Select and move object
        elif self.mkey['Hplace']:
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(FULLTILE)
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
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['remove']:
                self.pos = pos
                self.remove_object()

    def mode1(self):
        """Tile mode."""
        # Layer selection
        self.layer += self.key['nextlayer'] - self.key['prevlayer']
        length = len(self.game.tile.layers)-1

        # Layer creation
        if self.layer > length or self.layer < 0:
            if self.key['Hshift'] and self.key['Hcontrol']:
                name = self._get_data(
                    'Enter layer name: ', 'Name must be string',
                    '', str)
                depth = self._get_data(
                    'Enter layer depth: ', 'Depth must be an int',
                    'Layer Successfully Created!', int)
                self.game.tile.add_layer(name, vec2d(6, 6), {'depth': depth})
                self.game.tile.layers[name].cache()
                length += 1

        # Layer deletion
        if self.key['delete'] and length > 0:
            if self.key['Hshift'] and self.key['Hcontrol']:
                layer = self._get_current_layer()
                self.game.tile.remove_layer(layer.name)
                length -= 1

        self.layer = f_loop(self.layer, 0, length)

        # Tilemap selection
        dset = self.key['nextset'] - self.key['prevset']
        if dset != 0:
            self.tile_select = 0
            self.tilemap_select += dset
            length = len(self.game.tile.tilemaps_list)-1

            self.tilemap_select = f_loop(self.tilemap_select, 0, length)
            self.tilemap_id = self.game.tile.tilemaps_list[self.tilemap_select]
            self.tilemap = self._get_current_tilemap()

        # Changing selection
        dtile = (self.key['next'] - self.key['prev'])
        if dtile != 0:
            self.tile_select += dtile
            length = len(self.tilemap)-1
            self.tile_select = f_loop(self.tile_select, 0, length)

        # Toggling tile maps
        if self.key['f1']:
            layer = list(self.game.tile.layers.keys())[self.layer]
            self.game.tile.layers[layer].toggle_visibility()

        # View/Edit data
        if self.key['tab']:
            layer = self._get_current_layer()
            if self.key['Hshift']:
                text = self._get_data(
                    'Enter Data Dict: ', 'Input must be Dict',
                    'Data Successfully Written', dict)
                if text is not None:
                    layer.data = text
                    layer.update(1)
            else:
                print(layer.data)

        # Mouse
        # Place tile
        if self.mkey['Hplace'] and self.key['Hcontrol']:
            # Update position
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(HALFTILE)
            if self.pos != pos or self.mkey['place']:
                self.pos = pos
                self.place_tile()

        # Remove tile
        elif self.mkey['Hremove'] and self.key['Hcontrol']:
            # Update position
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(HALFTILE)
            if self.pos != pos or self.mkey['remove']:
                self.pos = pos
                self.remove_tile()

    def mode2(self):
        # Wall mode
        if self.key['f1']:
            self.game.collider.st.toggle_visibility()

        # Place object
        if self.mkey['Hplace']:
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                self.game.collider.st.add(pos)

        # Remove object
        elif self.mkey['Hremove']:
            pos = self.game.input.ms.get_pos() + self.game.cam.pos
            pos = pos.grid(FULLTILE)
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
        layer = self._get_current_layer()
        tile_map = self.tilemap_id
        layer.place(self.pos, tile_map, self.tile_select)
        layer.cache_partial(self.pos)

    def remove_tile(self):
        """Removes tile under cursor."""
        layer = self._get_current_layer()
        layer.remove(self.pos)
        layer.cache_partial(self.pos)

    def view_object_data(self):
        """Print object data or edit it if shift is held."""
        obj = self.selected_object
        if self.key['Hshift']:
            text = ''
            while True:
                text = input('Edit data? ')
                try:
                    text = literal_eval(text)
                except (SyntaxError, ValueError):
                    if text == 'exit':
                        break
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

    def draw(self):
        """Draw cursor and debug text."""
        #color = (224, 128, 224)

        text = 'pos: ({:.0f}, {:.0f})'.format(*self.pos)
        element = self.game.debug.menu.get('curpos')
        res = element.set_vars(text=text)

        if self.mode == 0:
            # Object name
            text = self.object_names[self.obj_select]
            text = 'Object: {}'.format(text)
            element = self.game.debug.menu.get('mode')
            res = element.set_vars(text=text)


        elif self.mode == 1:
            # Tile image
            surface = self._get_current_tile()
            pos = self.pos
            self.game.draw.add(4, pos=pos, surface=surface)

            # Layer name
            text = self._get_current_layer().name
            text = 'Layer: {}'.format(text)
            element = self.game.debug.menu.get('mode')
            res = element.set_vars(text=text)

        elif self.mode == 2:
            # Wall
            text = 'Wall mode'
            element = self.game.debug.menu.get('mode')
            res = element.set_vars(text=text)

        if res:
            self.game.debug.menu.draw()

    def _get_current_layer(self) -> object:
        return self.game.tile.layers[list(self.game.tile.layers.keys())[self.layer]]

    def _get_current_tilemap(self) -> list:
        return self.game.tile.tilemaps[self.tilemap_id]

    def _get_current_tile(self) -> Surface:
        return self.tilemap[self.tile_select]

    def _get_data(self, prompt: str, error: str, success: str, datatype: type):
        text = ''
        while True:
            text = input(prompt)
            try:
                text = literal_eval(text)
            except (SyntaxError, ValueError):
                if text == 'exit':
                    break
                print(error)
                continue
            if text == 'exit':
                    break
            if not isinstance(text, datatype):
                print(error)
            else:
                break
        if text != 'exit':
            print(success)
            return text
        return None

class ObjEntity(Entity):
    def __init__(self, game: object, name: str, key: int, pos: vec2d, data: dict):
        self.game = game
        self.name = name
        self.key = key
        self.pos = pos
        self.data = data
        game.obj.instantiate_object(key, self)
        self.image = image.load(path.join(PATH['DEVSPRITES'], name + '.png'))

    def draw(self):
        self.game.draw.add(0, pos=self.pos, surface=self.image)



# Main application method
def main(debug: bool = False):
    """Main game loop."""
    GAME = ObjGameHandler(SIZE, FULLTILE, PATH, object_creator,
                          fps=FPS, debug=debug)
    GAME.cam = ObjView(GAME, SIZE)
    GAME.level.load('default')
    GAME.tile.add_all()
    GAME.parallax = 0
    CUR = ObjCursor(GAME, vec2d(0, 0))
    if GAME.debug:
        GAME.debug.menu.get('fps').set_vars(backdrop=0)
        GAME.debug.menu.get('campos').set_vars(backdrop=0)
        GAME.debug.menu.get('memory').set_vars(backdrop=0)
        size = 12
        font = 'consolas'
        pos = vec2d(0, 12*3)
        element = ObjTextElement(GAME.debug.menu, 'curpos')
        element.set_vars(size=size, font=font, pos=pos)
        pos += vec2d(0, 12)
        element = ObjTextElement(GAME.debug.menu, 'mode')
        element.set_vars(size=size, font=font, pos=pos)

    clock = Clock()
    dt = 1

    while GAME.run:
        # Reset inputs for held keys
        GAME.input.reset()

        # Event Handler
        for event in pyevent.get():
            # Exit game
            if event.type == QUIT:
                return
            else:
                GAME.input.handle_events(event)
        if GAME.input.kb.get_key_pressed(41):
            GAME.end()
            return

        # Update objects
        update(GAME, dt)
        CUR.update(dt)

        # Draw objects and tile layers
        CUR.draw()
        draw(GAME)

        # Debug display
        if GAME.debug:
            fps = GAME.debug.menu.get('fps')
            text = 'fps: {:.0f}'.format(clock.get_fps())
            fps.set_vars(text=text)

            campos = GAME.debug.menu.get('campos')
            text = 'cam pos: {}'.format(GAME.cam.pos)
            campos.set_vars(text=text)

            memory = GAME.debug.menu.get('memory')
            mem = PROCESS.memory_info().rss
            mb = mem // (10**6)
            kb = (mem - (mb * 10**6)) // 10**3
            text = 'memory: {} MB, {} KB'.format(mb, kb)
            memory.set_vars(text=text)

        # Render to screen
        render(GAME)

        # Tick clock
        dt = clock.tick(FPS)
        dt *= (FPS / 1000)

def update(game: object, dt: float):
    game.obj.update_early(dt)
    game.obj.update(dt)
    game.obj.update_late(dt)
    game.cam.update(dt)

def draw(game: object):
    cam = game.cam

    cam.blank()
    game.collider.st.debug_draw(game.draw)
    game.draw.draw()
    game.debug.menu.draw()
    game.draw.render(cam)

def render(game: object):
    game.window.render(game.cam)


# If main file
if __name__ == '__main__':
    main(True)

