cimport very_cool_maths

cdef public int cool_add(int a, int b):
    return very_cool_maths.very_cool_add(a, b)

cdef public int semi_cool_add(int a, int b):
    return a+b+2  # the 2 makes it just a little cool