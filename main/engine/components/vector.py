from math import hypot, floor

class vec2d(tuple):
    def __new__(typ, x: float, y: float):
        n = tuple.__new__(typ, (x, y))
        n.x = x
        n.y = y
        return n

    def __add__(self, other):
        if isinstance(other, (tuple, list, vec2d)):
            x, y = other[0:2]
        elif isinstance(other, (float, int)):
            x, y = other, other
        return self.__new__(type(self), self.x + x, self.y + y)
    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (tuple, list, vec2d)):
            x, y = other[0:2]
        elif isinstance(other, (float, int)):
            x, y = other, other
        return self.__new__(type(self), self.x - x, self.y - y)
    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, (tuple, list, vec2d)):
            x, y = other[0:2]
        elif isinstance(other, (float, int)):
            x, y = other, other
        return self.__new__(type(self), self.x * x, self.y * y)
    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (tuple, list, vec2d)):
            x, y = other[0:2]
        elif isinstance(other, (float, int)):
            x, y = other, other
        return self.__new__(type(self), self.x / x, self.y / y)
    def __idiv__(self, other):
        return self.__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, (tuple, list, vec2d)):
            x, y = other[0:2]
        elif isinstance(other, (float, int)):
            x, y = other, other
        return self.__new__(type(self), self.x // x, self.y // y)
    def __ifloordiv__(self, other):
        return self.__floordiv__(other)

    def magnitude(self):
        return hypot(*self)

    def floor(self):
        return self.__new__(type(self), floor(self.x), floor(self.y))

    def grid(self, cell_size):
        x = (self.x // cell_size) * cell_size
        y = (self.y // cell_size) * cell_size
        return self.__new__(type(self), x, y)

    def __str__(self):
        return '<{}, {}>'.format(self.x, self.y)
