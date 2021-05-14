"""Level editing tool for Game-X."""
# Standard Library
from os import path, system, name as osname, sys, getcwd
from time import time

# External Libraries
from pygame.constants import KEYDOWN, QUIT
from pygame.time import Clock
from pygame.event import get as get_events

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



# Main application functions
def main(debug: bool = False):
    engine = Engine(FULLTILE, FPS, SIZE, debug, maindir=main_path)

    engine.debug.menu.remove('rect')
    ele = MenuText(engine, engine.debug.menu, 'curpos')
    ele.pos = vec2d(0, 12*3)
    ele = MenuText(engine, engine.debug.menu, 'mode')
    ele.pos = vec2d(0, 12*4)

    engine.init_obj(create_objects)
    cam = View(engine, SIZE)
    engine.cam = cam

    engine.lvl.load('default')
    engine.tile.add_all()

    editor(engine)

def editor(engine: Engine):
    cursor = ObjCursor(engine, vec2d(0, 0))
    clock = Clock()
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
        # Update debug menu
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



# Run main
if __name__ == '__main__':
    main(True)
