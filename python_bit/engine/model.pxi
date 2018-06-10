"""
a model has
 - vertex (and texture) co-ords
 - texture image data stuff
 - a hitbox maybe?
  but REALLY all it has is
 - a VAO (with bound VBO)
"""

from cpython cimport array

cdef extern from *:
    void glGenVertexArrays(int, unsigned int*)
    void glGenBuffers(int count, unsigned int* buffer_array)
    void glBindVertexArray(unsigned int)
    void glBindBuffer(unsigned int, unsigned int)
    unsigned int GL_ARRAY_BUFFER
    unsigned int GL_STATIC_DRAW
    unsigned int GL_FLOAT

    void glBufferData(unsigned int target, ptrdiff_t size, const void*, unsigned int)
    void glVertexAttribPointer(unsigned int index, int size, unsigned int type,
                               unsigned char normalized, int stride, const void* pointer)
    void glEnableVertexAttribArray(unsigned int)

cdef class Model:
    cdef unsigned int VAO, VBO

    def __cinit__(self, *args, **kwargs):
        self.VAO = 0
        self.VBO = 0

    cdef buffer_packed_data(self, data_p, int length, data_format=None):
        """
        packed data is in the format specified in data_format
        where the meta-format is (width1, width2, ...)
        eg, for a data format of (3, 1, 2) the data would look like
        [a, a, a, b, c, c
         a, a, a, b, c, c, 
         ...
         ]
        """
        # convert python list to array.array
        cdef array.array data = array.array('f', data_p)
        if data_format is None:
            data_format = (3, 2)

        cdef int total_width = sum(data_format)

        # create and bind array/buffer objects
        glGenVertexArrays(1, &self.VAO)
        glGenBuffers(1, &self.VBO)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        # buffer data, add format info
        glBufferData(GL_ARRAY_BUFFER, sizeof(float)*length, data.data.as_floats, GL_STATIC_DRAW)
        cdef int i, width, offset = 0
        for i, width in enumerate(data_format):
            glVertexAttribPointer(i, width, GL_FLOAT, 0, total_width*sizeof(float), <void*>(offset * sizeof(float)))
            glEnableVertexAttribArray(i)
            offset += width

    cpdef void bind(self):
        glBindVertexArray(self.VAO)