from pygame.image import load
from pygame import Surface, Rect
from os import path, listdir

from ..helper_functions.tuple_functions import (
    f_tupmult, f_tupgrid, f_tupround, f_tupadd)
from ..helper_functions.number_functions import (
    f_make_grid, f_change_grid_dimensions, f_minimize_grid)

# Tile map
class ObjTileMap():
    """Handles background and foreground graphics."""
    def __init__(self, game):
        self.game = game
        self.layers = {}
        self.tilemaps = {}
        self.tilemaps_list = []
        self.tilemap_path = game.PATH['TILEMAPS']
        self.clear()

    def add_tilemap(self, fname: str):
        """Adds a new tilemap to the tile_maps dictionary."""
        # Get image
        tile_set = load(path.join(self.tilemap_path, fname)).convert()
        new_tile_map = []
        half = self.game.HALFTILE

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

    def add_layer(self, layer: str, size: tuple, data: list, grid=None):
        """Creates a layer."""
        self.layers[layer] = ObjTileLayer(self.game, self, layer,
                                          size, data, grid)

    def remove_layer(self, layer: str):
        """Removes an existing layer."""
        try:
            del self.layers[layer]
        except KeyError:
            print('layer {} does not exist'.format(layer))

    def get_image(self, map_id: int, tile_id: int):
        """Gets tile image."""
        try:
            self.tilemaps[map_id]
        except KeyError:
            directory = listdir(self.tilemap_path)
            for file in directory:
                if int(file[0]) == map_id:
                    self.add_tilemap(file)
        return self.tilemaps[map_id][tile_id]

    def add_all(self):
        directory = listdir(self.tilemap_path)
        for file in directory:
            try:
                if int(file[0]):
                    self.add_tilemap(file)
            except TypeError:
                pass

    def clear(self):
        self.tilemaps = {}
        self.tilemaps_list = []
        self.add_tilemap('0-null.png')

# Layer with tiles
class ObjTileLayer():
    """Layer containing all of the tiles in a lookup form."""
    def __init__(self, game, tile_handler, name, size, data, grid=None):
        self.game = game
        self.tile = tile_handler
        self.name = name
        self.size = size
        if grid is None:
            grid = f_make_grid(size, None)
        self.grid = grid
        self.surface = None
        self.visible = True
        self.data = data
        try:
            self.parallax = f_tupadd((1, 1), f_tupmult(data['parallax'], -1))
        except KeyError:
            self.parallax = (0, 0)

    def update(self, dt):
        """Implement parallax."""
        pass

    def place(self, pos: tuple, tilemap_id: int, tile_id: int):
        """Add tiles to grid on the layer."""
        pos = f_tupround(f_tupmult(pos, 1/self.game.HALFTILE), -1)
        try:
            self.grid[pos[0]][pos[1]] = (tilemap_id, tile_id)
        except IndexError:
            if len(self.grid) == 0:
                size = (pos[0]+1, pos[1]+1)
            else:
                size = (max(pos[0] + 1, len(self.grid)),
                        max(pos[1] + 1, len(self.grid[0])))
            self.dialate(size)
            self.grid[pos[0]][pos[1]] = (tilemap_id, tile_id)

    def remove(self, pos):
        """Remove tiles from the grid on the grid."""
        pos = f_tupround(f_tupmult(pos, 1/self.game.HALFTILE), -1)
        try:
            self.grid[pos[0]][pos[1]] = None
        except IndexError:
            pass

    def draw(self, window):
        """Draw tiles."""
        if self.visible:
            if self.game.parallax == 1 and self.parallax != (0, 0):
                pos = f_tupmult(window.pos, self.parallax)
                pos = f_tupgrid(pos, 1)
                window.draw_image(pos, self.surface)
            else:
                window.draw_image((0, 0), self.surface)

    def toggle_visibility(self):
        """Turn layer invisible."""
        self.visible = not self.visible

    def dialate(self, size):
        """Change the size of the grid."""
        self.size = size
        self.grid = f_change_grid_dimensions(self.grid, size, None)

    def minimize(self):
        """Get rid of empty rows and columns."""
        self.grid = f_minimize_grid(self.grid, None)

    def cache(self):
        """Cache grid to memory and update the surface to match the current grid."""
        size = f_tupmult(self.size, self.game.HALFTILE)
        self.surface = Surface(size).convert_alpha()
        self.surface.fill([0, 0, 0, 0])
        for column in enumerate(self.grid):
                for row in enumerate(self.grid[column[0]]):
                    tile_info = self.grid[column[0]][row[0]]
                    if tile_info is not None:
                        self.half_tile = self.game.HALFTILE
                        tile = self.tile.get_image(*tile_info)
                        pos = f_tupmult((column[0], row[0]),
                                        self.half_tile)
                        self.surface.blit(tile, pos)
