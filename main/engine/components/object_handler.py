# Handles object instances
class ObjObjectHandler():
    """Handles game objects."""
    def __init__(self, game, object_creator, max_objects=2**14-1):
        self.game = game
        self.object_creator = object_creator
        self.pool_size = max_objects
        self.pool = set()
        for item in range(self.pool_size):
            self.pool.add(item)
        self.obj = {}
        self.visible = True

    # Update calls
    def update_early(self, dt, **kwargs):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            try:
                self.obj[key]
            except KeyError:
                print('key {} does not exist'.format(key))
            else:
                self.obj[key].update_early(dt, **kwargs)

    def update(self, dt, **kwargs):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            try:
                self.obj[key]
            except KeyError:
                print('key {} does not exist'.format(key))
            else:
                self.obj[key].update(dt, **kwargs)

    def update_late(self, dt, **kwargs):
        """Update all GameObjects."""
        objcopy = self.obj.copy()
        for key in objcopy:
            try:
                self.obj[key]
            except KeyError:
                print('key {} does not exist'.format(key))
            else:
                self.obj[key].update_late(dt, **kwargs)

    # Draw calls
    def draw_early(self, window):
        """Draw that occurs before the background."""
        if self.visible:
            for key in self.obj:
                self.obj[key].draw_early(window)

    def draw(self, window):
        """Draw that occurs between background and foreground."""
        if self.visible:
            for key in self.obj:
                self.obj[key].draw(window)

    def draw_late(self, window):
        """Draw that occurs after the foreground."""
        if self.visible:
            for key in self.obj:
                self.obj[key].draw_late(window)

    # Object creation
    def instantiate_key(self, key=None):
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

    def instantiate_object(self, key, obj):
        """Add a ref. to a game object in the self.obj dictionary."""
        self.obj[key] = obj

    def create_object(self, **kwargs):
        """Creates instances of objects and instantiates them."""
        self.object_creator(**kwargs)

    # Object deletion
    def delete(self, key):
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
