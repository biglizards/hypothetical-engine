"""
this is where i would put my shader spec
...
IF I HAD ONE
"""


from cengine cimport load_shader as c_load_shader

cdef extern from *:
    unsigned int glCreateProgram()
    void glAttachShader(unsigned int program, unsigned int shader)
    void glLinkProgram(unsigned int program)
    void glDeleteShader(unsigned int shader)

    int GL_FRAGMENT_SHADER
    int GL_VERTEX_SHADER
    int GL_GEOMETRY_SHADER
    void glfwInit()

FRAGMENT_SHADER = GL_FRAGMENT_SHADER
VERTEX_SHADER = GL_VERTEX_SHADER
GEOMETRY_SHADER = GL_GEOMETRY_SHADER

cpdef unsigned int load_shader_from_file(path, unsigned int shader_type):
    shader_source = open(path, 'rb').read()
    print("got shader program", shader_source)
    return c_load_shader(shader_source, shader_type)


cpdef unsigned int load_shader(const char* shader_source, unsigned int shader_type):
    return c_load_shader(shader_source, shader_type)


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

    def __cinit__(self, vert_path, frag_path, geometry_path=None):
        pass