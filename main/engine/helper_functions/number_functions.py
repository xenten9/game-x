
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
    for row, _ in enumerate(grid):
        for column, old in enumerate(grid[row]):
            try:
                new_grid[row][column] = old
            except IndexError:
                pass
    return new_grid

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
