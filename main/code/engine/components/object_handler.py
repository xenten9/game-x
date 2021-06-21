from typing import Any, Callable
from os import path

from pygame.surface import Surface
from pygame import draw as pydraw, Rect
import json
import uuid

from main.code.engine.components.output_handler import Draw
from main.code.engine.types import Component, array2d, vec2d
from main.code.engine.types.entity import Entity
from main.code.engine.constants import colorize, cprint


class ObjectHandler(Component):
    def __init__(self, engine, create_object: Callable):
        super().__init__(engine)
        self.level = LevelHandler(engine)
        self.ent = EntityHandler(engine)
        self.tile = TileHandler(engine)
        self.col = CollisionHandler(engine)
        self.create_object = create_object

    # Base methods
    def update(self):
        self.ent.update()

    def draw(self, draw: Draw):
        self.ent.draw(draw)
        self.tile.draw(draw)

    def clear(self):
        self.ent.clear()
        self.tile.clear()


# Level
class LevelHandler(Component):
    """Object which loads and saves levels."""

    def __init__(self, engine):
        super().__init__(engine)
        self.current_level = ""
        self.size = vec2d(0, 0)

    def load(self, level_name: str):
        """Load level parts such as GameObjects and Tiles."""
        # Get level name
        level = path.join(self.paths["levels"], level_name + ".json")
        if not path.exists(level):
            msg = (
                "LEVEL ERROR\n"
                f"path: {level}\n"
                f"level name: {level_name}\n"
                "level not found\n"
            )
            raise FileNotFoundError(colorize(msg, "red"))

        # Load level file
        level_name = path.join(self.paths["levels"], level_name)
        file = open(level_name + ".json", "r")
        contents = file.read()
        file.close()

        # Parse level data
        level_data: list[list] = json.loads(contents)
        obj_list = []

        # Go through all objects
        for obj in level_data:
            # Parse all objects in list
            name = obj[0]

            # Tile layer
            if name == "tile-layer":
                layername, array, data = obj[1:4]
                for column, _ in enumerate(array):
                    for row, cell in enumerate(array[column]):
                        if cell is not None:
                            array[column][row] = tuple(cell)
                data = dict(data)
                obj_list.append([name, layername, array, data])

            # Static collider
            elif name == "static-collider":
                array = obj[1]
                obj_list.append([name, array])

            # Any game object
            else:
                pos, key, data = obj[1:4]
                pos = tuple(pos)
                key = int(key)
                data = dict(data)
                obj_list.append([name, pos, key, data])

        # Clear level
        if self.current_level != level_name:
            self.engine.assets.clear()
        self.engine.objects.clear()

        # Create level
        for arg in obj_list:
            name = arg[0]

            # Create tile layers
            if name == "tile-layer":
                layer_name, array, data = arg[1:4]
                self.engine.objects.tile.add(layer_name, data, array)

            # Create static collider
            elif name == "static-collider":
                array = arg[1]
                self.size = vec2d(len(array), len(array[0])) * self.fulltile
                self.engine.objects.col.st.array.array = array

                # Update camera level size to bind camera position
                try:
                    self.engine.cam.level_size
                except AttributeError:
                    msg = "Camera has no variable: level_size"
                    cprint(msg, "yellow")
                else:
                    self.engine.cam.level_size = self.size

            # Create object
            else:
                pos, key, data = arg[1:4]
                pos = vec2d(*pos)
                args = {"name": name, "pos": pos, "data": data, "key": key}
                self.engine.objects.create_object(self.engine, **args)

        # Render all layers after being built
        for layer in self.engine.objects.tile.layers:
            layer.cache()

        # Say level succesful level laod if level is no reloaded
        if self.current_level != level_name:
            cprint("successful level load!", "green")

        # Update current level
        self.current_level = level_name
        self.engine.objects.ent.create()

    def save(self, level_name: str):
        """Saves level to level path."""
        # Compile level parts
        obj_list = []

        # Write layers
        for layer in self.engine.objects.tile.layers:
            info = ["tile-layer", layer.name, layer.array._array, layer.data]
            obj_list.append(info)

        # Write stcol
        col = self.engine.objects.col.st
        info = ["static-collider", col.array.array]
        obj_list.append(info)

        # Write each object to file
        for key, obj in self.engine.objects.ent.obj.items():
            info = [obj.name, obj.pos.ftup(), key, obj.data]
            obj_list.append(info)

        # Create json dump
        new_list = []
        for item in obj_list:
            new_list.append(NoIndent(item))
        data = json.dumps(new_list, indent=4, cls=NoIndentEncoder)
        data.replace(",\n", ", \n")
        if data.endswith("]]") or data.endswith("}]"):
            data = data[1:-1] + "\n" + data[-1]

        # Write to file
        level = open(
            path.join(self.paths["levels"], level_name + ".json"), "w"
        )
        level.write(data)
        level.close()
        cprint("successful level save!", "green")

    def reset(self):
        """Restart current level."""
        self.load(self.current_level)


class NoIndent(object):
    """Value wrapper."""

    def __init__(self, value):
        self.value = value


class NoIndentEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(NoIndentEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs["indent"]
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super(NoIndentEncoder, self).default(o)

    def encode(self, o):
        result = super(NoIndentEncoder, self).encode(o)
        for k, v in iter(self._replacement_map.items()):
            result = result.replace('"@@%s@@"' % (k,), v)
        return result


# Entity
class EntityHandler(Component):
    def __init__(self, engine):
        super().__init__(engine)

        self.obj: dict[int, Any] = {}
        self.sobj: dict[str, Any] = {}

        self.pool = set(range(2 ** 12))

        self.visible: bool = True

    # Base methods
    def create(self):
        for _, obj in self.obj.items():
            try:
                obj.create()
            except AttributeError:
                pass

        for _, obj in self.sobj.items():
            try:
                obj.create()
            except AttributeError:
                pass

    def delete(self, key: int):
        del self.obj[key]
        self.pool.add(key)

    def update(self):
        objcopy = self.obj.copy()
        for _, obj in objcopy.items():
            obj.update(self.engine.paused)

        for _, obj in self.sobj.items():
            obj.update(self.engine.paused)

    def draw(self, draw: Draw):
        if self.visible:
            for _, obj in self.obj.items():
                obj.draw(draw)

        for _, obj in self.sobj.items():
            obj.draw(draw)

    def clear(self):
        self.obj.clear()
        self.pool = set(range(2 ** 12))

    # Creation
    def add(self, entity, key: int = None, check: bool = False):
        if key is None:
            key = self._get_key()
        elif check:
            key = self._check_key(key)
        self.obj[key] = entity

    def _get_key(self) -> int:
        return self.pool.pop()

    def _check_key(self, key: int) -> int:
        if key in self.pool:
            self.pool.remove(key)
            return key
        else:
            newkey = self._get_key()
            if key is not None:
                cprint(f"key {key} is not in pool!", "yellow")
                cprint(f"replacing keys: {key} -> {newkey}!", "yellow")
            return newkey


# Tile
class TileHandler(Component):
    def __init__(self, engine):
        super().__init__(engine)
        self.layers: list[TileLayer] = []

        self.visible: bool = True

    # Base methods
    def draw(self, draw: Draw):
        if self.visible:
            for layer in self.layers:
                layer.draw(draw)

    # External
    def add(self, name: str, data: dict = {}, array: list[list] = None):
        """Add a new tile layer."""
        # Create layer
        if array is None:
            layer = TileLayer(self.engine, name, data)
        else:
            layer = TileLayer(self.engine, name, data, array)

        # Add layer
        self.layers.append(layer)

    def remove_layer(self, name: str):
        """Remove tile layer by name."""
        for i, layer in enumerate(self.layers):
            if layer.name == name:
                del self.layers[i]

    def clear(self):
        """Remove all tile layers."""
        self.layers = []


class TileLayer(Component):
    def __init__(
        self, engine, name: str, data: dict, array: list[list] = None
    ):
        super().__init__(engine)
        self.name = name
        self.depth = 0
        self.visible = True

        self.array = array2d((16, 16))
        if array is not None:
            self.array.array = array

        self.surface: Surface = Surface((1, 1))
        self.cache()

        self.data = data
        self.update()

    # Base methods
    def update(self):
        # Depth
        try:
            self.depth = self.data["depth"]
        except KeyError:
            pass

        # Parallax
        try:
            self.parallax = vec2d(1, 1) - vec2d(*self.data["parallax"])
        except KeyError:
            self.parallax = vec2d(0, 0)

    def draw(self, draw: Draw):
        """Draw tilelayer to screen."""
        if self.visible:
            if self.engine.parallax and self.parallax != vec2d.zero():
                pos = (self.engine.cam.pos * self.parallax).floor()
            else:
                pos = vec2d.zero()
            draw.add(self.depth, self.surface, pos)

    # External Interactions
    def place(self, pos: vec2d, tilemap_id: int, tile_id: int):
        """Add tiles to grid on the layer."""
        x, y = (pos // (self.fulltile // 2)).ftup()
        self.array.set(x, y, (tilemap_id, tile_id))

    def remove(self, pos: vec2d):
        """Remove tiles from the grid on the grid."""
        x, y = (pos // (self.fulltile // 2)).ftup()
        try:
            self.array.delete(x, y)
        except IndexError:
            pass

    def minimize(self):
        """Get rid of empty rows and columns."""
        self.array.minimize()

    # Caching
    def cache(self):
        surface_size = (vec2d(*self.array.size) * self.halftile).ftup()
        self.surface = Surface(surface_size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))

        # Iterate through array
        for x in range(self.array.width):
            for y in range(self.array.height):
                tile_info = self.array.get(x, y)
                if isinstance(tile_info, tuple):
                    tile = self.engine.assets.tiles.get(tile_info)
                    pos = (x * self.halftile, y * self.halftile)
                    self.surface.blit(tile, pos)

    def cache_partial(self, pos: vec2d):
        """Cache tile to Surface."""
        x, y = (pos // self.halftile).ftup()
        try:
            tile_info = self.array.get(x, y)
        except IndexError:
            pass
        else:
            # Replace singular tile
            if tile_info is None:  # Clear tile at position
                color = (0, 0, 0, 0)
                rect = Rect(pos.ftup(), (vec2d(1, 1) * self.halftile).ftup())
                pydraw.rect(self.surface, color, rect)

            elif isinstance(tile_info, tuple):  # Draw tile at position
                tile = self.engine.assets.tiles.get(tile_info)
                size = vec2d(*self.surface.get_size()) // 16

                if x >= size.x or y >= size.y:
                    # Create new larger surface with old data
                    new_size = vec2d(
                        max(x + 1, size.x) * 16, max(y + 1, size.y) * 16
                    )
                    new_surface = Surface(new_size.ftup()).convert_alpha()
                    new_surface.fill((0, 0, 0, 0))
                    new_surface.blit(self.surface, (0, 0))
                    self.surface = new_surface

                # Draw tile
                self.surface.blit(tile, pos.ftup())


# Collision
class CollisionHandler(Component):
    def __init__(self, engine):
        super().__init__(engine)
        self.dy = DynamicCollider(engine)
        self.st = StaticCollider(engine)


class StaticCollider(Component, Entity):
    """Handles static collisions aligned to a grid."""

    def __init__(self, engine):
        super().__init__(engine)
        self.array = array2d((16, 16))
        self.visible = True

    def add(self, pos: vec2d):
        """Add a wall at a given position."""
        pos //= self.fulltile
        x, y = pos.ftup()
        self.array.set(x, y, True)

    def remove(self, pos: vec2d):
        """Remove a wall at a given position."""
        pos //= self.fulltile
        x, y = pos.ftup()
        self.array.delete(x, y)

    def get(self, pos: vec2d) -> bool:
        """Check for a collision at a given position."""
        pos //= self.fulltile
        x, y = pos.ftup()
        try:
            if self.array.get(x, y):
                return True
            else:
                return False
        except IndexError:
            return False

    def clear(self):
        """Clear all Static collision points off of grid"""
        self.array = array2d((16, 16))

    def draw(self, draw: Draw):
        size = (vec2d(*self.array.size) * self.fulltile).ftup()
        surface = Surface(size).convert_alpha()
        surface.fill((0, 0, 0, 0))
        color = (16, 16, 16)
        size = (vec2d(1, 1) * self.fulltile).ftup()
        if self.visible:
            for x in range(self.array.width):
                for y in range(self.array.height):
                    if self.array.get(x, y):
                        pos = vec2d(x, y) * self.fulltile
                        rect = Rect(pos.ftup(), size)
                        pydraw.rect(surface, color, rect)
            pos = vec2d(0, 0)
            draw.add(0, pos=pos, surface=surface)

    def minimize(self):
        self.array.minimize()


class DynamicCollider(Component):
    """Handles collisions with moving objects."""

    def __init__(self, engine):
        super().__init__(engine)
        self.colliders: dict[int, object] = {}

    def get_colliders(self) -> list[Any]:
        return [self.colliders[collider] for collider in self.colliders]

    def add(self, key: int, obj: object):
        """Adds a collider to self.colliders."""
        self.colliders[key] = obj

    def remove(self, key: int):
        """Removes a collider to self.colliders."""
        try:
            del self.colliders[key]
        except KeyError:
            pass

    def clear(self):
        """Remove all colliders."""
        self.colliders = {}
