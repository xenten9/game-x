"""Handles rendering, loading and modifying tilemaps and tile layers."""
# Standard library
from os import path, listdir
from typing import Dict, List, Tuple

# External libraries
from pygame.image import load
from pygame import Surface, Rect, draw

# Local imports
from ..types.array import array2d
from ..types.vector import vec2d
from ..types.component import Component
from .draw import Draw
from ...constants import colorize

class TileMap(Component):
    """Handles background and foreground graphics."""
    def __init__(self, engine: object):
        super().__init__(engine)
        self.layers: Dict[str, TileLayer] = {}
        self.tilemaps = {}
        self.tilemaps_list = []
        self.clear_cache()

    def add_tilemap(self, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        # Get image
        tile_set = load(path.join(self.paths['tilemaps'], fname)).convert()
        new_tile_map = []
        half = self.fulltile // 2

        # Iterate through each tile in image
        for xpos in range(round((tile_set.get_width() / half))):
            # New surface
            surface = Surface((half, half))

            # Write section of image to surface
            surface.blit(tile_set, (0, 0),
                         area=Rect((xpos * (half), 0),
                                   (half, half)))

            # Add surface to tilemap
            new_tile_map.append(surface)

        # Add tilemap to list of tilemaps
        index = int(fname[0])
        self.tilemaps[index] = new_tile_map
        self.tilemaps_list.append(index)

    def remove_tilemap(self, map_id: int):
        """Removes a tilemap from the tile_maps dictionary."""
        try:
            del self.tilemaps[map_id]
        except KeyError:
            print('tilemap {} does not exist'.format(map_id))

    def add_layer(self, name: str, size: vec2d,
                  data: dict, grid: List[List] = None):
        """Creates a layer."""
        self.layers[name] = TileLayer(
            self.engine, self, name, size, data, grid)

    def remove_layer(self, name: str):
        """Removes an existing layer."""
        try:
            del self.layers[name]
        except KeyError:
            print('layer {} does not exist'.format(name))

    def get_image(self, map_id: int, tile_id: int):
        """Gets tile image."""
        try:
            self.tilemaps[map_id]
        except KeyError:
            directory = listdir(self.paths['tilemaps'])
            for file in directory:
                if int(file[0]) == map_id:
                    self.add_tilemap(file)
                    return self.tilemaps[map_id][tile_id]
            code = ['Tilemap not found.',
                    'Tilemap dir: {}'.format(self.paths['tilemaps']),
                    'Tilemap id: {}'.format(map_id)]
            code = '\n  ' + '\n  '.join(code)
            raise FileNotFoundError(colorize(code, 'red'))
        return self.tilemaps[map_id][tile_id]

    def add_all(self):
        directory = listdir(self.paths['tilemaps'])
        for file in directory:
            try:
                if int(file[0]):
                    self.add_tilemap(file)
            except TypeError:
                pass

    def clear_cache(self):
        self.tilemaps = {}
        self.tilemaps_list = []
        try:
            self.add_tilemap('0-null.png')
        except FileNotFoundError:
            code = ['Tilemap not found.',
                    'Tilemap dir: {}'.format(self.paths['tilemaps']),
                    'Tilemap name: {}'.format('0-null.png')]
            raise FileNotFoundError('\n  ' + '\n  '.join(code))

    def clear_ent(self):
        self.layers = {}

# Layer with tiles
class TileLayer(Component):
    """Layer containing all of the tiles in a lookup form."""
    def __init__(self, engine: object, tile_handler: TileMap, name: str,
                 size: vec2d, data: dict, array: List[List] = None):
        super().__init__(engine)
        self.tile = tile_handler
        self.name = name
        self.size = size
        self.array = array2d(size)
        if array is not None:
            self.array._array = array
        self.surface = Surface((0, 0))
        self.visible = True
        self.data = data
        try:
            self.parallax = vec2d(1, 1) - vec2d(*data['parallax'])
        except KeyError:
            self.parallax = vec2d(0, 0)
        try:
            self.depth = data['depth']
        except KeyError:
            self.depth = 0

    def update(self):
        try:
            self.depth = self.data['depth']
        except KeyError:
            pass

    def place(self, pos: vec2d, tilemap_id: int, tile_id: int):
        """Add tiles to grid on the layer."""
        x, y = pos // (self.fulltile // 2)
        self.array.set(x, y, (tilemap_id, tile_id))

    def remove(self, pos: vec2d):
        """Remove tiles from the grid on the grid."""
        x, y = pos // (self.fulltile // 2)
        try:
            self.array.delete(x, y)
        except IndexError:
            pass

    def draw(self, draw: Draw):
        """Draw tiles."""
        if self.visible:
            if self.size != self.array.size:
                self.size = self.array.size
                surface = Surface(vec2d(*self.array.size) * self.fulltile)
                surface = surface.convert_alpha()
                surface.fill((0, 0, 0, 0))
                surface.blit(self.surface, vec2d(0, 0))
            surface = self.surface
            depth = self.depth
            if self.engine.parallax and self.parallax != vec2d(0, 0):
                pos = (self.engine.cam.pos * self.parallax).floor()
            else:
                pos = vec2d(0, 0)
            draw.add(depth, pos=pos, surface=surface)

    def toggle_visibility(self):
        """Turn layer invisible."""
        self.visible = not self.visible

    def minimize(self):
        """Get rid of empty rows and columns."""
        self.array.minimize()

    def cache(self):
        """Cache grid to surface."""
        halftile = (self.fulltile // 2)
        size = self.size * halftile
        self.surface = Surface(size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))

        # Iterate through grid
        for x in range(self.array.width):
            for y in range(self.array.height):
                cell = self.array.get(x, y)
                if isinstance(cell, tuple):
                    tile = self.tile.get_image(*cell)
                    pos = vec2d(x, y) * halftile
                    self.surface.blit(tile, pos)

    def cache_partial(self, pos: vec2d):
        """Cache tile to Surface."""
        halftile = self.fulltile // 2
        x, y = (pos // halftile)
        try:
            tile_info = self.array.get(x, y)
        except IndexError:
            pass
        else:
            # Replace singular tile
            if tile_info is None:
                color = (0, 0, 0, 0)
                rect = Rect((x, y), vec2d(1, 1) * halftile)
                draw.rect(self.surface, color, rect)
            elif isinstance(tile_info, tuple):
                tile = self.tile.get_image(*tile_info)
                size = self.surface.get_size()
                size = vec2d(*size) // 16
                if x >= size.x or y >= size.y:
                    new_size = vec2d(max(x + 1, size.x) * 16, max(y + 1, size.y) * 16)
                    new_surface = Surface(new_size.ftup()).convert_alpha()
                    new_surface.fill((0, 0, 0, 0))
                    new_surface.blit(self.surface, (0, 0))
                    self.surface = new_surface
                self.surface.blit(tile, pos)
