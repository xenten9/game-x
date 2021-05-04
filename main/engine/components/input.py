from typing import Union
from pygame.constants import (KEYDOWN, KEYUP, MOUSEMOTION,
                              MOUSEBUTTONUP, MOUSEBUTTONDOWN)
from pygame.event import Event
from ..types.component import Component
from ..types.vector import vec2d


class Input(Component):
    def __init__(self, engine: object):
        super().__init__(engine)
        self.kb = Keyboard()
        self.ms = Mouse()

    def handle_events(self, event: Event):
        """Handles inputs and events."""
        # Key pressed
        if event.type == KEYDOWN:
            self.kb.set_key(event.scancode, True)

        # Key released
        elif event.type == KEYUP:
            self.kb.set_key(event.scancode, False)

        # Mouse movement
        elif event.type == MOUSEMOTION:
            self.ms.pos = vec2d(*event.pos)
            self.ms.rel = self.ms.rel + vec2d(*event.rel)

        # Mouse pressed
        elif event.type == MOUSEBUTTONDOWN:
            self.ms.button_pressed[event.button] = 1
            self.ms.button_held[event.button] = 1
            self.ms.button_pressed_pos[event.button] = vec2d(*event.pos)

        # Mouse released
        elif event.type == MOUSEBUTTONUP:
            self.ms.button_pressed[event.button] = 0
            self.ms.button_held[event.button] = 0

        # Music end
        elif event.type == 56709:
            self.engine.aud.music.end()

    def reset(self):
        """Resets keyboard and mouse."""
        self.kb.reset()
        self.ms.reset()

# keyboard inputs
class Keyboard():
    """Record all of the keyoard inputs whether pressed or held."""
    def __init__(self):
        # define dictionarys for keyboard lookup and storage
        self.key_held = {}
        self.key_pressed = {}

    def get_key_held(self, *keys) -> bool:
        """Returns bool for a series of keys if any are being held."""
        for k in keys:
            try:
                if self.key_held[k]:
                    return True
            except KeyError:
                pass
        return False

    def get_key_pressed(self, *keys) -> bool:
        """Returns bool for if a key just got pressed."""
        for k in keys:
            try:
                if self.key_pressed[k]:
                    return True
            except KeyError:
                pass
        return False

    def get_key_combo(self, kpress, *kheld) -> bool:
        """Returns bool for a series of keys if any are being held."""
        if self.get_key_pressed(kpress):
            held = []
            for k in kheld:
                held.append(self.get_key_held(k))
            if min(held) == 1:
                return True
        return False

    def set_key(self, key: int, value: bool):
        """Used to set a key within key_pressed and key_held."""
        self.key_held[key] = value
        self.key_pressed[key] = value

    def reset(self):
        """Resets inputs."""
        self.key_pressed = {}

# mouse inputs
class Mouse():
    """Used to get mouse inputs and movement."""
    def __init__(self):
        self.button_pressed = {}
        self.button_pressed_pos = {}
        self.button_held = {}
        self.pos = vec2d(0, 0)
        self.rel = vec2d(0, 0)

    def get_pos(self) -> vec2d:
        """Returns the current mouse position."""
        return self.pos

    def get_delta(self) -> vec2d:
        """Returns the mouse position relative to last cycle."""
        return self.rel

    def get_button_pressed_pos(self, button) -> Union[vec2d, None]:
        """Returns the position of where a mouse clicked with a button."""
        try:
            return self.button_pressed_pos[button]
        except KeyError:
            return None

    def get_button_pressed(self, *button) -> bool:
        """Returns whether or not a mouse button was just pressed."""
        for b in button:
            try:
                if self.button_pressed[b]:
                    return True
            except KeyError:
                pass
        return False

    def get_button_held(self, *button) -> bool:
        """Returns whether or not a mouse button is currently being held."""
        for b in button:
            try:
                if self.button_held[b]:
                    return True
            except KeyError:
                pass
        return False

    def reset(self):
        """Resets inputs."""
        self.button_pressed = {}
        self.button_pressed_pos = {}
        self.rel = vec2d(0, 0)
