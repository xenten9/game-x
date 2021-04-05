"""Objects used for event handling related to inputs of a keyboard or mouse."""
# keyboard inputs
class ObjKeyboard():
    """Record all of the keyoard inputs whether pressed or held."""
    def __init__(self):
        # define dictionarys for keyboard lookup and storage
        self.key_held = {}
        self.key_pressed = {}

    def get_key_held(self, *keys) -> bool:
        """Returns bool for a series of keys if any are being held."""
        for k in keys:
            try:
                if self.key_held[k] == 1:
                    return 1
            except KeyError:
                #print(str(k) + " key has not been pressed yet")
                pass
        return 0

    def get_key_pressed(self, *keys):
        """Returns bool for if a key just got pressed."""
        for k in keys:
            try:
                if self.key_pressed[k] == 1:
                    return 1
            except KeyError:
                #print(str(k) + " key has not been pressed yet")
                pass
        return 0

    def set_key(self, key, value):
        """Used to set a key within key_pressed and key_held."""
        self.key_held[key] = value
        self.key_pressed[key] = value

    def reset(self):
        """Resets the key_pressed dictionary
        so that the inputs only last for the loop where in they were recorded"""
        self.key_pressed = {}

# mouse inputs
class ObjMouse():
    """Used to get mouse inputs and movement."""
    def __init__(self):
        self.button_pressed = {}
        self.button_pressed_pos = {}
        self.button_held = {}
        self.pos = (0, 0)
        self.rel = (0, 0)

    def get_pos(self):
        """Returns the current mouse position."""
        return self.pos

    def get_delta(self):
        """Returns the mouse position relative to last cycle."""
        return self.rel

    def get_button_pressed(self, button):
        """Returns whether or not a mouse button was just pressed."""
        try:
            return self.button_pressed[button]
        except KeyError:
            return 0

    def get_button_presssed_pos(self, button) -> tuple:
        """Returns the position of where a mouse clicked with a button."""
        try:
            return self.button_pressed_pos[button]
        except KeyError:
            return 0

    def get_button_held(self, button):
        """Returns whether or not a mouse button is currently being held."""
        try:
            return self.button_held[button]
        except KeyError:
            return 0

    def reset(self):
        """Resets the button_pressed and button_pressed_pos dictionary
        so that the inputs only last for the loop where in they were recorded"""
        self.button_pressed = {}
        self.button_pressed_pos = {}
        self.rel = (0, 0)
