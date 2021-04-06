"""A set of functions for collisions between pixels ranges and rectangles."""

# collision functions
# pixel in range
def f_col_pixran(pix, ran):
    """ran[0] < ran[1]"""
    if ran[0] <= pix <= ran[1] or pix in ran:
        return 1
    return 0

# pixel in rect
def f_col_pixrect(pos, dom, ran):
    """dom[0] < dom[1], ran[0] < ran[1]"""
    if f_col_pixran(pos[0], dom) and f_col_pixran(pos[1], ran):
        return 1
    return 0

# range overlap
def f_col_ranges(ran0, ran1):
    """ran0[0] < ran0[1], ran1[0] < ran1[1]"""
    if f_col_pixran(ran0[0], ran1):
        return 1
    if f_col_pixran(ran0[1], ran1):
        return 1
    if f_col_pixran(ran1[0], ran0):
        return 1
    if f_col_pixran(ran1[1], ran0):
        return 1
    return 0

# rectangle overlap
def f_col_rects(dom0, ran0, dom1, ran1):
    """dom0[0] < dom0[1], ran0[0] < ran0[1];
    dom1[0] < dom1[1], ran1[0] < ran1[1];"""
    if f_col_ranges(dom0, dom1) and f_col_ranges(ran0, ran1):
        return 1
    return 0
