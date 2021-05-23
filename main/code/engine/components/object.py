"""Handles object instances."""
# Standard library
from typing import Callable, Any

# Local imports
from ..constants import colorize
from ..types.entity import Entity
from ..types.component import Component

class ObjectHandler(Component):
    """Handles game objects."""
    def __init__(self, engine: object, object_creator: Callable, max_objects: int = 2**14-1):
        super().__init__(engine)
        self.object_creator = object_creator
        self.pool_size = max_objects
        self.pool = set()
        for item in range(self.pool_size):
            self.pool.add(item)
        self.obj: dict[int, Any] = {}
        self.sobj: dict[str, Any] = {}
        self.visible = True

    # Update calls
    def update_early(self):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].update_early(self.engine.paused)
        for key in self.sobj:
            self.sobj[key].update_early(self.engine.paused)

    def update(self):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].update(self.engine.paused)
        sobjcopy = self.sobj.copy()
        for key in sobjcopy:
            self.sobj[key].update(self.engine.paused)

    def update_late(self):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].update_late(self.engine.paused)
        for key in self.sobj:
            self.sobj[key].update_late(self.engine.paused)

    # Object creation
    def instantiate_key(self, key: int = None):
        """Add a ref. to a game object in the self.obj dictionary."""
        if key is None:
            newkey = self.pool.pop()
            return newkey
        else:
            if key in self.pool:
                self.pool.remove(key)
                return key
            else:
                print('key {} is not in pool!'.format(key))
                newkey = self.pool.pop()
                print('supplementing key {} with {}!'.format(key, newkey))
                return newkey

    def instantiate_object(self, key: int, obj: object):
        """Add a ref. to a game object in the self.obj dictionary."""
        if issubclass(obj.__class__, Entity):
            self.obj[key] = obj
        else:
            message = 'Object {} cannot be instantied'.format(obj)
            message += 'It does not sublass to Entity'
            raise TypeError(colorize(message, 'red'))

    def create_object(self, **kwargs):
        """Creates instances of objects and instantiates them."""
        self.object_creator(self.engine, **kwargs)

    def post_init(self):
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].post_init()

    # Object deletion
    def delete(self, key: int):
        """Removes a ref. of a game object from the self.obj dictionary."""
        try:
            self.obj[key].delete()
        except AttributeError:
            pass
        del self.obj[key]
        self.pool.add(key)

    def toggle_visibility(self):
        """Stop rendering for all objects."""
        self.visible = not self.visible

    def clear(self):
        """Clear all GameObjects."""
        objcopy = self.obj.copy()
        for obj in objcopy:
            self.delete(obj)
