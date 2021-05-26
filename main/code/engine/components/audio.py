"""Handles game audio"""
# Standard library
from typing import Union
from os import path

# External libraries
from pygame import mixer

# Local imports
from ..types.component import Component
from ..constants import cprint

class Mixer(Component):
    """Handles all audio."""
    def __init__(self, engine: object):
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
    def __init__(self, engine: object, mix: Mixer):
        super().__init__(engine)
        self.mixer = mix
        self.music = None
        self.music_queue = None
        self.fading = False
        self.paused = False
        self._volume = 1.0
        mixer.music.set_volume(self.volume * self.main_volume)
        mixer.music.set_endevent(56709)

    @property
    def main_volume(self):
        return self.mixer.volume

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
        music = path.join(self.paths['music'], file)
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
    def __init__(self, engine: object, mix: Mixer):
        super().__init__(engine)
        self.mixer = mix
        self.tracks: dict[str, mixer.Sound] = {}
        self.tvolume: dict[str, float] = {}

    @property
    def main_volume(self) -> float:
        return self.mixer.volume

    def update_volume(self):
        for key in self.tracks:
            self.tracks[key].set_volume(self.tvolume[key] * self.main_volume)

    def add(self, file: str, volume: float = 1.0):
        """add file to tracks."""
        try:
            self.tracks[file]
        except KeyError:
            sound = path.join(self.paths['sfx'], file)
            self.tracks[file] = mixer.Sound(sound)
            self.tvolume[file] = volume
            vol = self.tvolume[file] * self.main_volume
            self.tracks[file].set_volume(vol)

    def remove(self, file: str):
        """remove file from tracks."""
        try:
            del self.tracks[file]
        except KeyError:
            cprint('file {} does not exist'.format(file), 'red')

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
