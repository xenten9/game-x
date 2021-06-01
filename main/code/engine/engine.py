"""Game engine."""

from __future__ import annotations

import sys
from os import getcwd, mkdir, path
from typing import Callable

from .components import (
    Mixer,
    Camera,
    Collider,
    Debug,
    Draw,
    Font,
    Input,
    Level,
    ObjectHandler,
    Settings,
    TileMap,
    Window,
)
from .constants import colorize
from .types import vec2d


class Engine:
    """Game engine which all components interact with."""

    def __init__(
        self,
        fulltile: int,
        fps: int,
        size: vec2d,
        object_creator: Callable,
        root: str,
        object_limit: int = None,
        debug: bool = False
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
        self.paths["debug"] = path.join(self.paths["root"], "debug")
        self.paths["assets"] = path.join(self.paths["root"], "assets")
        self.paths["sprites"] = path.join(self.paths["assets"], "sprites")
        self.paths["devsprites"] = path.join(
            self.paths["assets"], "devsprites"
        )
        self.paths["levels"] = path.join(self.paths["assets"], "levels")
        self.paths["tilemaps"] = path.join(self.paths["assets"], "tilemaps")
        self.paths["music"] = path.join(self.paths["assets"], "music")
        self.paths["sfx"] = path.join(self.paths["assets"], "sfx")
        self.paths["settings"] = path.join(self.paths["root"], "settings")
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
        # Output
        self._win = Window(self, size)
        self._cam = Camera(self, size)
        self._draw = Draw(self)
        self._aud = Mixer(self)

        # Input
        self._inp = Input(self)

        # System interaction
        self._font = Font(self)

        # Level interaction
        self._col = Collider(self)
        self._lvl = Level(self)
        self._tile = TileMap(self)
        if object_limit is None:
            self._obj = ObjectHandler(self, object_creator)
        else:
            self._obj = ObjectHandler(self, object_creator, object_limit)

        # Settings
        self._set = Settings(self)

        # Debug
        self._debug = Debug(self, debug)

    # All components
    @property
    def win(self) -> Window:
        return self._win

    @property
    def cam(self) -> Camera:
        return self._cam

    @cam.setter
    def cam(self, cam: Camera):
        if issubclass(type(cam), Camera):
            self._cam = cam

    @property
    def draw(self) -> Draw:
        return self._draw

    @property
    def aud(self) -> Mixer:
        return self._aud

    @property
    def inp(self) -> Input:
        return self._inp

    @property
    def font(self) -> Font:
        return self._font

    @property
    def col(self) -> Collider:
        return self._col

    @property
    def lvl(self) -> Level:
        return self._lvl

    @property
    def tile(self) -> TileMap:
        return self._tile

    @property
    def obj(self) -> ObjectHandler:
        return self._obj

    @property
    def settings(self) -> Settings:
        return self._set

    @property
    def debug(self) -> Debug:
        return self._debug

    def clear_ent(self):
        """Clears out all objects and colliders."""
        self.obj.clear()
        self.col.st.clear()
        self.col.dy.clear()
        self.tile.clear_ent()

    def clear_cache(self):
        """Clears out all objects and colliders."""
        self.aud.sfx.clear()
        self.tile.clear_cache()

    def pause(self):
        self.paused = not self.paused

    def end(self):
        self.run = False
