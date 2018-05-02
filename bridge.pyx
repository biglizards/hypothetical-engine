import sys

cdef public int add(int a, int b):
    print(sys.version)
    return a+b