from typing import Any, List, Union
from ..types.vector import vec2d

# Creates a grid
def f_make_grid(size, nullval: Any) -> List[List]:
    """Makes a grid populated with some default value."""
    grid = []
    for _ in range(size[0]):
        grid.append([nullval] * size[1])
    return grid

# Returns a grid with a new size preserving as many old values as possible
def f_change_grid_dimensions(grid: List[List],
                             size: vec2d,
                             nullval: Any) -> List[List]:
    """Updates an existing grid to be a new size."""
    new_grid = f_make_grid(size, nullval)
    for column, _ in enumerate(grid):
        for row, old in enumerate(grid[column]):
            try:
                new_grid[column][row] = old
            except IndexError:
                pass
    return new_grid

# Returns a grid with no empty rows or columns
def f_minimize_grid(grid: List[List], nullval: Any):
    """Remove empty rows and columns."""
    if len(grid) == 0:
        return []
    width, height = len(grid), len(grid[0])
    for n in range(1, width):
        column = f_get_column(grid, width-n)
        if not f_is_list_empty(column, nullval):
            width -= n - 1
            break

    for n in range(1, height):
        row = f_get_row(grid ,height-n)
        if not f_is_list_empty(row, nullval):
            height -= n - 1
            break

    return f_change_grid_dimensions(grid, vec2d(width, height), nullval)

def f_is_list_empty(inlist: List, nullval: Any):
    """Checks if a list is made entirely of nullval."""
    for cell in inlist:
            if cell != nullval:
                return 0
    return 1

def f_get_column(grid: List[List], column: int):
    """Returns a column from a 2d grid."""
    return grid[column]

def f_get_row(grid: List[List], row: int):
    """Returns a row from a 2d grid."""
    out = []
    for column in grid:
        out.append(column[row])
    return out

# Return a value following packman logic
def f_loop(value, minval, maxval):
    """Returns a number that loops between the min and max."""
    if minval <= value <= maxval:
        return value
    while value <= minval:
        value = maxval - (minval - value) + 1
    while value >= maxval:
        value = minval + (value - maxval) - 1
    return value

# Return the value closest to the range min to max
def f_limit(value, minval, maxval):
    """Limits/clamps the value n between the min and max."""
    if value < minval:
        return minval
    if value > maxval:
        return maxval
    return value
