"""Handles loading and saving settings."""

from os import path
import json


from ..constants import cprint
from ..types import Component


class Settings(Component):
    def __init__(self, engine):
        super().__init__(engine)

        # Settings file
        self.settings_file = path.join(self.paths["settings"], "settings.json")

        # Settings
        self._volume = 0.5

        # Load settings from file
        if path.exists(self.settings_file):
            self.load()
        else:
            self.save()

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, volume: float):
        if 0.0 <= volume <= 1.0:
            self._volume = volume
            self.engine.aud.volume = volume

    def load(self):
        file = open(self.settings_file, "r")
        data = file.read()
        file.close()

        settings = json.loads(data)
        self.volume = settings["volume"]

        cprint("succesful settings load!", "green")

    def save(self):
        data = self._getdata()
        text = json.dumps(data, indent=4, separators=(", ", " : "))

        file = open(self.settings_file, "w")
        file.write(text)
        file.close()

        cprint("succesful settings save!", "green")

    def _getdata(self):
        data = {"volume": self.volume}
        return data
