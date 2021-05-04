# Imports
from os import path, getcwd
import sys
from typing import Callable

from .types.vector import vec2d
from .components.window import Window
from .components.input import Input
from .components.audio import Mixer
from .components.font import Font
from .components.object import ObjectHandler
from .components.collision import Collider
from .components.draw import Draw
from .components.level import Level
from .components.camera import Camera
from .components.tile import TileMap
from .components.debug import Debug


class Engine():
    def __init__(self, fulltile: int, fps: int, size: vec2d, debug: bool = False, maindir: str = None):
        # Define constants
        self.FULLTILE = fulltile
        self.FPS = fps

        # File paths
        self.paths = {}
        if maindir is None:
            if getattr(sys, 'frozen', False):
                self.paths['main'] = path.dirname(sys.executable)
            else:
                self.paths['main'] = getcwd()
        else:
            self.paths['main'] = maindir
        self.paths['debug'] = path.join(self.paths['main'], 'debug')
        self.paths['assets'] = path.join(self.paths['main'], 'assets')
        self.paths['sprites'] = path.join(self.paths['assets'], 'sprites')
        self.paths['devsprites'] = path.join(self.paths['assets'], 'devsprites')
        self.paths['levels'] = path.join(self.paths['assets'], 'levels')
        self.paths['tilemaps'] = path.join(self.paths['assets'], 'tilemaps')
        self.paths['music'] = path.join(self.paths['assets'], 'music')
        self.paths['sfx'] = path.join(self.paths['assets'], 'sfx')

        # Parameters
        self.run = True
        self.parallax = False

        # Define components
        self.win = Window(self, size)
        self.aud = Mixer(self)
        self.inp = Input(self)
        self.fnt = Font(self)
        self.col = Collider(self)
        self.draw = Draw(self)
        self.lvl = Level(self)
        self.til = TileMap(self)
        self.cam = Camera(size)
        self.debug = Debug(self, debug)
        self.obj = None


    def init_obj(self, object_creator: Callable, max_object: int = None):
        if max_object is None:
            self.obj = ObjectHandler(self, object_creator)
        else:
            self.obj = ObjectHandler(self, object_creator, max_object)

    def init_cam(self, size: vec2d):
        self.cam = Camera(size)

    def set_cam(self, cam):
        if issubclass(type(cam), Camera):
            self.cam = cam

    def clear_ent(self):
        """Clears out all objects and colliders."""
        self.obj.clear()
        self.col.st.clear()
        self.col.dy.clear()
        self.til.clear_ent()

    def clear_cache(self):
        """Clears out all objects and colliders."""
        self.aud.sfx.clear()
        self.til.clear_cache()

    def end(self):
        self.run = False
