# Standard library
from os import system, name as osname
from time import time

# External libraries
from pygame.constants import KEYDOWN, QUIT
from pygame.time import Clock
from pygame.event import get as get_events

# Package imports
if __name__ == '__main__':
    # If ran directly
    from code.engine.types.vector import vec2d
    from code.engine.engine import Engine
    from code.engine.components.maths import f_limit
    from code.engine.components.camera import Camera
    from code.classes.entities import *
    from code.classes.objects import *
else:
    # If imported as module
    from .code.engine.types.vector import vec2d
    from .code.engine.engine import Engine
    from .code.engine.components.maths import f_limit
    from .code.engine.components.camera import Camera
    from .code.classes.entities import *
    from .code.classes.objects import *



# Clear the terminal
def clear_terminal():
    if osname == 'nt':
        system('cls')
    else:
        system('clear')

clear_terminal()
print('All imports finished.')

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
    name = kwargs['name']
    if name == 'player':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE)
        ObjPlayer(engine, key, pos, size, name, data)

    elif name == 'grav-orb':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE)
        ObjGravOrb(engine, key, pos, size, name, data)

    elif name == 'door':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE)
        ObjDoor(engine, key, pos, size, name, data)

    elif name == 'button':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE//8)
        ObjButton(engine, key, pos, size, name, data)

    elif name == 'spike':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE//4)
        ObjSpike(engine, key, pos, size, name, data)

    elif name == 'spike-inv':
        key = kwargs['key']
        pos = kwargs['pos']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        size = vec2d(FULLTILE, FULLTILE//4)
        ObjSpikeInv(engine, key, pos, size, name, data)

    elif name == 'juke-box':
        key = kwargs['key']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        ObjJukeBox(engine, key, name, data)

    elif name == 'main-menu':
        key = kwargs['key']
        data = kwargs['data']
        key = engine.obj.instantiate_key(key)
        ObjMainMenu(engine, key, name, data)



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



# Main application functions
def main(debug: bool = False):
    # Create engine object
    engine = Engine(FULLTILE, FPS, SIZE, debug)
    engine.init_obj(create_objects)
    cam = View(SIZE)
    engine.set_cam(cam)

    # Load main menu
    engine.lvl.load('mainmenu')
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
