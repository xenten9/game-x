"""Game-X main application file."""
printer = ["\033[36m# Game-X main_application.py"]


import sys
from os import getcwd, path, sep as ossep

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
from main.code.constants import FPS, FULLTILE, SIZE
from main.code.engine.components.camera import Camera
from main.code.engine.components.maths import f_limit
from main.code.engine.components.menu import MenuText
from main.code.engine.constants import clear_terminal, cprint
from main.code.engine.engine import Engine
from main.code.engine.types import vec2d
from main.code.objects import enemies, entities, game_objects


# Object creation function
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


# Special
class View(Camera):
    """Camera like object which is limited to the inside of the level."""

    def __init__(self, engine: Engine, size: vec2d):
        super().__init__(engine, size)

    @Camera.pos.setter
    def pos(self, pos: vec2d):
        """Position setter."""
        size0 = self.size
        size1 = self.level_size
        x = f_limit(pos.x, 0, size1.x - size0.x)
        y = f_limit(pos.y, 0, size1.y - size0.y)
        self._pos = vec2d(x, y).floor()


class Game(Application):
    """Class in which the game loop runs."""

    def __init__(
        self,
        fulltile: int,
        fps: int,
        size: vec2d,
        debug: bool = False,
        maindir: str = None,
    ):
        # Initialize engine
        super().__init__(
            fulltile, fps, size, create_objects, debug=debug, maindir=maindir
        )

        # Objects
        self.cam = View(self, SIZE)

        # Debug menu expansiosn
        if self.debug:
            volume = MenuText(self, self.debug.menu, "volume")
            volume.pos = vec2d(0, 12 * 3)
            volume.depth = 16
            rect = self.debug.menu.get("rect")
            rect.size = vec2d(190, 52)

        # Load main menu
        self.lvl.load("mainmenu")

    def update(self):
        """Update all objecsts and menu's."""
        super().update()

        # Update debug menu
        debug = self.debug
        if debug:
            volume = debug.menu.get("volume")
            vol = self.aud.volume
            mvol = self.aud.music.volume
            volume.text = f"volume: {vol}; music_volume: {mvol}"


# Main application functions
def main(debug: bool = False):
    """Create a Game object and run it's main_loop."""
    # Print out printer lines
    clear_terminal()
    for line in printer:
        print(line)
    cprint("All imports finished.", "green")

    # Create engine object
    game = Game(FULLTILE, FPS, SIZE, debug, maindir=root)

    # Run main game loop
    game.main_loop()


# Parse arguments given to script
def parse_args(args: list[str]) -> dict:
    """Returns a formated dictionary of arguments for main."""
    # Setup
    script_name: str = args.pop(0)
    out_args: dict = {}

    # Default
    out_args.setdefault("debug", True)

    # Group args into declerator and value
    new_args: list[tuple[str, str]] = []
    for i in range(len(args) // 2):
        new_args.append((args[2 * i], args[2 * i + 1]))

    # Parse args
    for arg in new_args:
        declerator, value = arg

        # Debug
        if declerator == "-d":
            if value in ("False", "false", "0"):
                out_args["debug"] = False
            else:
                out_args["debug"] = True

    # Return parsed args
    return out_args


if __name__ == "__main__":
    # Parse arguments
    args = parse_args(sys.argv)
    main(**args)
