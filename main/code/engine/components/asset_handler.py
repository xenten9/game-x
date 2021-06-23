from os import path, listdir
import re

from pygame.surface import Surface
from pygame.image import load
from pygame import font, Rect

from main.code.engine.types import Component
from main.code.engine.constants import colorize


class AssetHandler(Component):
    def __init__(self, engine):
        super().__init__(engine)
        # self.audio = Audio(engine)
        self.sprites = Sprites(engine)
        self.tiles = Tiles(engine)
        self.font = Font(engine)

    def clear(self):
        # self.audio.clear()
        self.tiles.clear()
        self.font.clear()


# NOTE to be created as an object for loading sfx and music
# class Audio(Component):
#     def __init__(self, engine):
#         super().__init__(engine)
#         self.dir_music = self.paths["music"]
#         self.dir_sfx = self.paths["sfx"]


class Sprites(Component):
    def get(self, alpha: bool, *fname: str) -> list[Surface]:
        sprites: list[Surface] = []
        for name in fname:
            sprites.append(load(path.join(self.paths["sprites"], name)))
        if alpha:
            sprites = [sprite.convert_alpha() for sprite in sprites]
        else:
            sprites = [sprite.convert() for sprite in sprites]
        return sprites


class Tiles(Component):
    def __init__(self, engine):
        super().__init__(engine)
        self.tilemaps: dict[int, list[Surface]] = {}
        self.add_tilemap("0-null.png")

    def add_tilemap(self, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        # Get image
        tile_set = load(path.join(self.paths["tilemaps"], fname)).convert()
        new_tile_map = []

        # Iterate through each tile in image
        for xpos in range(round((tile_set.get_width() / self.halftile))):
            # New surface
            surface = Surface((self.halftile, self.halftile))

            # Write section of image to surface
            area = Rect(self.halftile * xpos, 0, self.halftile, self.halftile)
            surface.blit(tile_set, (0, 0), area)

            # Add surface to tilemap
            new_tile_map.append(surface)

        # Add tilemap to list of tilemaps
        number = re.search(r"[0-9]+-", fname)
        if number is not None:
            index = int(number[0].removesuffix("-"))
            self.tilemaps[index] = new_tile_map
        else:
            msg = f"Could not find map id index.\nMap name {fname}"
            raise ValueError(msg)

    def add_all(self):
        """Load all of the tilemaps."""
        # Get all tile maps
        directory = listdir(self.paths["tilemaps"])
        for file in directory:
            if re.match(r"[0-9]+", file) is not None:
                self.add_tilemap(file)

    def get(self, tile_info: tuple) -> Surface:
        if tile_info[0] in self.tilemaps:
            # Return tile
            tilemap = self.tilemaps[tile_info[0]]
            if len(tilemap) - 1 >= tile_info[1]:
                return tilemap[tile_info[1]]
            else:
                msg = (
                    "Tile outside of tilemap.\n"
                    f"Tilemap id: {tile_info[0]}\n"
                    f"Tilemap length: {len(tilemap)}\n"
                    f"Tilemap position: {tile_info[1]}\n"
                )
                raise IndexError(colorize(msg, "red"))

        else:
            # Try to find tile map and return tile
            for file in listdir(self.paths["tilemaps"]):
                if re.match(f"{tile_info[0]}-", file) is not None:
                    self.add_tilemap(file)
                    return self.tilemaps[tile_info[0]][tile_info[1]]
        msg = (
            "Tilemap not found.\n"
            f"Tilemap dir: {self.paths['tilemaps']}\n"
            f"Tilemap id: {tile_info[0]}\n"
        )
        raise FileNotFoundError(colorize(msg, "red"))

    def clear(self):
        self.tilemaps = {}


class Font(Component):
    """Object for handling fonts."""

    def __init__(self, engine):
        super().__init__(engine)
        font.init()
        self.fonts = {"arial12": font.SysFont("arial", 12)}

    def add(self, name: str, size: int):
        """Adds a font to self."""
        try:
            return self.fonts[name + str(size)]
        except KeyError:
            self.fonts[name + str(size)] = font.SysFont(name, size)
            return self.fonts[name + str(size)]

    def get(self, name: str, size: int):
        """Returns a font object."""
        try:
            return self.fonts[name + str(size)]
        except KeyError:
            return self.add(name, size)

    def clear(self):
        self.fonts.clear()

    def __del__(self):
        font.quit()
