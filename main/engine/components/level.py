from os import path
from ast import literal_eval

from ..helper_functions.file_system import ObjFile
from ..helper_functions.tuple_functions import f_tupmult

# Handles level loading
class ObjLevel():
    """Object which contains all levels in the game."""
    def __init__(self, game, level_path):
        self.game = game
        self.level_path = level_path
        self.current_level = ''
        self.level_size = (0, 0)

    def load(self, level_name=None):
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
        self.current_level = level_name
        obj_list = level.file.readlines()

        # Convert types
        for count in enumerate(obj_list):
            obj_list[count[0]] = (literal_eval(obj_list[count[0]][:-1]))
            if not isinstance(obj_list[count[0]], list):
                obj_list[count[0]] = []

        # Close file
        level.close()

        # Clear entities
        self.game.clear()

        # Create objects
        for arg in obj_list:
            # Interpret object info
            name = arg[0]
            if name == 'tile-layer':
                # Interpret layer info
                layer_name, grid = arg[1:3]
                size = (len(grid), len(grid[0]))
                self.game.tile.add_layer(layer_name, size, grid)
            elif name == 'static-collider':
                self.game.collider.st.grid = arg[1]
                self.size = f_tupmult((len(arg[1]), len(arg[1][0])), self.game.FULLTILE)
                self.game.cam.set_level_size(self.size)
            else:
                pos, key, data = arg[1:4]
                self.game.obj.create_object(game=self.game, name=name, pos=pos, data=data, key=key)

        for layer in self.game.tile.layers:
            self.game.tile.layers[layer].generate()

        print('successful level load!')

    def save(self, level_name=None):
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
            info = ['tile-layer', name, layer.grid]
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
