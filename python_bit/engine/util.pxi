from libc.stdlib cimport malloc, free
from libc.string cimport strcpy, strlen
from cpython.string cimport PyString_AsString

cdef bytes to_bytes(some_string):
    if isinstance(some_string, bytes):
        return some_string
    if isinstance(some_string, unicode):
        return some_string.encode()
    if isinstance(some_string, (int, float)):
        return str(some_string).encode()  # why would you do that though
    else:
        raise TypeError("Could not convert to bytes")

cdef list to_list(int length, const char** str_array):
    cdef int i
    python_list = []
    for i in range(length):
        python_list.append(str_array[i].decode())
    return python_list

cdef const char** to_c_array(in_list):
    """
    given a python list of strings/bytes, returns a char**
    this seems very unstable or memory leaky, i should fix that
    """
    cdef char** c_array = <char**>malloc(len(in_list) * sizeof(char*))
    for i, value in enumerate(in_list):
        in_list[i] = to_bytes(value)
        c_array[i] = in_list[i]
    return <const char**>c_array
