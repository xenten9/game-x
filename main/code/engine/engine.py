"""Game engine."""

from __future__ import annotations
from main.code.engine.components.output_handler import OutputHandler

from os import mkdir, path
from typing import Callable

from main.code.engine.components import (
    AssetHandler,
    InputHandler,
    ObjectHandler,
    Debug,
    Settings,
)
from main.code.engine.constants import colorize
from main.code.engine.types import vec2d


class Engine:
    """Game engine which all components interact with."""

    def __init__(
        self,
        fulltile: int,
        fps: int,
        size: vec2d,
        create_object: Callable,
        root: str,
        debug: bool = False,
    ):
        # Define constants
        self.FULLTILE = fulltile
        self.FPS = fps

        # File paths
        self.paths: dict[str, str] = {}
        self.paths["root"] = root
        if not path.exists(self.paths["root"]):
            msg = f"ROOT: {root} DOES NOT EXIST"
            raise FileNotFoundError(colorize(msg, "red"))

        # Non-Required
        self.paths["settings"] = path.join(self.paths["root"], "settings")
        self.paths["debug"] = path.join(self.paths["root"], "debug")

        # Assets
        self.paths["assets"] = path.join(self.paths["root"], "assets")
        self.paths["sprites"] = path.join(self.paths["assets"], "sprites")
        self.paths["devsprites"] = path.join(self.paths["sprites"], "dev")
        self.paths["levels"] = path.join(self.paths["assets"], "levels")
        self.paths["tilemaps"] = path.join(self.paths["assets"], "tilemaps")
        self.paths["music"] = path.join(self.paths["assets"], "music")
        self.paths["sfx"] = path.join(self.paths["assets"], "sfx")

        for dirpath in self.paths:
            if dirpath not in ("root", "debug"):
                if not path.exists(self.paths[dirpath]):
                    if dirpath == "settings":
                        mkdir(self.paths[dirpath])
                    elif dirpath == "debug":
                        mkdir(self.paths[dirpath])
                    else:
                        msg = (
                            f"unable to locate {dirpath} directory\n"
                            f"attempted path: {self.paths[dirpath]}\n"
                        )
                        raise FileNotFoundError(colorize(msg, "red"))

        # Parameters
        self.run = True
        self.paused = False
        self.parallax = False

        # Components
        self.input = InputHandler(self)
        self.output = OutputHandler(self, size)
        self.assets = AssetHandler(self)
        self.objects = ObjectHandler(self, create_object)
        self.debug = Debug(self, debug)
        self.settings = Settings(self)
        self.cam = self.output.cam

    def pause(self):
        self.paused = not self.paused

    def end(self):
        self.run = False
