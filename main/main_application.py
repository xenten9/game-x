"""Game-X main application file[supports running directly and from root]."""
printer = ['\033[36m# Game-X main_application.py'] # For printing after terminal clear

# Standard library
from os import path, getcwd, sys
import sys
from typing import List, Tuple

# Check if ran from an executable
if getattr(sys, 'frozen', False):
    main_path: str = path.dirname(sys.executable)
else:
    def splitall(filepath: str) -> List[str]:
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
    main_path: str = getcwd()
    path_parts = splitall(main_path)
    root = path_parts[0]
    main_path = root
    for part in path_parts[1:]:
        main_path = path.join(main_path, part)
        if part == 'game-x':
            break

# Add current directory to sys.path
if main_path not in sys.path:
    printer.append('main path: {}'.format(main_path))
    printer.append('sys.path: ')
    for spath in sys.path:
        printer.append('\t' + spath)
    printer.append('adding path: {}'.format(main_path))
    sys.path.insert(0, main_path)

# Local imports
if __name__ == '__main__':
    try:
        from main.code.engine.types.vector import vec2d
        from main.code.engine.engine import Engine
        from main.code.application import Application
        from main.code.engine.components.maths import f_limit
        from main.code.engine.components.camera import Camera
        from main.code.engine.components.menu import MenuText
        from main.code.constants import FULLTILE, FPS, SIZE, PROCESS
        from main.code.constants import cprint, clear_terminal
        from main.code.objects import game_objects
        from main.code.objects import enemies
        from main.code.objects import entities

    except ModuleNotFoundError:
        print('Unable to find all modules.')
        print('sys.path:')
        paths = sys.path
        for spath in paths:
            print('\t' + spath)
        exit()

else:
    try:
        # If imported as module
        from .code.engine.types.vector import vec2d
        from .code.engine.engine import Engine
        from .code.application import Application
        from .code.engine.components.maths import f_limit
        from .code.engine.components.camera import Camera
        from .code.engine.components.menu import MenuText
        from .code.constants import FULLTILE, FPS, SIZE, PROCESS
        from .code.constants import cprint, clear_terminal
        from .code.objects import game_objects
        from .code.objects import enemies
        from .code.objects import entities

    except ModuleNotFoundError:
        printer.append('unable to import modules relatively.')
        exit()



# print succesful importing
clear_terminal()
for line in printer:
    print(line)
cprint('All imports finished.', 'green')

# Object creation function
def create_objects(engine: Engine, **kwargs):
    """Takes in a set of keywords and uses them to make an object."""
    # Setup
    name: str = kwargs['name']
    cname: str = name

    # Classify the name
    parts = cname.split('-')
    cname = 'Obj' + ''.join(x.title() for x in parts)
    try:
        obj_class = getattr(game_objects, cname)
    except AttributeError:
        try:
            obj_class = getattr(entities, cname)
        except AttributeError:
            try:
                obj_class = getattr(enemies, cname)
            except AttributeError:
                # NOTE here is where mods would be implemented.
                # SEE ~/game-x/ideas.txt
                msg = 'Unable to find: {}'.format(cname)
                cprint(msg, 'red')
                return

    # Instantiate the class
    if issubclass(obj_class, entities.Entity):
        key = kwargs['key']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        if issubclass(obj_class, game_objects.GameObject) or issubclass(obj_class, enemies.Enemy):
            pos = kwargs['pos']
            obj_class(engine, key, name, data, pos)
        else:
            obj_class(engine, key, name, data)



# Special
class View(Camera):
    """Camera like object which is limited to the inside of the level."""
    def __init__(self, engine: Engine, size: vec2d):
        super().__init__(engine, size)
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

class Game(Application):
    def __init__(self, fulltile: int, fps: int, size: vec2d,
                 debug: bool = False, maindir: str = None):
        # Initialize engine
        super().__init__(fulltile, fps, size, create_objects,
                         debug=debug, maindir=maindir)

        # Objects
        self.cam = View(self, SIZE)

        # Debug menu expansiosn
        if self.debug:
            volume = MenuText(self, self.debug.menu, 'volume')
            volume.pos = vec2d(0, 12*3)
            rect = self.debug.menu.get('rect')
            rect.size = vec2d(190, 12*4)

        # Load main menu
        self.lvl.load('mainmenu')

    def update(self):
        super().update()

        # Update debug menu
        debug = self.debug
        if debug:
            volume = debug.menu.get('volume')
            vol = self.aud.volume
            mvol = self.aud.music.volume
            volume.text = 'volume: {}; music_volume: {}'.format(vol, mvol)



# Main application functions
def main(debug: bool = False):
    # Create engine object
    game = Game(FULLTILE, FPS, SIZE, debug, maindir=main_path)

    # Run main game loop
    game.main_loop()

# Parse arguments given to script
def parse_args(args: List[str]) -> dict:
    # Setup
    script_name: str = args.pop(0)
    out_args: dict = {}

    # Default
    out_args.setdefault('debug', True)

    # Group args into declerator and value
    new_args: List[Tuple[str, str]] = []
    for i in range(len(args)//2):
        new_args.append((args[2*i], args[2*i+1]))

    # Parse args
    for arg in new_args:
        declerator, value = arg

        # Debug
        if declerator == '-d':
            if value in ('False', 'false', '0'):
                out_args['debug'] = False
            else:
                out_args['debug'] = True

    # Return parsed args
    return out_args



# Run main
if __name__ == '__main__':
    # Setup
    debug = True

    # Parse arguments
    args = parse_args(sys.argv)

    # Run main
    main(**args)
