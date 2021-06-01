from os import path, getcwd, sep as ossep
import sys

printer = ["### tester.py"]

# Try to get root
root = ""
try:
    import git

    def get_root_git():
        git_repo = git.Repo(getcwd(), search_parent_directories=True)
        git_root = str(git_repo.working_dir)
        return git_root

    try:
        root = get_root_git()
    except git.InvalidGitRepositoryError:
        pass
except ImportError:
    pass


def get_root(dir_name):
    main_path = getcwd()
    part = ""
    while part != dir_name:
        main_path, part = path.split(main_path)
        if main_path == path.abspath(ossep):
            MSG = "Unable to find root in path."
            raise FileNotFoundError(MSG)
    return path.join(main_path, part)


if root == "":
    if getattr(sys, "frozen", False):
        root = path.dirname(sys.executable)
    else:
        # Try finding root by name
        root = get_root("game-x")


# Print out sys.path
printer.append("sys.path: ")
for spath in sys.path:
    printer.append("\t" + spath)

# Add main_path if not in sys.path
if root not in sys.path:
    printer.append(f"adding path: {root}")
    sys.path.insert(0, root)

from main.code.application import Application
from main.code.engine.engine import Engine
from main.code.engine.types import vec2d
from main.code.engine.constants import clear_terminal
from main.code.objects import game_objects, entities, enemies
from main.code.engine.constants import cprint


# Printer
clear_terminal()
for line in printer:
    print(line)

# Object creator
def create_objects(engine: Engine, **kwargs):
    """Takes in a set of keywords and uses them to make an object."""
    # Setup
    name: str = kwargs["name"]
    cname: str = name

    # Classify the name
    parts = cname.split("-")
    cname = "Obj" + "".join(x.title() for x in parts)
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
                msg = f"Unable to find: {cname}"
                cprint(msg, "red")
                return

    # Instantiate the class
    if issubclass(obj_class, entities.Entity):
        key = kwargs["key"]
        data = kwargs["data"]
        key = engine.obj.instantiate_key(key)
        if issubclass(obj_class, game_objects.GameObject):
            pos = kwargs["pos"]
            obj_class(engine, key, name, data, pos)
        else:
            obj_class(engine, key, name, data)


# Classes
class Game(Application):
    def __init__(self):
        super().__init__(32, 16, vec2d(512, 512), create_objects)

    def draw_all(self):
        super().draw_all()
        self.col.st.draw(self.draw)


class TestCol(game_objects.GameObject):
    def __init__(self, engine: Engine, key: int):
        super().__init__(engine, key, "test-col", {}, vec2d(32, 32))

        self.set_frames("player.png")

        self.kkeys = {
            "up": (26, 82),
            "down": (22, 81),
            "left": (4, 80),
            "right": (7, 79),
            "test": (40,),
            "run": (225, 224),
        }

        self.kkey = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "test": False,
            "Hrun": False,
        }

        self.hspd = 0
        self.vspd = 0

    def get_inputs(self):
        for key in self.kkey:
            if key[0] != "H":
                self.kkey[key] = self.engine.inp.kb.get_key_pressed(
                    *self.kkeys[key]
                )
            else:
                self.kkey[key] = self.engine.inp.kb.get_key_held(
                    *self.kkeys[key[1:]]
                )

    def update(self, paused: bool):
        if not paused:
            self.get_inputs()
            self.hspd = self.kkey["right"] - self.kkey["left"]
            self.vspd = self.kkey["down"] - self.kkey["up"]
            if self.kkey["Hrun"]:
                spd = vec2d(self.hspd, self.vspd) * 8
            else:
                spd = vec2d(self.hspd, self.vspd) / 10

            self.pos += spd

            if self.kkey["test"]:
                print(self.pos)

            if self.scollide() and spd != vec2d(0, 0):
                print("SCOL")

            col = self.dcollide()
            if col != [] and spd != vec2d(0, 0):
                print("DCOL")


# Main
def main():
    game = Game()

    game.lvl.load("test-level")

    key = game.obj.instantiate_key()
    TestCol(game, key)

    game.main_loop()


# If ran directly
if __name__ == "__main__":
    main()
