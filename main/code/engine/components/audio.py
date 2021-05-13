"""Handles game audio"""
# Standard library
from typing import Union
from os import path

# External libraries
from pygame import mixer

# Local imports
from ..types.component import Component

class Mixer(Component):
    """Handles all audio."""
    def __init__(self, engine: object):
        super().__init__(engine)
        mixer.init(size=-16)
        self.sfx = SFX(engine)
        self.music = Music(engine)

class Music(Component):
    def __init__(self, engine: object):
        super().__init__(engine)
        self.music = None
        self.music_queue = []
        self.fading = False
        self.paused = False
        self._volume = 1
        self._music_volume = 1
        mixer.music.set_volume(self.music_volume * self.volume)
        mixer.music.set_endevent(56709)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume: float):
        if 0 <= volume <= 1:
            self._volume = volume
            mixer.music.set_volume(self.music_volume * self.volume)

    @property
    def music_volume(self):
        return self._music_volume

    @music_volume.setter
    def music_volume(self, volume: float):
        if 0 <= volume <= 1:
            self._music_volume = volume
            mixer.music.set_volume(self.music_volume * self.volume)

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
        self.music_queue.append((file, loops, volume))

    def get_current(self) -> Union[str, None]:
        """Unload music."""
        if mixer.music.get_busy():
            return self.music
        return None

    def end(self):
        """Called when music ends."""
        self.music = None
        self.fading = False
        if len(self.music_queue) > 0:
            music = self.music_queue.pop(0)
            file = music[0]
            loops = music[1]
            volume = music[2]
            self.load(file)
            self.music_volume = volume
            self.play(loops)

class SFX(Component):
    def __init__(self, engine: object):
        super().__init__(engine)
        self.tracks = {}

    def add(self, file: str):
        """add file to tracks."""
        try:
            self.tracks[file]
        except KeyError:
            sound = path.join(self.paths['sfx'], file)
            self.tracks[file] = mixer.Sound(sound)

    def remove(self, file: str):
        """remove file from tracks."""
        try:
            del self.tracks[file]
        except KeyError:
            print('file {} does not exist'.format(file))

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

    def volume(self, file: str, vol: float):
        """vol is a float from 0 to 1."""
        self.tracks[file].set_volume(vol)
