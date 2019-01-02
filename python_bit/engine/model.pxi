from cpython cimport array

cdef class Mesh:
    """
    a mesh has
     - vertex (and texture) co-ords
     - texture image data stuff (like where the texture is meant to be; part of the vertex data)
     - a hitbox maybe?
      but REALLY all it has is
     - a VAO (with bound VBO)
    """
    cdef unsigned int VAO, VBO, EBO

    def __cinit__(self, *args, **kwargs):
        self.VAO = 0
        self.VBO = 0
        self.EBO = 0

    cdef buffer_packed_data(self, data_p, data_format, indices=None):
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
        cdef array.array index_array
        cdef int length = len(data)
        cdef int total_width = sum(data_format)

        # create and bind array/buffer objects
        glGenVertexArrays(1, &self.VAO)
        glGenBuffers(1, &self.VBO)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        # buffer data
        glBufferData(target=GL_ARRAY_BUFFER, size=sizeof(float)*length,
                     data=data.data.as_floats, usage=GL_STATIC_DRAW)

        # add format info
        cdef int i, width, offset = 0
        for i, width in enumerate(data_format):
            glVertexAttribPointer(index=i, size=width, type=GL_FLOAT, normalized=0,
                                  stride=total_width*sizeof(float), pointer=<void*>(offset * sizeof(float)))
            glEnableVertexAttribArray(i)
            offset += width

        if indices:
            index_array = array.array('i', indices)
            glGenBuffers(1, &self.EBO)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices)*sizeof(int),
                         index_array.data.as_ints, GL_STATIC_DRAW)

    cpdef void bind(self):
        glBindVertexArray(self.VAO)

cdef class Drawable:
    """
    A drawable thing has
     - a shader program
     - a model (which consists of multiple meshes?)
     - textures
    This was originally meant to be a base class for stuff which could be drawn,
    but it became generic enough that i don't even need subclasses.
    I guess stuff can still extend it though, if they want.
    """
    cdef Mesh mesh
    cdef public ShaderProgram shader_program
    cdef int no_of_indices
    cdef bint indexed

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, data, indices, data_format, vert_path, frag_path, geo_path=None):
        if indices is None:
            self.indexed = False
            self.no_of_indices = len(data) / sum(data_format)
        else:
            self.indexed = True
            self.no_of_indices = len(indices)

        self.mesh = Mesh()
        self.shader_program = ShaderProgram(vert_path, frag_path, geo_path)
        self.mesh.buffer_packed_data(data, data_format, indices)


    cpdef draw(self, unsigned int mode=GL_TRIANGLES):
        if not self.mesh:
            raise RuntimeError('Drawable was not properly init! Was super() called?')
        self.mesh.bind()
        self.shader_program.use()
        self.shader_program.bind_textures()
        if self.indexed:
            glDrawElements(mode, self.no_of_indices, GL_UNSIGNED_INT, NULL)
        else:
            glDrawArrays(mode, 0, self.no_of_indices)
