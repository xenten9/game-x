"""Game-X main application file[supports running directly and from root]."""
printer = ['# Game-X main_application.py'] # For printing after terminal clear

# Standard library
from os import path, getcwd
from time import sleep, time
import sys
from typing import List

# External libraries
from pygame.constants import KEYDOWN, QUIT
from pygame.time import Clock
from pygame.event import get as get_events

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
        from main.code.engine.components.maths import f_limit
        from main.code.engine.components.camera import Camera
        from main.code.engine.components.menu import MenuText
        from main.code.constants import FULLTILE, FPS, SIZE, PROCESS
        from main.code.constants import cprint, clear_terminal
        from main.code.objects import game_objects
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
        from .code.engine.components.maths import f_limit
        from .code.engine.components.camera import Camera
        from .code.engine.components.menu import MenuText
        from .code.constants import FULLTILE, FPS, SIZE, PROCESS
        from .code.constants import cprint, clear_terminal
        from .code.objects import game_objects
        from .code.objects import entities

    except ModuleNotFoundError:
        printer.append('unable to import modules relatively.')
        exit()



# print succesful importing
clear_terminal()
for line in printer:
    print(line)
    sleep(0.1)
cprint('All imports finished.', 'green')

# Object creation function
def create_objects(engine: Engine, **kwargs):
    """Takes in a set of keywords and uses them to make an object.
        Required kwargs:
        name: name of the object being created.
        engine: engine which contains game components.

        Dependent kwargs:
        key: id of the key when created
        pos: position of the created object.
        data: dictionary containing kwargs for __init__."""
    name: str = kwargs['name']
    cname: str = name
    if True:
        # Classify the name
        parts = cname.split('-')
        cname = 'Obj'
        for part in parts:
            cname += part[0].upper() + part[1:]
        try:
            obj_class = getattr(game_objects, cname)
        except AttributeError:
            try:
                obj_class = getattr(entities, cname)
            except AttributeError:
                msg = 'Unable to find: {}'.format(cname)
                cprint(msg, 'red')
                return
    if issubclass(obj_class, entities.Entity):
        key = kwargs['key']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        if issubclass(obj_class, game_objects.GameObject):
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



# Main application functions
def main(debug: bool = False):
    # Create engine object
    engine = Engine(FULLTILE, FPS, SIZE, debug, maindir=main_path)
    engine.init_obj(create_objects)
    cam = View(engine, SIZE)
    engine.cam = cam

    # Load main menu
    engine.lvl.load('mainmenu')

    # Add debug elements
    if engine.debug:
        volume = MenuText(engine, engine.debug.menu, 'volume')
        volume.pos = vec2d(0, 12*3)
        rect = engine.debug.menu.get('rect')
        rect.size = vec2d(190, 12*4)

    gameplay_mode(engine)

def gameplay_mode(engine: Engine):
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
        update_debug(engine, clock)

        # Drawing
        draw(engine)

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

        volume = debug.menu.get('volume')
        vol = engine.aud.volume
        mvol = engine.aud.music.volume
        volume.text = 'volume: {}; music_volume: {}'.format(vol, mvol)

def draw(engine: Engine):
    t = 0
    if engine.debug:
        t = time()
    engine.draw.draw()
    if engine.debug:
        engine.debug.menu.draw(engine.draw)
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
    main(debug=True)
