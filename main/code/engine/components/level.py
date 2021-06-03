"""Loads and saves levels from disk."""

import json
import uuid
from os import path
from typing import Union

from ..constants import colorize, cprint
from ..types import Component, vec2d
from .tile import TileLayer


class Level(Component):
    """Object which loads and saves levels."""

    def __init__(self, engine):
        super().__init__(engine)
        self.current_level = ""
        self.size = vec2d(0, 0)

    def load(self, level_name: Union[str, None] = None):
        """Load level parts such as GameObjects and Tiles."""
        # Get level name
        if level_name is None:
            while level_name in ("", None):
                level_name = input("Load level name? ")
                if level_name in ("", None):
                    cprint("Improper level name.", "yellow")
                elif level_name == "exit":
                    return
                else:
                    level = path.join(
                        self.paths["levels"], level_name + ".json"
                    )
                    if not path.exists(level):
                        level_name = None
                        cprint("Level not found.", "yellow")
        else:
            level = path.join(self.paths["levels"], level_name + ".json")
            if not path.exists(level):
                msg = (
                    "LEVEL ERROR\n"
                    f"path: {level}\n"
                    f"level name: {level_name}\n"
                    "level not found\n"
                )
                raise FileNotFoundError(colorize(msg, "red"))
        if not isinstance(level_name, str):
            return

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
            self.engine.clear_cache()
        self.engine.clear_ent()

        # Create level
        for arg in obj_list:
            name = arg[0]

            # Create tile layers
            if name == "tile-layer":
                layer_name, array, data = arg[1:4]
                size = vec2d(len(array), len(array[0]))
                self.engine.tile.add_layer(layer_name, size, data, array)

            # Create static collider
            elif name == "static-collider":
                array = arg[1]
                self.size = vec2d(len(array), len(array[0])) * self.fulltile
                self.engine.col.st.array.array = array

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
                self.engine.obj.create_object(**args)

        # Render all layers after being built
        for layer in self.engine.tile.layers:
            self.engine.tile.layers[layer].cache()

        # Say level succesful level laod if level is no reloaded
        if self.current_level != level_name:
            cprint("successful level load!", "green")

        # Update current level
        self.current_level = level_name
        self.engine.obj.post_init()

    def save(self, level_name: Union[str, None] = None):
        """Saves level to level path."""
        # Get level name
        if level_name is None:
            while level_name in ("", None):
                level_name = input("save level name? ")
                if level_name == "":
                    cprint("improper level name.", "yellow")
                elif level_name == "exit":
                    return
        if level_name is None:
            raise ValueError(colorize("level name is None!", "red"))

        # Compile level parts
        obj_list = []

        # Write layers
        for name, layer in self.engine.tile.layers.items():
            if isinstance(layer, TileLayer):
                info = ["tile-layer", name, layer.array._array, layer.data]
                obj_list.append(info)

        # Write stcol
        col = self.engine.col.st
        info = ["static-collider", col.array.array]
        obj_list.append(info)

        # Write each object to file
        for key, obj in self.engine.obj.obj.items():
            info = [obj.name, obj.pos, key, obj.data]
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


# Json encoding stuffs
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
