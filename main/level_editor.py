"""Level editing tool for Game-X."""
# Standard Library
from os import path, system, name as osname, sys, getcwd

# Check if ran from an executable
if getattr(sys, 'frozen', False):
    main_path = path.dirname(sys.executable)
else:
    def splitall(filepath: str) -> list:
        allparts = []
        while True:
            parts = path.split(filepath)
            if parts[0] == filepath:
                allparts.insert(0, parts[0])
                break
            elif parts[1] == filepath:
                allparts.insert(0, parts[1])
                break
            else:
                filepath = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    main_path = getcwd()
    path_parts = splitall(main_path)
    root = path_parts[0]
    main_path = root
    for part in path_parts[1:]:
        main_path = path.join(main_path, part)
        if part == 'game-x':
            break

# Add current directory to sys.path
if main_path not in sys.path:
    print('adding path: {}'.format(main_path))
    sys.path.insert(0, main_path)

# Local Imports
if __name__ == '__main__':
    try:
        # If ran directly
        from main.code.engine.types.vector import vec2d
        from main.code.engine.engine import Engine
        from main.code.application import Application
        from main.code.engine.components.camera import Camera
        from main.code.engine.components.menu import MenuText
        from main.code.constants import FULLTILE, FPS, SIZE, PROCESS
        from main.code.constants import cprint, clear_terminal
        from main.code.objects.editor import ObjCursor, Object

    except ModuleNotFoundError:
        print('Unable to find all modules.')
        print('sys path is: ')
        paths = sys.path
        for path in paths:
            print(path)
        exit()
else:
    try:
        # If imported as module
        from .code.engine.types.vector import vec2d
        from .code.engine.engine import Engine
        from main.code.application import Application
        from .code.engine.components.camera import Camera
        from .code.engine.components.menu import MenuText
        from .code.constants import FULLTILE, FPS, SIZE, PROCESS
        from .code.constants import cprint
        from .code.objects.editor import ObjCursor, Object

    except ModuleNotFoundError:
        print('unable to import modules relatively.')
        exit()



# Clear the terminal
def clear_terminal():
    if osname == 'nt':
        system('cls')
    else:
        system('clear')

clear_terminal()
cprint('All imports finished.', 'green')

# Object creation function
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



# Special
class View(Camera):
    """Camera like object which is limited to the inside of the level."""
    def __init__(self, engine: Engine, size: vec2d):
        super().__init__(engine, size)
        self.keys = {
            }
        self.key = {
            }

    def _pos_get(self) -> vec2d:
        return self._pos

    def _pos_set(self, pos: vec2d):
        """Position setter."""
        if pos.x < 0:
            pos = vec2d(0, pos.y)
        if pos.y < 0:
            pos = vec2d(pos.x, 0)
        self._pos = pos.floor()

    pos = property(_pos_get, _pos_set)

class Game(Application):
    def __init__(self, fulltile: int, fps: int, size: vec2d,
                 debug: bool = False, maindir: str = None):
        # Initialize engine
        super().__init__(fulltile, fps, size, create_objects,
                         debug=debug, maindir=maindir)

        if self.debug:
            self.debug.menu.remove('rect')
            ele = MenuText(self, self.debug.menu, 'curpos')
            ele.pos = vec2d(0, 12*3)
            ele = MenuText(self, self.debug.menu, 'mode')
            ele.pos = vec2d(0, 12*4)

        # Create cursor and camera
        ObjCursor(self, vec2d(0, 0))
        self.cam = View(self, SIZE)

        # Add stcol to sobj
        self.obj.sobj['stcol'] = self.col.st

        # Load empty level
        self.lvl.load('default')
        self.tile.add_all()



# Main application functions
def main(debug: bool = False):
    game = Game(FULLTILE, FPS, SIZE, debug, maindir=main_path)

    game.main_loop()



# Run main
if __name__ == '__main__':
    main(True)
