cdef class Model:
    cdef unsigned int VAO, VBO

    cdef buffer_packed_data(self, data_p, int length, data_format=?)
    cpdef void bind(self)