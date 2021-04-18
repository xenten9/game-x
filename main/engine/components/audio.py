"""Handles game audio"""
from pygame import mixer
from os import path

class ObjMixer():
    """Handles all audio."""
    def __init__(self, game):
        self.game = game
        mixer.init(size=-16)
        self.sfx = ObjSFX(game)
        self.music = ObjMusic(game)

class ObjMusic():
    def __init__(self, game):
        self.game = game
        self.music_path = game.PATH['MUSIC']
        self.music = None
        self.music_queue = []
        self.fading = 1
        mixer.music.set_endevent(56709)
        mixer.music.set_endevent(56709)

    def load(self, file: str):
        """Load music."""
        music = path.join(self.music_path, file)
        mixer.music.load(music)
        self.music = file

    def play(self, loops=0):
        """Load music."""
        mixer.music.play(loops)

    def stop(self, fade=0):
        """Load music."""
        if fade == 0 and self.fading == 0:
            mixer.music.stop()
        else:
            mixer.music.fadeout(fade)
            self.fading = 1

    def pause(self):
        """Load music."""
        mixer.music.pause()

    def resume(self):
        """Load music."""
        mixer.music.unpause()

    def queue(self, file: str, loops: int, volume: float):
        """Queue up a song."""
        self.music_queue.append((file, loops, volume))

    def get_current(self):
        """Unload music."""
        if mixer.music.get_busy():
            return self.music
        return None

    def set_volume(self, vol: float):
        """Change volume."""

        mixer.music.set_volume(vol)

    def end(self):
        """Called when music ends."""
        self.music = None
        self.fading = 0
        if len(self.music_queue) > 0:
            music = self.music_queue.pop(0)
            file = music[0]
            loops = music[1]
            volume = music[2]
            self.load(file)
            self.set_volume(volume)
            self.play(loops)

class ObjSFX():
    def __init__(self, game):
        self.game = game
        self.sfx_path = game.PATH['SFX']
        self.tracks = {}

    def add(self, file: str):
        """add file to tracks."""
        try:
            self.tracks[file]
        except KeyError:
            sound = path.join(self.sfx_path, file)
            self.tracks[file] = mixer.Sound(sound)

    def remove(self, file: str):
        """remove file from tracks."""
        try:
            del self.tracks[file]
        except KeyError:
            print('file {} does not exist'.format(file))

    def play(self, file: str, loops=0):
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
