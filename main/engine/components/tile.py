
from os import path, listdir
from typing import List

from pygame.image import load
from pygame import Surface, Rect, draw

from .grid import f_make_grid, f_change_grid_dimensions, f_minimize_grid
from ..types.vector import vec2d
from ..types.component import Component
from .draw import Draw

# Tile map
class TileMap(Component):
    """Handles background and foreground graphics."""
    def __init__(self, engine: object):
        super().__init__(engine)
        self.layers = {}
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
        self.add_tilemap('0-null.png')

    def clear_ent(self):
        self.layers = {}

# Layer with tiles
class TileLayer(Component):
    """Layer containing all of the tiles in a lookup form."""
    def __init__(self, engine: object, tile_handler: TileMap, name: str,
                 size: vec2d, data: dict, grid: List[List] = None):
        super().__init__(engine)
        self.tile = tile_handler
        self.name = name
        self.size = size
        if grid is None:
            grid = f_make_grid(size, None)
        self.grid = grid
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
        try:
            self.grid[x][y] = (tilemap_id, tile_id)
        except IndexError:
            if len(self.grid) == 0:
                size = vec2d(x + 1, y + 1)
            else:
                size = vec2d(max(x + 1, len(self.grid)),
                        max(y + 1, len(self.grid[0])))
            self.dialate(size)
            self.grid[x][y] = (tilemap_id, tile_id)

    def remove(self, pos: vec2d):
        """Remove tiles from the grid on the grid."""
        x, y = pos // (self.fulltile // 2)
        try:
            self.grid[x][y] = None
        except IndexError:
            pass

    def draw(self, draw: Draw):
        """Draw tiles."""
        if self.visible:
            surface = self.surface
            depth = self.depth
            if self.engine.parallax and self.parallax != vec2d(0, 0):
                pos = (self.engine.cam.pos * self.parallax).floor()
                self.engine.draw.add(depth, pos=pos, surface=surface)
            else:
                pos = vec2d(0, 0)
                self.engine.draw.add(depth, pos=pos, surface=surface)

    def toggle_visibility(self):
        """Turn layer invisible."""
        self.visible = not self.visible

    def dialate(self, size: vec2d):
        """Change the size of the grid."""
        self.size = size
        self.grid = f_change_grid_dimensions(self.grid, size, None)
        surface = Surface(size * self.fulltile).convert_alpha()
        surface.fill((0, 0, 0, 0))
        surface.blit(self.surface, vec2d(0, 0))
        self.surface = surface

    def minimize(self):
        """Get rid of empty rows and columns."""
        self.grid = f_minimize_grid(self.grid, None)

    def cache(self):
        """Cache grid to surface."""
        halftile = (self.fulltile // 2)
        size = self.size * halftile
        self.surface = Surface(size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))

        # Iterate through grid
        for column, _ in enumerate(self.grid):
            for row, cell in enumerate(self.grid[column]):
                if cell is not None:
                    tile = self.tile.get_image(*cell)
                    pos = vec2d(column, row) * halftile
                    self.surface.blit(tile, pos)

    def cache_partial(self, pos: vec2d):
        """Cache tile to Surface."""
        halftile = self.fulltile // 2
        x, y = pos // halftile
        try:
            tile_info = self.grid[x][y]
        except IndexError:
            pass
        else:
            # Replace singular tile
            if tile_info is None:
                color = (0, 0, 0, 0)
                rect = Rect((x, y), vec2d(1, 1) * halftile)
                draw.rect(self.surface, color, rect)
            else:
                tile = self.tile.get_image(*tile_info)
                self.surface.blit(tile, pos)
