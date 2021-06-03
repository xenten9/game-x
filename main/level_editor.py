"""Game-X Level editing tool."""
printer = ["\033[36m# Game-X level_editor.py"]

import sys
from os import getcwd, path

# Add root of executable
if getattr(sys, "frozen", False):
    root = path.dirname(sys.executable)
    if root not in sys.path:
        printer.append(f"adding path: {root}")
        sys.path.insert(0, root)
else:
    root = getcwd()

# Print out sys.path
printer.append("sys.path: ")
for spath in sys.path:
    printer.append("\t" + spath)

# Add main_path if not in sys.path
if root not in sys.path:
    printer.append(f"adding path: {root}")
    sys.path.insert(0, root)


from main.code.application import Application
from main.code.constants import FPS, FULLTILE, SIZE
from main.code.engine.components.camera import Camera
from main.code.engine.components.menu import MenuText
from main.code.engine.constants import clear_terminal, cprint
from main.code.engine.engine import Engine
from main.code.engine.types import vec2d
from main.code.objects.editor import ObjCursor, Object


# Object creation function
def create_objects(engine: Engine, **kwargs):
    """Takes in a set of keywords and uses them to make an object.
    engine: engine which contains game components.

    name: name of the object being created.
    key: id of the key when created
    pos: position of the created object.
    data: dictionary containing kwargs for __init__."""
    name = kwargs["name"]
    key = kwargs["key"]
    key = engine.obj.instantiate_key(key)
    pos = kwargs["pos"]
    data = kwargs["data"]
    Object(engine, name, key, pos, data)


# Special
class View(Camera):
    """Camera like object which is limited to the inside of the level."""

    def __init__(self, engine: Engine, size: vec2d):
        super().__init__(engine, size)

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
    def __init__(
        self,
        fulltile: int,
        fps: int,
        size: vec2d,
        root: str,
        debug: bool = False,
    ):
        # Initialize engine
        super().__init__(
            fulltile, fps, size, create_objects, debug=debug, root=root
        )

        if self.debug:
            self.debug.menu.remove("rect")
            ele = MenuText(self, self.debug.menu, "curpos")
            ele.pos = vec2d(0, 12 * 3)
            ele = MenuText(self, self.debug.menu, "mode")
            ele.pos = vec2d(0, 12 * 4)

        # Create cursor and camera
        ObjCursor(self, vec2d(0, 0))
        self.cam = View(self, SIZE)

        # Add stcol to sobj
        self.obj.sobj["stcol"] = self.col.st

        # Load empty level
        self.lvl.load("default")
        self.tile.add_all()

    def event_handler(self):
        super().event_handler()

        if self.inp.kb.get_key_pressed(41):
            self.end()
            return


# Main application functions
def main(debug: bool = False):
    # Print out printer lines
    clear_terminal()
    for line in printer:
        print(line)
    cprint("All imports finished.", "green")

    # Create engine object
    game = Game(FULLTILE, FPS, SIZE, root, debug=debug)

    # Run main game loop
    game.main_loop()


# Run main
if __name__ == "__main__":
    main(True)
