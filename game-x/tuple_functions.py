"""A series of functions built for tuples."""
# tuple functions
from math import floor, ceil

# mutiplies all of the vaules in tuple by another tuple or a singular value
def f_tupmult(tup: tuple, mult) -> tuple:
    """Returns a tuple multiplied term by term with another tuple or a scalar
        Ex. a
            n = (3, 4, 5), m = 2;
            n = list(n)
            n[0] * m:3 * 2 = 6
            n[1] * m:4 * 2 = 8
            n[2] * m:5 * 2 = 10
            return tup([6, 8, 10])
        Ex. b
            n = (1, -2), m = (2, 8); # NOTE both must be same length
            n = list(n)
            m = list(m)
            n[0] * m[0]:1 * 2 = 2
            n[1] * m[1]:-2 * 8 = -16
            return tup([2, -16])
    """
    tlist = list(tup)
    length = len(tlist)
    if isinstance(mult, (float, int)):
        for count in range(0, length):
            tlist[count] *= mult
    elif isinstance(mult, (tuple, list)):
        mult = list(mult)
        for count in range(0, length):
            tlist[count] *= mult[count]
    else:
        tlist = None
    return tuple(tlist)

# adds two tuples or a tuple and a scalar together
def f_tupadd(tup: tuple, add):
    """Sums a tuple with another tuple or scalar
        Ex. a
            n = (3, 4, 5), m = 2;
            n = list(n)
            n[0] * m:3 + 2 = 5
            n[1] * m:4 + 2 = 6
            n[2] * m:5 + 2 = 7
            return tup([5, 6, 7])
        Ex. b
            n = (1, -2), m = (2, 8); # NOTE both must be same length
            n = list(n)
            m = list(m)
            n[0] * m[0]:1 + 2 = 3
            n[1] * m[1]:-2 + 8 = 6
            return tup([3, 6])
    """
    tlist = list(tup)
    length = len(tlist)
    if isinstance(add, int):
        for count in range(0, length):
            tlist[count] += add
        return tuple(tlist)
    add = list(add)
    for count in range(0, length):
        tlist[count] += add[count]
    return tuple(tlist)

# aligns tuple to grid
def f_tupgrid(tup: tuple, cellsize):
    """Aligns a given value tuple to a grid with a certain cell size."""
    tup = f_tupmult(tup, 1 / cellsize)
    tup = f_tupround(tup, 'floor')
    return f_tupmult(tup, cellsize)

#
# takes all values in a tuple and roudns them up or down
def f_tupround(tup: tuple, func):
    """floor is -1 or 'floor'; ceil is 1 or 'ceil';
        Rounds every number in a tuple up or down to the nearest integer
        Ex. a
            val = (3.5, 4, 8.27), floorceil = 0
            val = list(val)
            val[0] = floor(val[0]) = 3
            val[1] = floor(val[1]) = 4
            val[2] = floor(val[2]) = 8
            return tup(val)
    """
    # convert to array and divide by div
    tlist = list(tup)
    count = len(tlist)

    if func in (-1, 'floor'):
        # floor all values
        for num in range(count):
            tlist[num] = floor(tlist[num])
    elif func == (1, 'ceil'):
        # ceil all values
        for num in range(count):
            tlist[num] = ceil(tlist[num])
    elif func in (0, 'round'):
        # round all values
        for num in range(count):
            tlist[num] = round(tlist[num])
    elif callable(func):
        for num in range(count):
            tlist[num] = func(tlist[num])
    else:
        raise ValueError
    return tuple(tlist)
