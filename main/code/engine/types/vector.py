from __future__ import annotations
from math import hypot, floor


class vec2d:
    # Magic methods
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # def __new__(cls, x, y):
    #    return cls(x, y)

    def __len__(self):
        return 2

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        else:
            raise StopIteration()

    def __str__(self) -> str:
        return f"<{self.x}, {self.y}>"

    def __add__(self, other) -> vec2d:
        other = self.parse(other)
        return vec2d(self.x + other.x, self.y + other.y)

    def __iadd__(self, other) -> vec2d:
        return self.__add__(other)

    def __sub__(self, other) -> vec2d:
        other = self.parse(other)
        return vec2d(self.x - other.x, self.y - other.y)

    def __isub__(self, other) -> vec2d:
        return self.__sub__(other)

    def __mul__(self, other) -> vec2d:
        other = self.parse(other)
        return vec2d(self.x * other.x, self.y * other.y)

    def __imul__(self, other) -> vec2d:
        return self.__mul__(other)

    def __rmul__(self, other) -> vec2d:
        return self.__mul__(other)

    def __truediv__(self, other) -> vec2d:
        other = self.parse(other)
        return vec2d(self.x / other.x, self.y / other.y)

    def __idiv__(self, other) -> vec2d:
        return self.__truediv__(other)

    def __floordiv__(self, other) -> vec2d:
        other = self.parse(other)
        return vec2d(self.x // other.x, self.y // other.y)

    def __ifloordiv__(self, other) -> vec2d:
        return self.__floordiv__(other)

    def parse(self, other) -> vec2d:
        if isinstance(other, vec2d):
            return other
        elif isinstance(other, (int, float)):
            return vec2d(other, other)
        else:
            raise TypeError(f"type: {type(other)} not supported by vec2d")

    # Propertiess
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def grid(self, cell_size) -> vec2d:
        x = (self.x // cell_size) * cell_size
        y = (self.y // cell_size) * cell_size
        return vec2d(x, y)

    def floor(self) -> vec2d:
        return vec2d(floor(self.x), floor(self.y))

    def tup(self) -> tuple[float, float]:
        return (self.x, self.y)

    def ftup(self) -> tuple[int, int]:
        return (floor(self.x), floor(self.y))

    # Vector methods
    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def normalize(self, mag: float = None):
        if mag is None:
            mag = self.magnitude()
        return self / mag
