from __future__ import annotations
from math import hypot, floor
from typing import Tuple, Union

class vec2d(tuple):
    def __new__(cls, x, y) -> vec2d:
        n = tuple.__new__(cls, (x, y))
        n.x = x
        n.y = y
        return n

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

    def parse(self, variable):
        if isinstance(variable, (tuple, list, vec2d)):
            return iter(variable[0:2])
        elif isinstance(variable, (float, int)):
            return iter((variable, variable))
        else:
            raise Exception('variable not parsable')

    def __add__(self, other) -> vec2d:
        x, y = self.parse(other)
        return self.__new__(type(self), self.x + x, self.y + y)
    def __iadd__(self, other) -> vec2d:
        return self.__add__(other)

    def __sub__(self, other) -> vec2d:
        x, y = self.parse(other)
        return self.__new__(type(self), self.x - x, self.y - y)
    def __isub__(self, other) -> vec2d:
        return self.__sub__(other)

    def __mul__(self, other) -> vec2d:
        x, y = self.parse(other)
        return self.__new__(type(self), self.x * x, self.y * y)
    def __imul__(self, other) -> vec2d:
        return self.__mul__(other)
    def __rmul__(self, other) -> vec2d:
        return self.__mul__(other)

    def __truediv__(self, other) -> vec2d:
        x, y = self.parse(other)
        return self.__new__(type(self), self.x / x, self.y / y)
    def __idiv__(self, other) -> vec2d:
        return self.__truediv__(other)

    def __floordiv__(self, other) -> vec2d:
        x, y = self.parse(other)
        return self.__new__(type(self), self.x // x, self.y // y)
    def __ifloordiv__(self, other) -> vec2d:
        return self.__floordiv__(other)

    def magnitude(self) -> float:
        return hypot(*self)

    def grid(self, cell_size) -> vec2d:
        x = (self.x // cell_size) * cell_size
        y = (self.y // cell_size) * cell_size
        return self.__new__(type(self), x, y)

    def floor(self) -> vec2d:
        return self.__new__(type(self), floor(self.x), floor(self.y))

    def tup(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def ftup(self):
        return (floor(self.x), floor(self.y))

    def __str__(self) -> str:
        return '<{}, {}>'.format(self.x, self.y)

    def normalize(self, mag: float = None):
        if mag is None:
            mag = self.magnitude()
        return self / mag
