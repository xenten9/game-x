from os import path, system, name as osname, getpid
from typing import Optional
from time import time
from psutil import Process
from ast import literal_eval

def clear_terminal():
    if osname == 'nt':
        system('cls')
    else:
        system('clear')

clear_terminal()

from pygame.constants import KEYDOWN, QUIT
from pygame.time import Clock
from pygame.event import get as get_events
from pygame import Surface, image

if __name__ == '__main__':
    from engine.types.vector import vec2d
    from engine.engine import Engine
    from engine.components.grid import f_loop, f_limit
    from engine.components.camera import Camera
    from engine.components.draw import Draw
    from engine.components.menu import MenuText
    from engine.components.tile import TileLayer
else:
    from .engine.types.vector import vec2d
    from .engine.engine import Engine
    from .engine.components.grid import f_loop, f_limit
    from .engine.components.camera import Camera
    from .engine.components.draw import Draw
    from .engine.components.menu import MenuText
    from .engine.components.tile import TileLayer

print('All imports finished.')


def create_objects(engine: Engine, **kwargs):
    """Takes in a set of keywords and uses them to make an object.
        engine: engine which contains game components.

        Required kwargs:
        name: name of the object being created.

        Dependent kwargs:
        key: id of the key when created
        pos: position of the created object.
        data: dictionary containing kwargs for __init__."""
    name = kwargs['name']
    key = kwargs['key']
    key = engine.obj.instantiate_key(key)
    pos = kwargs['pos']
    data = kwargs['data']
    Object(engine, name, key, pos, data)


# Constants
if True:
    FULLTILE = 32
    FPS = 60
    SIZE = vec2d(1024, 768)
    PROCESS = Process(getpid())


# Special
class View(Camera):# type: ignore
    """Camera like object which is limited to the inside of the level."""
    def __init__(self, size: vec2d):
        super().__init__(size)
        self.level_size = size

    def pos_get(self) -> vec2d:
        return self._pos

    def pos_set(self, pos: vec2d):
        """Position setter."""
        size0 = self.size
        size1 = self.level_size
        x = f_limit(pos.x, 0, size1.x - size0.x)
        y = f_limit(pos.y, 0, size1.y - size0.y)
        self._pos = vec2d(x, y).floor()

    pos = property(pos_get, pos_set)


# Entities
class Entity():
    """Base class for all game entities."""
    def __init__(self, engine: Engine):
        self.engine = engine

    def update_early(self):
        """Update called first."""
        pass

    def update(self):
        """Update called second."""
        pass

    def update_late(self):
        """Update called last."""
        pass

    def draw(self, draw: Draw):
        """Draw called in between back and foreground."""
        pass


# Game objects
class Object(Entity):
    def __init__(self, engine: Engine, name: str, key: int, pos: vec2d, data: dict):
        self.engine = engine
        self.name = name
        self.key = key
        self.pos = pos
        self.data = data
        engine.obj.instantiate_object(key, self)
        file = path.join(engine.paths['devsprites'], name + '.png')
        self.image = image.load(file)

    def draw(self, draw):
        draw.add(0, pos=self.pos, surface=self.image)

class ObjCursor(Entity):
    def __init__(self, engine: Engine, pos: vec2d):
        # Default variables
        self.engine = engine
        self.pos = pos
        self.color = (192, 192, 192)
        self.name = 'cursor'

        # Modes
        self.mode = 0
        self.obj_select = 0
        self.tile_select = 0
        self.tilemap_select = 0
        self.tilemap_id = engine.til.tilemaps_list[self.tilemap_select]
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

    def update(self):
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
            self.engine.col.st.minimize()
            for layer in self.engine.til.layers:
                layer = self.engine.til.layers[layer]
                layer.minimize()

        # Saving and loading
        if (self.key['save'] and self.key['Hcontrol']
            and not self.mkey['Hplace']):
            self.engine.lvl.save()
            return
        elif (self.key['load'] and self.key['Hcontrol']
              and not self.mkey['Hplace']):
            self.engine.lvl.load()
            self.engine.til.add_all()
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
                self.key[key] = self.engine.inp.kb.get_key_pressed(
                    *self.keys[key])
            else:
                self.key[key] = self.engine.inp.kb.get_key_held(
                    *self.keys[key[1:]])

        for key in self.mkey:
            if key[0] != 'H':
                self.mkey[key] = self.engine.inp.ms.get_button_pressed(
                    *self.mkeys[key])
            else:
                self.mkey[key] = self.engine.inp.ms.get_button_held(
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
            self.engine.obj.toggle_visibility()

        # View/Edit data
        if self.key['tab'] and self.selected_object != None:
            self.view_object_data()

        # Deselect object
        if self.mkey['place']:
            self.selected_object = None

        # Place object
        if self.mkey['Hplace'] and self.key['Hcontrol']:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                self.place_object()
        # Select and move object
        elif self.mkey['Hplace']:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
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
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['remove']:
                self.pos = pos
                self.remove_object()

    def mode1(self):
        """Tile mode."""
        # Layer selection
        self.layer += self.key['nextlayer'] - self.key['prevlayer']
        length = len(self.engine.til.layers)-1

        # Layer creation
        if self.layer > length or self.layer < 0:
            if self.key['Hshift'] and self.key['Hcontrol']:
                name = self._get_data(
                    'Enter layer name: ', 'Name must be string',
                    '', str)
                depth = self._get_data(
                    'Enter layer depth: ', 'Depth must be an int',
                    'Layer Successfully Created!', int)
                if name is not None and depth is not None:
                    self.engine.til.add_layer(name, vec2d(6, 6), {'depth': depth})
                    self.engine.til.layers[name].cache()
                    length += 1
                else:
                    self.layer -= 1

        # Layer deletion
        if self.key['delete'] and length > 0:
            if self.key['Hshift'] and self.key['Hcontrol']:
                layer = self._get_current_layer()
                self.engine.til.remove_layer(layer.name)
                length -= 1

        self.layer = f_loop(self.layer, 0, length)

        # Tilemap selection
        dset = self.key['nextset'] - self.key['prevset']
        if dset != 0:
            self.tile_select = 0
            self.tilemap_select += dset
            length = len(self.engine.til.tilemaps_list)-1

            self.tilemap_select = f_loop(self.tilemap_select, 0, length)
            self.tilemap_id = self.engine.til.tilemaps_list[self.tilemap_select]
            self.tilemap = self._get_current_tilemap()

        # Changing selection
        dtile = (self.key['next'] - self.key['prev'])
        if dtile != 0:
            self.tile_select += dtile
            length = len(self.tilemap)-1
            self.tile_select = f_loop(self.tile_select, 0, length)

        # Toggling tile maps
        if self.key['f1']:
            layer = list(self.engine.til.layers.keys())[self.layer]
            self.engine.til.layers[layer].toggle_visibility()

        # View/Edit data
        if self.key['tab']:
            layer = self._get_current_layer()
            if self.key['Hshift']:
                text = self._get_data(
                    'Enter Data Dict: ', 'Input must be Dict',
                    'Data Successfully Written', dict)
                if text is not None:
                    layer.data = text
                    layer.update()
            else:
                print(layer.data)

        # Mouse
        # Place tile
        if self.mkey['Hplace'] and self.key['Hcontrol']:
            # Update position
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE//2)
            if self.pos != pos or self.mkey['place']:
                self.pos = pos
                self.place_tile()

        # Remove tile
        elif self.mkey['Hremove'] and self.key['Hcontrol']:
            # Update position
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE//2)
            if self.pos != pos or self.mkey['remove']:
                self.pos = pos
                self.remove_tile()

    def mode2(self):
        # Wall mode
        if self.key['f1']:
            self.engine.col.st.toggle_visibility()

        # Place object
        if self.mkey['Hplace']:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['place']:
                self.pos = pos
                self.engine.col.st.add(pos)

        # Remove object
        elif self.mkey['Hremove']:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey['remove']:
                self.pos = pos
                self.engine.col.st.remove(pos)

    def get_overlaping_object(self) -> Optional[Object]:
        """Find if object is under cursor."""
        for key in self.engine.obj.obj:
            obj = self.engine.obj.obj[key]
            if obj.pos == self.pos and obj.name != self.name:
                return obj
        return None

    def place_object(self):
        """Places object under cursor."""
        self.remove_object()
        name = self.object_names[self.obj_select]
        self.engine.obj.create_object(name=name, game=self.engine, key=None, pos=self.pos, data={})

    def remove_object(self):
        """Removes object under cursor."""
        obj = self.get_overlaping_object()
        while obj is not None:
            self.engine.obj.delete(obj.key)
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

    def draw(self, draw: Draw):
        """Draw cursor and debug text."""
        #color = (224, 128, 224)

        element = self.engine.debug.menu.get('curpos')
        element.text = 'pos: ({:.0f}, {:.0f})'.format(*self.pos)

        if self.mode == 0:
            # Object name
            element = self.engine.debug.menu.get('mode')
            text = self.object_names[self.obj_select]
            element.text = 'Object: {}'.format(text)

        elif self.mode == 1:
            # Tile image
            surface = self._get_current_tile()
            pos = self.pos
            self.engine.draw.add(4, pos=pos, surface=surface)

            # Layer name
            element = self.engine.debug.menu.get('mode')
            text = self._get_current_layer().name
            element.text = 'Layer: {}'.format(text)

        elif self.mode == 2:
            # Wall
            element = self.engine.debug.menu.get('mode')
            element.text = 'Wall mode'

    def _get_current_layer(self) -> TileLayer:
        return self.engine.til.layers[list(self.engine.til.layers.keys())[self.layer]]

    def _get_current_tilemap(self) -> list:
        return self.engine.til.tilemaps[self.tilemap_id]

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


# Main application functions
def main():
    clock = Clock()
    engine = Engine(FULLTILE, FPS, SIZE, True)

    cursor = ObjCursor(engine, vec2d(0, 0))
    engine.debug.menu.remove('rect')
    ele = MenuText(engine, engine.debug.menu, 'curpos')
    ele.pos = vec2d(0, 12*3)
    ele = MenuText(engine, engine.debug.menu, 'mode')
    ele.pos = vec2d(0, 12*4)

    engine.init_obj(create_objects)
    cam = View(SIZE)
    engine.set_cam(cam)

    engine.lvl.load('default')
    engine.til.add_all()

    if engine.debug:
        engine.debug.time_record = {
            'Update': 0.0,
            'Draw': 0.0,
            'Render': 0.0}

    while engine.run:
        # Event handler
        event_handle(engine)

        # Updating
        update(engine)
        cursor.update()
        update_debug(engine, clock)

        # Drawing
        draw(engine)
        cursor.draw(engine.draw)

        # Rendering
        render(engine)

        # Maintain FPS
        clock.tick(FPS)
        if engine.debug:
            engine.debug.tick()

def event_handle(engine: Engine):
    """Handles events."""
    engine.inp.reset()
    events = get_events()
    for event in events:
        if event.type == KEYDOWN:
            #print(event.scancode)
            pass
        engine.inp.handle_events(event)
        if event.type == QUIT:
            engine.end()
            return
    if engine.inp.kb.get_key_pressed(41):
        engine.end()
        return

def update(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.obj.update_early()
    engine.obj.update()
    engine.obj.update_late()
    if engine.debug:
        engine.debug.time_record['Update'] += (time() - t)

def update_debug(engine: Engine, clock: Clock):
    debug = engine.debug
    if debug:
            fps = debug.menu.get('fps')
            fps.text = 'fps: {:.0f}'.format(clock.get_fps())

            campos = debug.menu.get('campos')
            campos.text = 'cam pos: {}'.format(engine.cam.pos)

            memory = debug.menu.get('memory')
            mem = PROCESS.memory_info().rss
            mb = mem // (10**6)
            kb = (mem - (mb * 10**6)) // 10**3
            memory.text = 'memory: {} MB, {} KB'.format(mb, kb)

def draw(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.draw.draw()
    engine.debug.menu.draw(engine.draw)
    engine.col.st.debug_draw(engine.draw)
    if engine.debug:
        engine.debug.time_record['Draw'] += (time() - t)

def render(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.win.blank()
    engine.cam.blank()
    engine.draw.render(engine.cam)
    engine.win.render(engine.cam)
    engine.win.update()
    if engine.debug:
        engine.debug.time_record['Render'] += (time() - t)


if __name__ == '__main__':
    main()
