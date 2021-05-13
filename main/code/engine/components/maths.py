"""Useful mathematical functions"""

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
