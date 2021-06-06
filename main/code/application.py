from time import time
from typing import Callable

from pygame import KEYDOWN, QUIT
from pygame.event import Event
from pygame.event import get as get_events
from pygame.time import Clock

from main.code.constants import FPS, PROCESS
from main.code.engine.engine import Engine
from main.code.engine.types import vec2d


class Application(Engine):
    def __init__(
        self,
        fulltile: int,
        fps: int,
        size: vec2d,
        object_creator: Callable,
        root: str,
        debug: bool = False,
    ):
        # Initialize engine
        super().__init__(
            fulltile, fps, size, object_creator, root, debug=debug
        )

        self.clock = Clock()

        if self.debug:
            # Debug timing
            self.debug.time_record = {
                "Update": 0.0,
                "Draw": 0.0,
                "Render": 0.0,
            }

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

    def event_handler(self, events: list[Event] = None):
        """Handle events from pyevent."""
        # Reset pressed inputs
        self.input.reset()
        if events is None:
            events = get_events()
        for event in events:
            if event.type == KEYDOWN:
                # For getting key id's
                # print(event.scancode)
                pass
            self.input.handle_events(event)
            if event.type == QUIT:
                self.end()
                return

    def draw_all(self):
        # Setup
        t = 0

        if self.debug:
            t = time()

        # Draw all objects
        self.objects.draw(self.output.draw)

        if self.debug:
            self.debug.time_record["Draw"] += time() - t

    def update(self):
        """Update all objects and debug."""
        # Setup
        t = 0
        debug = self.debug
        obj = self.objects.ent

        if debug:
            t = time()

        obj.update()

        if debug:
            # Update debug menu
            fps = debug.menu.get("fps")
            fps.text = f"fps: {self.clock.get_fps():.0f}"

            campos = debug.menu.get("campos")
            campos.text = f"cam pos: {self.cam.pos}"

            memory = debug.menu.get("memory")
            mem = PROCESS.memory_info().rss
            mb = mem // (10 ** 6)
            kb = (mem - (mb * 10 ** 6)) // 10 ** 3
            memory.text = f"memory: {mb} MB, {kb} KB"

            self.debug.time_record["Update"] += time() - t

    def render(self):
        """Render all draw calls to screen."""
        # Setup
        t = 0

        if self.debug:
            t = time()

        # Blank
        self.output.window.blank()
        self.cam.blank()

        # Render
        self.output.draw.render(self.cam)
        self.output.window.render(self.cam)

        # Update display
        self.output.window.update()

        if self.debug:
            self.debug.time_record["Render"] += time() - t
