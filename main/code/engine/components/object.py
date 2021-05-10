"""Handles object instances"""
import sys
from typing import Callable
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
        self.obj = {}
        self.visible = True

    # Update calls
    def update_early(self):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].update_early(self.engine.paused)

    def update(self):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].update(self.engine.paused)

    def update_late(self):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            if key in self.obj:
                self.obj[key].update_late(self.engine.paused)

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
        self.obj[key] = obj

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
