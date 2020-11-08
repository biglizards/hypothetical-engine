"""
this is where i would put my shader spec
...
IF I HAD ONE
"""

IF FALSE:
    # this is a hack to get code inspection working
    include "util.pxi"
    include "includes/gl_declarations.pxi"
    include "texture.pxi"


from includes.cengine cimport load_shader as c_load_shader
import ctypes


FRAGMENT_SHADER = GL_FRAGMENT_SHADER
VERTEX_SHADER = GL_VERTEX_SHADER
GEOMETRY_SHADER = GL_GEOMETRY_SHADER

cpdef unsigned int load_shader_from_file(path, unsigned int shader_type):
    shader_source = open(path, 'rb').read()
    return c_load_shader(shader_source, shader_type)

cdef float* value_ptr(thing):
    return <float*>(<uintptr_t>ctypes.addressof(glm.value_ptr(thing).contents))

cpdef load_shader_program(vert_path, frag_path, geometry_path=None):
    cdef unsigned int vert_shader, frag_shader, geometry_shader
    vert_shader = load_shader_from_file(vert_path, GL_VERTEX_SHADER)
    frag_shader = load_shader_from_file(frag_path, GL_FRAGMENT_SHADER)
    geometry_shader = load_shader_from_file(geometry_path, GL_GEOMETRY_SHADER) if geometry_path else 0

    cdef unsigned int program = glCreateProgram()
    glAttachShader(program, vert_shader)
    glAttachShader(program, frag_shader)
    if geometry_shader:
        glAttachShader(program, geometry_shader)

    glLinkProgram(program)

    glDeleteShader(vert_shader)
    glDeleteShader(frag_shader)
    if geometry_shader:
        glDeleteShader(geometry_shader)

    return program

cdef class ShaderProgram:
    cdef unsigned int program
    cdef public list paths
    cdef int trans_mat_location

    def __init__(self, vert_path, frag_path, geo_path=None, trans_mat_name=None):
        self.program = load_shader_program(vert_path, frag_path, geo_path)
        self.paths = [vert_path, frag_path, geo_path]

        trans_mat_name = to_bytes(trans_mat_name) if trans_mat_name is not None else b'transformMat'
        self.trans_mat_location = glGetUniformLocation(self.program, trans_mat_name)

    cpdef use(self):
        glUseProgram(self.program)

    cpdef bint set_trans_mat(self, value):
        self.use()
        glUniformMatrix4fv(self.trans_mat_location, 1, False, value_ptr(value))

    cpdef bint set_value(self, name, value) except False:  # i _think_ this means on error return false
        self.use()
        cdef bytes c_name = to_bytes(name)
        cdef int location = glGetUniformLocation(self.program, c_name)

        if isinstance(value, int):  # also returns true for bools, but that's fine here
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, glm.mat4):
            glUniformMatrix4fv(location, 1, False, value_ptr(value))
        elif isinstance(value, glm.vec4):
            glUniform4fv(location, 1, value_ptr(value))
        else:
            raise TypeError("invalid type and/or type not yet implemented")

        return True
