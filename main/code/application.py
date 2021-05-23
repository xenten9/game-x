# Standard library
from time import time
from typing import Callable

# External libraries
from pygame.time import Clock
from pygame import QUIT, KEYDOWN
from pygame.event import get as get_events

# Local imports
from .engine.engine import Engine
from .engine.types.vector import vec2d
from .constants import FPS, PROCESS

class Application(Engine):
    def __init__(self, fulltile: int, fps: int, size: vec2d, object_creator: Callable,
                 debug: bool = False, maindir: str = None):
        # Initialize engine
        super().__init__(fulltile, fps, size, object_creator,
                         debug=debug, maindir=maindir)

        self.clock = Clock()

        if self.debug:
            # Debug timing
            self.debug.time_record = {
                'Update': 0.0,
                'Draw': 0.0,
                'Render': 0.0}

    def main_loop(self):
        """Main loop."""
        # Main loop
        while self.run:
            # Event handler
            self.event_handler()

            # Updating
            self.update()

            # Drawing
            self.draw_all()

            # Rendering
            self.render()

            # Maintain FPS
            self.clock.tick(FPS)
            if self.debug:
                self.debug.tick()

    def event_handler(self):
        """Handle events from pyevent."""
        # Reset pressed inputs
        self.inp.reset()
        events = get_events()
        for event in events:
            if event.type == KEYDOWN:
                # For getting key id's
                #print(event.scancode)
                pass
            self.inp.handle_events(event)
            if event.type == QUIT:
                self.end()
                return

    def draw_all(self):
        # Setup
        t = 0

        if self.debug:
            t = time()

        # Draw all objects
        self.draw.draw()

        if self.debug:
            self.debug.time_record['Draw'] += (time() - t)

    def update(self):
        """Update all objects and debug."""
        # Setup
        t = 0
        debug = self.debug
        obj = self.obj

        if debug:
            t = time()

        # Update objects
        obj.update_early()
        obj.update()
        obj.update_late()

        if debug:
            # Update debug menu
            fps = debug.menu.get('fps')
            fps.text = 'fps: {:.0f}'.format(self.clock.get_fps())

            campos = debug.menu.get('campos')
            campos.text = 'cam pos: {}'.format(self.cam.pos)

            memory = debug.menu.get('memory')
            mem = PROCESS.memory_info().rss
            mb = mem // (10**6)
            kb = (mem - (mb * 10**6)) // 10**3
            memory.text = 'memory: {} MB, {} KB'.format(mb, kb)

            self.debug.time_record['Update'] += (time() - t)

    def render(self):
        """Render all draw calls to screen."""
        # Setup
        t = 0

        if self.debug:
            t = time()

        # Blank
        self.win.blank()
        self.cam.blank()

        # Render
        self.draw.render(self.cam)
        self.win.render(self.cam)

        # Update display
        self.win.update()
        if self.debug:
            self.debug.time_record['Render'] += (time() - t)
