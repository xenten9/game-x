from os import path
from ast import literal_eval

from ..helper_functions.file_system import ObjFile
from ..helper_functions.tuple_functions import f_tupmult

# Handles level loading
class ObjLevel():
    """Object which loads and saves levels."""
    def __init__(self, game):
        self.game = game
        self.level_path = game.PATH['LEVELS']
        self.current_level = ''
        self.level_size = (0, 0)

    def load(self, level_name:str = None):
        """Load level parts such as GameObjects and Tiles."""
        # Get level name
        if level_name is None:
            while level_name in ('', None):
                level_name = input('load level name? ')
                if level_name in ('', None):
                    print('improper level name.')
                elif level_name == 'exit':
                    return
                else:
                    level = path.join(self.level_path, level_name + '.lvl')
                    if not path.exists(level):
                        level_name = None
                        print('improper level name.')
        else:
            level = path.join(self.level_path, level_name + '.lvl')
            if not path.exists(level):
                code = ['LEVEL ERROR',
                        'path: {}'.format(level),
                        'level name: {}'.format(level_name),
                        'level not found']
                raise Exception('\n'.join(code))

        # Load level file
        level = ObjFile(self.level_path, level_name + '.lvl')
        level.read()
        obj_list = level.file.readlines()

        # Convert from str to proper types
        for count in enumerate(obj_list):
            obj_list[count[0]] = (literal_eval(obj_list[count[0]][:-1]))
            if not isinstance(obj_list[count[0]], list):
                obj_list[count[0]] = []

        # Close file
        level.close()

        # Clear level
        if self.current_level != level_name:
            self.game.clear_cache()
        self.game.clear_ent()

        # Create level
        for arg in obj_list:
            name = arg[0]

            # TILE LAYER
            if name == 'tile-layer':
                layer_name, grid, data = arg[1:4]
                size = (len(grid), len(grid[0]))
                self.game.tile.add_layer(layer_name, size, data, grid)

            # STATIC COLLIDER
            elif name == 'static-collider':
                self.game.collider.st.grid = arg[1]
                self.size = f_tupmult(
                    (len(arg[1]), len(arg[1][0])), self.game.FULLTILE)
                # Update camera level size to bind camera position
                try:
                    self.game.cam.set_level_size(self.size)
                except AttributeError:
                    print('camera has no method: set_leveL_size')

            # OBJECT
            else:
                pos, key, data = arg[1:4]
                self.game.obj.create_object(
                    game=self.game, name=name,pos=pos, data=data, key=key)

        # Render all layers after being built
        for layer in self.game.tile.layers:
            self.game.tile.layers[layer].generate()

        # Say level succesful level laod if level is no reloaded
        if self.current_level != level_name:
            print('successful level load!')

        # Update current level
        self.current_level = level_name

    def save(self, level_name:str = None):
        """Saves level to level path."""
        # Get level name
        if level_name is None:
            while level_name in ('', None):
                level_name = input('save level name? ')
                if level_name in ('', None):
                    print('improper level name.')
                elif level_name == 'exit':
                    return

        # Create file object and open it to writing
        level = ObjFile(self.level_path, level_name + '.lvl')
        level.create(1) # Overwrite file if it exists
        level.write()

        # Write layers
        for name, layer in self.game.tile.layers.items():
            info = ['tile-layer', name, layer.grid, layer.data]
            level.file.write(str(info) + '\n')

        # Write stcol
        info = ['static-collider', self.game.collider.st.grid]
        level.file.write(str(info) + '\n')

        # Write each object to file
        for key, obj in self.game.obj.obj.items():
            info = [obj.name, obj.pos, key, obj.data]
            level.file.write(str(info) + '\n')

        # Close file
        level.close()
        print('successful level save!')

    def reset(self):
        """Restart current level."""
        self.load(self.current_level)
