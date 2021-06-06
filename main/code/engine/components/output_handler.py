from os import path
from typing import Union

from main.code.engine.constants import colorize, cprint
from main.code.engine.types import Component, vec2d
from pygame import DOUBLEBUF, HWSURFACE, display, mixer
from pygame.surface import Surface

DRAW = tuple[Surface, vec2d, bool, int]


class OutputHandler(Component):
    def __init__(self, engine, window_size: vec2d):
        super().__init__(engine)
        self.audio = Audio(engine)
        self.draw = Draw(engine)
        self.window = Window(engine, window_size)
        self.cam = Camera(engine, window_size)


class Audio(Component):
    """Handles all audio."""

    def __init__(self, engine):
        super().__init__(engine)
        mixer.init(size=-16)
        self._volume = 1.0
        self.sfx = SFX(engine, self)
        self.music = Music(engine, self)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume: float):
        if 0 <= volume <= 1:
            self._volume = volume
            self.music.update_volume()
            self.sfx.update_volume()


class Music(Component):
    """Play's music in game.
    Can only play one song at a time."""

    def __init__(self, engine, audio: Audio):
        super().__init__(engine)
        self.audio = audio
        self.music = None
        self.music_queue = None
        self.fading = False
        self.paused = False
        self._volume = 1.0
        mixer.music.set_volume(self.volume * self.main_volume)
        mixer.music.set_endevent(56709)

    @property
    def main_volume(self):
        return self.audio.volume

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume: float):
        if 0.0 <= volume <= 1.0:
            if volume != self.volume:
                self._volume = volume
                mixer.music.set_volume(self.volume * self.main_volume)

    def update_volume(self):
        mixer.music.set_volume(self.volume * self.main_volume)

    def load(self, file: str):
        """Load music."""
        music = path.join(self.paths["music"], file)
        mixer.music.load(music)
        self.music = file

    def play(self, loops: int = 0):
        """Load music."""
        mixer.music.play(loops)

    def stop(self, fade: int = 0):
        """Load music."""
        if fade == 0 and not self.fading:
            mixer.music.stop()
        else:
            mixer.music.fadeout(fade)
            self.fading = True

    def pause(self):
        """Load music."""
        mixer.music.pause()
        self.paused = True

    def resume(self):
        """Load music."""
        mixer.music.unpause()
        self.paused = False

    def queue(self, file: str, loops: int, volume: float):
        """Queue up a song."""
        self.music_queue = (file, loops, volume)

    def get_current(self) -> Union[str, None]:
        """Unload music."""
        if mixer.music.get_busy():
            return self.music
        return None

    def end(self):
        """Called when music ends."""
        self.music = None
        self.fading = False
        if self.music_queue is not None:
            music = self.music_queue
            self.music_queue = None
            file = music[0]
            loops = music[1]
            volume = music[2]
            self.load(file)
            self.volume = volume
            self.play(loops)


class SFX(Component):
    """Play's sound effects.
    Can play multiple sounds at a time."""

    def __init__(self, engine, audio: Audio):
        super().__init__(engine)
        self.audio = audio
        self.tracks: dict[str, mixer.Sound] = {}
        self.tvolume: dict[str, float] = {}

    @property
    def main_volume(self) -> float:
        return self.audio.volume

    def update_volume(self):
        for key in self.tracks:
            self.tracks[key].set_volume(self.tvolume[key] * self.main_volume)

    def add(self, file: str, volume: float = 1.0):
        """add file to tracks."""
        try:
            self.tracks[file]
        except KeyError:
            sound = path.join(self.paths["sfx"], file)
            self.tracks[file] = mixer.Sound(sound)
            self.tvolume[file] = volume
            vol = self.tvolume[file] * self.main_volume
            self.tracks[file].set_volume(vol)

    def remove(self, file: str):
        """remove file from tracks."""
        try:
            del self.tracks[file]
        except KeyError:
            msg = f"file {file} does not exist"
            cprint(msg, "red")

    def play(self, file: str, loops: int = 0):
        """Play sfx."""
        self.tracks[file].play(loops=loops)

    def stop(self, file: str, fade: int):
        """fade is number of milliseconds of fade out."""
        if fade == 0:
            self.tracks[file].stop()
        elif fade > 0:
            self.tracks[file].fadeout(fade)

    def clear(self):
        self.tracks = {}


class Camera(Component):
    """Camera object for defining viewframe."""

    def __init__(self, engine, size: vec2d):
        super().__init__(engine)
        self.size = size
        self.level_size = size
        self._pos = vec2d(0, 0)
        self._surface = Surface(size.ftup())

    @property
    def pos(self) -> vec2d:
        return self._pos

    @pos.setter
    def pos(self, pos: vec2d):
        self._pos = pos

    @property
    def surface(self):
        return self._surface

    def draw_surface(
        self,
        surface: Surface,
        pos: vec2d,
        gui: bool = False,
        special_flags: int = 0,
    ):
        """Draws a surface at a position."""
        if gui:
            self._surface.blit(
                surface, pos.ftup(), special_flags=special_flags
            )
        else:
            self._surface.blit(
                surface, (pos - self.pos).ftup(), special_flags=special_flags
            )

    def blank(self):
        """Blanks the screen"""
        self._surface.fill((255, 255, 255))


class Draw(Component):
    def __init__(self, engine):
        super().__init__(engine)
        self.depths: dict[int, list[DRAW]] = {}

    def add(
        self,
        depth: int,
        surface: Surface,
        pos: vec2d,
        gui: bool = False,
        special_flags: int = 0,
    ):
        """Add an element to be drawn when called."""
        if not isinstance(depth, int):
            msg = (
                "Depth must be int\n"
                f"Depth: {depth}\n"
                f"Depth<type>: {type(depth)}\n"
            )
            raise TypeError(colorize(msg, "red"))
        try:
            self.depths[depth]
        except KeyError:
            self.depths[depth] = []
        self.depths[depth].append((surface, pos, gui, special_flags))

    def render(self, window: Camera):
        """Render all depths."""
        # Sort depths
        depths = sorted(self.depths)
        for i in depths:
            depth = self.depths[i]

            for draw in depth:
                window.draw_surface(*draw)

        self.depths = {}


class Window(Component):
    """Object for rendering to the screen."""

    def __init__(self, engine, size: vec2d):
        super().__init__(engine)
        display.init()
        size = size.floor()
        flags = HWSURFACE | DOUBLEBUF
        self.display = display.set_mode(size.ftup(), flags)
        self.size = size

    def render(self, camera: Camera):
        """Renders camera surface to screen."""
        surface = camera.surface
        self.display.blit(surface, (0, 0))

    def update(self):
        """Update screen."""
        display.flip()

    def blank(self):
        """Blanks the screen in-between frames."""
        self.display.fill((255, 255, 255))
