from copy import deepcopy

# Creates a grid
def f_make_grid(size, default_value):
    """Makes a grid populated with some default value."""
    grid = []
    for _ in range(size[0]):
        grid.append([default_value] * size[1])
    return grid

# Returns a grid with a new size preserving as many old values as possible
def f_change_grid_dimensions(grid, size, value):
    """Updates an existing grid to be a new size."""
    new_grid = f_make_grid(size, value)
    for column, _ in enumerate(grid):
        for row, old in enumerate(grid[column]):
            try:
                new_grid[column][row] = old
            except IndexError:
                pass
    return new_grid

# Returns a grid with no empty rows or columns
def f_minimize_grid(grid, nullval):
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

    return f_change_grid_dimensions(grid, (width, height), nullval)

def f_is_list_empty(inlist, nullval):
    for cell in inlist:
            if cell != nullval:
                return 0
    return 1

def f_get_column(grid, column):
    return grid[column]

def f_get_row(grid, row):
    out = []
    for column in grid:
        out.append(column[row])
    return out

# Return a value following packman logic
def f_loop(val, minval, maxval):
    """Returns a number that loops between the min and max
    Ex. n = 8, minval = 3, maxval = 5;
        8 is 3 more then 5
        minval + 3 = 6
        6 is 1 more then 5
        minval + 1 = 4
        minval < 4 < maxval
        return 4
    """
    if minval <= val <= maxval:
        return val
    if val <= minval:
        return maxval - (minval - val) + 1
    return minval + (val - maxval) - 1

# Return the value closest to the range min to max
def f_limit(val, minval, maxval):
    """Reutrns value n
    limits/clamps the value n between the min and max
    """
    if val < minval:
        return minval
    if val > maxval:
        return maxval
    return val
