"""Objects exclusive to the level editor."""

from ast import literal_eval
from os import path
from typing import Optional


from numpy import sign
from pygame import Surface, image


from ..constants import FULLTILE
from ..engine.components.draw import Draw
from ..engine.components.maths import f_loop
from ..engine.components.tile import TileLayer
from ..engine.constants import colorize
from ..engine.engine import Engine
from ..engine.types.entity import Entity
from ..engine.types import vec2d


class Object(Entity):
    """Game objects in the level_editor."""

    def __init__(
        self, engine: Engine, name: str, key: int, pos: vec2d, data: dict
    ):
        self.engine = engine
        self.name = name
        self.key = key
        self.pos = pos
        self.data = data
        engine.obj.instantiate_object(key, self)
        devsprite_path = engine.paths["devsprites"]
        file_path = path.join(devsprite_path, name + ".png")
        try:
            self.image = image.load(file_path)
        except FileNotFoundError as error:
            msg = (
                "Sprite image not found."
                f"Images path: {file_path}"
                f"Engine sprite path: {devsprite_path}"
            )
            raise FileNotFoundError(colorize(msg, "red")) from error

    def draw(self, draw):
        """Draw call."""
        draw.add(0, pos=self.pos, surface=self.image)


class ObjCursor(Entity):
    """Object used for level editing."""

    def __init__(self, engine: Engine, pos: vec2d):
        # Default variables
        self.engine = engine
        self.pos: vec2d = pos
        self.color = (192, 192, 192)
        self.name = "cursor"
        self.engine.obj.sobj[self.name] = self
        self.rel = vec2d(0, 0)

        # Modes
        self.mode = 0
        self.obj_select = 0
        self.tile_select = 0
        self.tilemap_select = 0
        self.tilemap_id = engine.tile.tilemaps_list[self.tilemap_select]
        self.tilemap = self._get_current_tilemap()
        self.layer = 0
        self.selected_object = None

        # Names
        self.object_names = [
            "player",
            "button",
            "door",
            "grav-orb",
            "spike",
            "spike-inv",
            "juke-box",
            "main-menu",
            "walking-enemy",
        ]

        # Input keys
        self.kkeys = {
            # Keyboard
            "save": (22,),
            "load": (15,),
            "modeup": (16,),
            "modedown": (17,),
            "next": (8,),
            "prev": (20,),
            "f1": (58,),
            "tab": (43,),
            "shift": (225,),
            "control": (224,),
            "delete": (76,),
            "nextset": (27,),
            "prevset": (29,),
            "nextlayer": (25,),
            "prevlayer": (6,),
            "reload": (21,),
            "left": (4, 80),
            "right": (7, 79),
            "up": (26, 82),
            "down": (22, 81),
        }

        self.mkeys = {"place": (1,), "remove": (3,)}

        # input vars
        self.kkey = {
            # Keyboard
            "save": False,
            "load": False,
            "modeup": False,
            "modedown": False,
            "next": False,
            "prev": False,
            "f1": False,
            "tab": False,
            "shift": False,
            "control": False,
            "Hcontrol": False,
            "Hshift": False,
            "delete": False,
            "nextset": False,
            "prevset": False,
            "nextlayer": False,
            "prevlayer": False,
            "reload": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        self.mkey = {
            "place": False,
            "Hplace": False,
            "remove": False,
            "Hremove": False,
        }

    def update(self, paused: bool):
        """Update cursor pos and level changes."""
        if paused:
            pass
        else:
            # Get inputs
            self._get_inputs()

            # Change modes
            if self.kkey["modeup"] or self.kkey["modedown"]:
                self.mode += self.kkey["modeup"] - self.kkey["modedown"]
                self.pos = self.pos.grid(FULLTILE)
            self.mode = f_loop(self.mode, 0, 2)

            # Reload # NOTE # use before saving level in order to shrink grids
            if self.kkey["reload"] and self.kkey["Hcontrol"]:
                self.engine.col.st.minimize()
                for layer in self.engine.tile.layers:
                    layer = self.engine.tile.layers[layer]
                    layer.minimize()

            # Saving and loading
            if (
                self.kkey["save"]
                and self.kkey["Hcontrol"]
                and not self.mkey["Hplace"]
            ):
                self.engine.lvl.save()
                return
            elif (
                self.kkey["load"]
                and self.kkey["Hcontrol"]
                and not self.mkey["Hplace"]
            ):
                self.engine.lvl.load()
                self.engine.tile.add_all()
                return

            # State machine
            if self.mode == 0:  # Object mode
                self.object_mode()
            elif self.mode == 1:  # Tile mode
                self.tile_mode()
            elif self.mode == 2:  # Wall mode
                self.wall_mode()

            # Move camera
            hspd = (self.kkey["right"] - self.kkey["left"]) * FULLTILE
            vspd = (self.kkey["down"] - self.kkey["up"]) * FULLTILE

            if self.engine.inp.ms.get_button_held(2):
                self.rel += self.engine.inp.ms.get_delta()
                dx = abs(self.rel.x) // FULLTILE * sign(self.rel.x) * FULLTILE
                dy = abs(self.rel.y) // FULLTILE * sign(self.rel.y) * FULLTILE
                if dx != 0:
                    hspd -= dx
                    self.rel -= vec2d(dx, 0)
                if dy != 0:
                    vspd -= dy
                    self.rel -= vec2d(0, dy)
            else:
                self.rel = vec2d(0, 0)

            cam = self.engine.cam
            cam.pos = cam.pos + vec2d(hspd, vspd)

    def draw(self, draw: Draw):
        """Draw cursor and debug text."""
        # color = (224, 128, 224)

        element = self.engine.debug.menu.get("curpos")
        element.text = f"pos: {self.pos.ftup()}"

        if self.mode == 0:
            # Object name
            element = self.engine.debug.menu.get("mode")
            text = self.object_names[self.obj_select]
            element.text = f"Object: {text}"

        elif self.mode == 1:
            # Tile image
            surface = self._get_current_tile()
            pos = self.pos
            self.engine.draw.add(4, pos=pos, surface=surface)

            # Layer name
            element = self.engine.debug.menu.get("mode")
            text = self._get_current_layer().name
            element.text = f"Layer: {text}"

        elif self.mode == 2:
            # Wall
            element = self.engine.debug.menu.get("mode")
            element.text = "Wall mode"

    def _get_inputs(self):
        """Register inputs and change variables."""
        for key in self.kkey:
            if key[0] != "H":
                self.kkey[key] = self.engine.inp.kb.get_key_pressed(
                    *self.kkeys[key]
                )
            else:
                self.kkey[key] = self.engine.inp.kb.get_key_held(
                    *self.kkeys[key[1:]]
                )

        for key in self.mkey:
            if key[0] != "H":
                self.mkey[key] = self.engine.inp.ms.get_button_pressed(
                    *self.mkeys[key]
                )
            else:
                self.mkey[key] = self.engine.inp.ms.get_button_held(
                    *self.mkeys[key[1:]]
                )

    # Object
    def object_mode(self):
        """Object mode."""
        # Changing selection
        dobj = self.kkey["next"] - self.kkey["prev"]
        if dobj != 0:
            self.obj_select += dobj
            length = len(self.object_names) - 1
            self.obj_select = f_loop(self.obj_select, 0, length)

        # Toggling objects
        if self.kkey["f1"]:
            self.engine.obj.toggle_visibility()

        # View/Edit data
        if self.kkey["tab"] and self.selected_object != None:
            self._view_object_data()

        # Deselect object
        if self.mkey["place"]:
            self.selected_object = None

        # Place object
        if self.mkey["Hplace"] and self.kkey["Hcontrol"]:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey["place"]:
                self.pos = pos
                self._place_object()
        # Select and move object
        elif self.mkey["Hplace"]:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey["place"]:
                self.pos = pos
                obj = self.selected_object
                if obj is not None:
                    if obj.pos != pos:
                        obj.pos = pos
                    self.selected_object = obj
                self.selected_object = self._get_overlaping_object()

        # Remove object
        elif self.mkey["Hremove"] and self.kkey["Hcontrol"]:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey["remove"]:
                self.pos = pos
                self._remove_object()

    def _place_object(self):
        """Places object under cursor."""
        self._remove_object()
        name = self.object_names[self.obj_select]
        self.engine.obj.create_object(
            name=name, game=self.engine, key=None, pos=self.pos, data={}
        )

    def _remove_object(self):
        """Removes object under cursor."""
        obj = self._get_overlaping_object()
        while obj is not None:
            self.engine.obj.delete(obj.key)
            obj = self._get_overlaping_object()

    def _view_object_data(self):
        """Print object data or edit it if shift is held."""
        obj = self.selected_object
        if self.kkey["Hshift"]:
            text = ""
            while True:
                text = input("Edit data? ")
                try:
                    text = literal_eval(text)
                except (SyntaxError, ValueError):
                    if text == "exit":
                        break
                    print("input must be list")
                    continue
                if text == "exit":
                    break
                if not isinstance(text, dict):
                    print("input must be dictionary")
                else:
                    break
            if text != "exit":
                obj.data = text
                print("data succesfully written.")

        else:
            info = [f"name: {obj.name}", f"id: {obj.key}", f"data: {obj.data}"]
            print("\n".join(info))

    def _get_overlaping_object(self) -> Optional[Object]:
        """Find if object is under cursor."""
        for key in self.engine.obj.obj:
            obj = self.engine.obj.obj[key]
            if obj.pos == self.pos and obj.name != self.name:
                return obj
        return None

    # Tile
    def tile_mode(self):
        """Tile mode."""
        # Layer selection
        self.layer += self.kkey["nextlayer"] - self.kkey["prevlayer"]
        length = len(self.engine.tile.layers) - 1

        # Layer creation
        if self.layer > length or self.layer < 0:
            if self.kkey["Hshift"] and self.kkey["Hcontrol"]:
                name = self._get_data(
                    "Enter layer name: ", "Name must be string", "", str
                )
                depth = self._get_data(
                    "Enter layer depth: ",
                    "Depth must be an int",
                    "Layer Successfully Created!",
                    int,
                )
                if name is not None and depth is not None:
                    self.engine.tile.add_layer(
                        name, vec2d(6, 6), {"depth": depth}
                    )
                    self.engine.tile.layers[name].cache()
                    length += 1
                else:
                    self.layer -= 1

        # Layer deletion
        if self.kkey["delete"] and length > 0:
            if self.kkey["Hshift"] and self.kkey["Hcontrol"]:
                layer = self._get_current_layer()
                self.engine.tile.remove_layer(layer.name)
                length -= 1

        self.layer = f_loop(self.layer, 0, length)

        # Tilemap selection
        dset = self.kkey["nextset"] - self.kkey["prevset"]
        if dset != 0:
            self.tile_select = 0
            self.tilemap_select += dset
            length = len(self.engine.tile.tilemaps_list) - 1

            self.tilemap_select = f_loop(self.tilemap_select, 0, length)
            self.tilemap_id = self.engine.tile.tilemaps_list[
                self.tilemap_select
            ]
            self.tilemap = self._get_current_tilemap()

        # Changing selection
        dtile = self.kkey["next"] - self.kkey["prev"]
        if dtile != 0:
            self.tile_select += dtile
            length = len(self.tilemap) - 1
            self.tile_select = f_loop(self.tile_select, 0, length)

        # Toggling tile maps
        if self.kkey["f1"]:
            layer = list(self.engine.tile.layers.keys())[self.layer]
            self.engine.tile.layers[layer].toggle_visibility()

        # View/Edit data
        if self.kkey["tab"]:
            layer = self._get_current_layer()
            if self.kkey["Hshift"]:
                text = self._get_data(
                    "Enter data dict: ",
                    "Input must be of type dict",
                    "Data Successfully Written",
                    dict,
                )
                if text is not None:
                    layer.data = text
                    layer.update()
            else:
                print(f"name: {layer.name}")
                print(f"size: {layer.size}")
                print(f"data: {layer.data}")

        # Mouse
        # Place tile
        if self.mkey["Hplace"] and self.kkey["Hcontrol"]:
            # Update position
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE // 2)
            if self.pos != pos or self.mkey["place"]:
                self.pos = pos
                self._place_tile()

        # Remove tile
        elif self.mkey["Hremove"] and self.kkey["Hcontrol"]:
            # Update position
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE // 2)
            if self.pos != pos or self.mkey["remove"]:
                self.pos = pos
                self._remove_tile()

    def _place_tile(self):
        """Places tile under cursor."""
        layer = self._get_current_layer()
        tile_map = self.tilemap_id
        layer.place(self.pos, tile_map, self.tile_select)
        layer.cache_partial(self.pos)

    def _remove_tile(self):
        """Removes tile under cursor."""
        layer = self._get_current_layer()
        layer.remove(self.pos)
        layer.cache_partial(self.pos)

    def _get_current_layer(self) -> TileLayer:
        return self.engine.tile.layers[
            list(self.engine.tile.layers.keys())[self.layer]
        ]

    def _get_current_tilemap(self) -> list:
        return self.engine.tile.tilemaps[self.tilemap_id]

    def _get_current_tile(self) -> Surface:
        return self.tilemap[self.tile_select]

    # Wall
    def wall_mode(self):
        # Wall mode
        if self.kkey["f1"]:
            self.engine.col.st.toggle_visibility()

        # Place wall
        if self.mkey["Hplace"]:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey["place"]:
                self.pos = pos
                self.engine.col.st.add(pos)

        # Remove wall
        elif self.mkey["Hremove"]:
            pos = self.engine.inp.ms.get_pos() + self.engine.cam.pos
            pos = pos.grid(FULLTILE)
            if pos != self.pos or self.mkey["remove"]:
                self.pos = pos
                self.engine.col.st.remove(pos)

    # Info query
    def _get_data(self, prompt: str, error: str, success: str, datatype: type):
        text = ""
        while True:
            text = input(prompt)
            try:
                text = literal_eval(text)
            except (SyntaxError, ValueError):
                if text == "exit":
                    break
                print(error)
                continue
            if text == "exit":
                break
            if not isinstance(text, datatype):
                print(error)
            else:
                break
        if text != "exit":
            print(success)
            return text
        return None
