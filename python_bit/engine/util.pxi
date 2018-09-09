cdef bytes to_bytes(some_string):
    if isinstance(some_string, bytes):
        return some_string
    if isinstance(some_string, unicode):
        return some_string.encode()
    else:
        raise TypeError("Could not convert to bytes")
