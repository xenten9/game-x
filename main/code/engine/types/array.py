from typing import Union


from .vector import vec2d


def f_is_list_empty(list: list):
    for element in list:
        if element is not None:
            return False
    return True


class array2d:
    def __init__(self, size: tuple[int, int]):
        self._array = [[None] * size[1] for _ in range(size[0])]
        self._size = size

    def __str__(self):
        string = []
        string.append("[")
        for y in range(self.height):
            string.append("\t" + str(self.get_row(y)))
        string.append("]")
        return "\n".join(string)

    @property
    def array(self):
        return self._array

    @array.setter
    def array(self, array: list[list]):
        self._array = array
        self._size = (len(array), len(array[0]))

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @size.setter
    def size(self, size: tuple[int, int]):
        new = array2d(size)
        for x in range(min(self.size[0], size[0])):
            for y in range(min(self.size[1], size[1])):
                new.set(x, y, self.get(x, y))
        self._array = new._array
        self._size = size

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def minimize(self):
        width, height = self.size
        for x in range(1, self.size[0]):
            column = self.get_column(width - x)
            if not f_is_list_empty(column):
                width = self.width - x + 1
                break
        for y in range(1, self.size[1]):
            row = self.get_row(height - y)
            if not f_is_list_empty(row):
                height = self.height - y + 1
                break

        self.size = (width, height)

    def get(self, x: int, y: int):
        if self._bounded((x, y)):
            return self._array[x][y]
        raise IndexError(f"no point ({x}, {y})")

    def set(self, x: int, y: int, value):
        if not self._bounded((x, y)):
            self.size = (max(x + 1, self.size[0]), max(y + 1, self.size[1]))
        self._array[x][y] = value

    def delete(self, x: int, y: int):
        if self._bounded((x, y)):
            self._array[x][y] = None

    def get_column(self, x: int):
        if self._bounded((x, 0)):
            return self._array[x]
        raise IndexError(f"no column {x}")

    def get_row(self, y: int):
        if self._bounded((0, y)):
            return [column[y] for column in self._array]
        raise IndexError(f"no row {y}")

    def fill(self, value):
        self._array = [[value] * self.height for _ in range(self.width)]

    def _bounded(self, point: Union[vec2d, tuple]):
        if point[0] + 1 <= self.size[0] and point[1] + 1 <= self.size[1]:
            return True
        return False
