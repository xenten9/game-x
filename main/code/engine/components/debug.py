"""Debug object for containing and displaying debug info."""

from os import path, mkdir
from datetime import datetime

from main.code.engine.components.menu import Menu, MenuRect, MenuText
from main.code.engine.components.output_handler import Draw
from main.code.engine.types import Component, vec2d
from main.code.engine.types.entity import Entity


class Debug(Component, Entity):
    def __init__(self, engine, debug):
        super().__init__(engine)
        self.debug = debug

        if self.debug:
            self.engine.objects.ent.sobj["debug"] = self

            # Menu vars
            self.menu = Menu(engine)

            fps = MenuText(engine, self.menu, "fps")
            fps.size = 12
            fps.font = "consolas"
            fps.depth = 16

            campos = MenuText(engine, self.menu, "campos")
            campos.size = 12
            campos.pos = vec2d(0, 12)
            campos.font = "consolas"
            campos.depth = 16

            memory = MenuText(engine, self.menu, "memory")
            memory.size = 12
            memory.pos = vec2d(0, 24)
            memory.font = "consolas"
            memory.depth = 16

            rect = MenuRect(engine, self.menu, "rect")
            rect.size = vec2d(160, 36)
            rect.color = (0, 0, 0)

            # Create debug directory
            if not path.exists(self.paths["debug"]):
                mkdir(self.paths["debug"])
                print("debug directory created!")

            # Debug file vars
            self.date_time = datetime.now()
            self.date_time = self.date_time.strftime("%Y-%m-%d_%Hh%M_%S")
            self.file = path.join(self.paths["debug"], f"{self.date_time}.txt")
            file = open(self.file, "a")
            file.write(self.date_time + "\n")
            file.close()

            # Timing vars
            self.time_record = {}
            self.clock = 0

    def __bool__(self):
        return self.debug

    def draw(self, draw: Draw):
        self.menu.draw(draw)

    def tick(self):
        """Called once every frame."""
        self.clock += 1
        if self.clock == self.engine.FPS * 10:
            self.clock = 0
            self.record(10)

    def record(self, time: float):
        """Record time data to file."""
        size = 0
        total = 0
        for item in self.time_record:
            total += self.time_record[item]
            size = max(size, len(item))

        write = ""
        write += "###\n"
        write += f"Total: {total * (100 / time):.1f}%\n"

        for item in self.time_record:
            text = item
            while len(text) < size:
                text += " "
            text = f"{text}: {100 * (self.time_record[item] / time):.1f}%\n"
            write += text
            self.time_record[item] = 0
        file = open(self.file, "a")
        file.write(write + "\n")
        file.close()
