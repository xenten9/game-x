"""Loads and saves levels from disk."""
# Standard library
from os import path
from ast import literal_eval
from typing import Union
import json

# Local imports
from ...constants import colorize, cprint
from ..types.component import Component
from ..types.vector import vec2d
from ..types.component import Component
from .tile import TileLayer

# Handles level loading
class Level(Component):
    """Object which loads and saves levels."""
    def __init__(self, engine: object):
        super().__init__(engine)
        self.current_level = ''
        self.size = vec2d(0, 0)

    def load(self, level_name: Union[str, None] = None):
        """Load level parts such as GameObjects and Tiles."""
        # Get level name
        if level_name is None:
            while level_name in ('', None):
                level_name = input('load level name? ')
                if level_name in ('', None):
                    cprint('improper level name.', 'yellow')
                elif level_name == 'exit':
                    return
                else:
                    level = path.join(self.paths['levels'], level_name+'.json')
                    if not path.exists(level):
                        level_name = None
                        cprint('improper level name.', 'yellow')
        else:
            level = path.join(self.paths['levels'], level_name+'.json')
            if not path.exists(level):
                code = ['LEVEL ERROR',
                        'path: {}'.format(level),
                        'level name: {}'.format(level_name),
                        'level not found']
                raise Exception(colorize('\n'.join(code), 'red'))

        # Load level file
        if not isinstance(level_name, str):
            return
        level_name = path.join(self.paths['levels'], level_name)
        a = open(level_name+'.json', 'r')
        b = a.read()
        a.close()
        b = json.loads(b)
        obj_list = []
        for c in b:
            # Parse all objects in list
            name = c[0]
            if name == 'tile-layer':
                layername, array, data = c[1:4]
                for column, _ in enumerate(array):
                    for row, cell in enumerate(array[column]):
                        if cell is not None:
                            array[column][row] = tuple(cell)
                data = dict(data)
                obj_list.append([name, layername, array, data])

            elif name == 'static-collider':
                array = c[1]
                obj_list.append([name, array])

            else: # Any game object
                pos, key, data = c[1:4]
                pos = tuple(pos)
                key = int(key)
                data = dict(data)
                obj_list.append([name, pos, key, data])

        # Clear level
        if self.current_level != level_name:
            self.engine.clear_cache()
        self.engine.clear_ent()

        # Create level
        for arg in obj_list:
            name = arg[0]

            # TILE LAYER
            if name == 'tile-layer':
                layer_name, array, data = arg[1:4]
                size = vec2d(len(array), len(array[0]))
                self.engine.tile.add_layer(layer_name, size, data, array)

            # STATIC COLLIDER
            elif name == 'static-collider':
                array = arg[1]
                self.size = (vec2d(len(array), len(array[0]))
                             * self.fulltile)
                self.engine.col.st.array.array = array
                self.engine.col.st.size = self.size // self.fulltile

                # Update camera level size to bind camera position
                try:
                    self.engine.cam.level_size
                except AttributeError:
                    msg = 'Camera has no variable: level_size'
                    cprint(msg, 'yellow')
                else:
                    self.engine.cam.level_size = self.size

            # OBJECT
            else:
                pos, key, data = arg[1:4]
                pos = vec2d(*pos)
                args = {
                    'name': name,
                    'pos': pos,
                    'data': data,
                    'key': key
                }
                self.engine.obj.create_object(**args)

        # Render all layers after being built
        for layer in self.engine.tile.layers:
            self.engine.tile.layers[layer].cache()

        # Say level succesful level laod if level is no reloaded
        if self.current_level != level_name:
            cprint('successful level load!', 'green')

        # Update current level
        self.current_level = level_name
        self.engine.obj.post_init()

    def save(self, level_name: Union[str, None] = None):
        """Saves level to level path."""
        # Get level name
        if level_name is None:
            while level_name in ('', None):
                level_name = input('save level name? ')
                if level_name in ('', None):
                    cprint('improper level name.', 'yellow')
                elif level_name == 'exit':
                    return

        # Compile level parts
        obj_list = []

        # Write layers
        for name, layer in self.engine.tile.layers.items():
            if isinstance(layer, TileLayer):
                info = ['tile-layer', name, layer.array._array, layer.data]
                obj_list.append(info)

        # Write stcol
        col = self.engine.col.st
        info = ['static-collider', col.array.array]
        obj_list.append(info)

        # Write each object to file
        for key, obj in self.engine.obj.obj.items():
            info = [obj.name, obj.pos, key, obj.data]
            obj_list.append(info)

        # Create file object and write dumped json to it
        data = json.dumps(obj_list)
        data = data.replace('[["', '[\n\t["')
        data = data.replace('], ["', '], \n\t["')
        data = data.replace('}]]', '}]\n]')
        level = open(path.join(self.paths['levels'], level_name+'.json'), 'w')
        level.write(data)
        level.close()
        cprint('successful level save!', 'green')

    def convert(self, level_name: Union[str, None] = None):
        # Get name
        if level_name is None:
            while level_name in ('', None):
                level_name = input('load level name? ')
                if level_name in ('', None):
                    cprint('improper level name.', 'yellow')
                elif level_name == 'exit':
                    return
                else:
                    level = path.join(self.paths['levels'], level_name+'.lvl')
                    if not path.exists(level):
                        level_name = None
                        cprint('improper level name.', 'yellow')
        else:
            level = path.join(self.paths['levels'], level_name+'.lvl')
            if not path.exists(level):
                code = ['LEVEL ERROR',
                        'path: {}'.format(level),
                        'level name: {}'.format(level_name),
                        'level not found']
                raise FileNotFoundError(colorize('\n'.join(code), 'red'))

        # Load lvl
        if not isinstance(level_name, str):
            return
        level_name = path.join(self.paths['levels'], level_name)
        l = open(level_name+'.lvl', 'r')
        q = l.readlines()
        e = []
        for item in q:
            e.append(literal_eval(item))
        a = open(level_name+'.json', 'w')
        b = json.dumps(e)
        b = b.replace('[["', '[\n\t["')
        b = b.replace('}], ["', '}], \n\t["')
        b = b.replace('}]]', '}]\n]')
        a.write(b)
        a.close()

    def reset(self):
        """Restart current level."""
        self.load(self.current_level)
