cdef extern from *:
    #*******
    # TYPES
    #*******

    ctypedef int GLint
    ctypedef unsigned int GLuint
    ctypedef unsigned int GLsizei
    ctypedef unsigned int GLenum
    ctypedef float GLfloat
    ctypedef char GLchar
    ctypedef unsigned char GLboolean
    ctypedef void GLvoid


    #***********
    # FUNCTIONS
    #***********

    # uniforms
    void glUniform1f(GLint location, GLfloat v0)
    void glUniform2f(GLint location, GLfloat v0, GLfloat v1)
    void glUniform3f(GLint location, GLfloat v0, GLfloat v1, GLfloat v2)
    void glUniform4f(GLint location, GLfloat v0, GLfloat v1, GLfloat v2, GLfloat v3)
    void glUniform1i(GLint location, GLint v0)
    void glUniform2i(GLint location, GLint v0, GLint v1)
    void glUniform3i(GLint location, GLint v0, GLint v1, GLint v2)
    void glUniform4i(GLint location, GLint v0, GLint v1, GLint v2, GLint v3)
    void glUniform1ui(GLint location, GLuint v0)
    void glUniform2ui(GLint location, GLuint v0, GLuint v1)
    void glUniform3ui(GLint location, GLuint v0, GLuint v1, GLuint v2)
    void glUniform4ui(GLint location, GLuint v0, GLuint v1, GLuint v2, GLuint v3)
    void glUniform1fv(GLint location, GLsizei count, const GLfloat *value)
    void glUniform2fv(GLint location, GLsizei count, const GLfloat *value)
    void glUniform3fv(GLint location, GLsizei count, const GLfloat *value)
    void glUniform4fv(GLint location, GLsizei count, const GLfloat *value)
    void glUniform1iv(GLint location, GLsizei count, const GLint *value)
    void glUniform2iv(GLint location, GLsizei count, const GLint *value)
    void glUniform3iv(GLint location, GLsizei count, const GLint *value)
    void glUniform4iv(GLint location, GLsizei count, const GLint *value)
    void glUniform1uiv(GLint location, GLsizei count, const GLuint *value)
    void glUniform2uiv(GLint location, GLsizei count, const GLuint *value)
    void glUniform3uiv(GLint location, GLsizei count, const GLuint *value)
    void glUniform4uiv(GLint location, GLsizei count, const GLuint *value)
    void glUniformMatrix2fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix3fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix4fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix2x3fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix3x2fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix2x4fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix4x2fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix3x4fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    void glUniformMatrix4x3fv(GLint location, GLsizei count, GLboolean transpose, const GLfloat *value)
    GLint glGetUniformLocation(GLuint program, const GLchar* name)
    
    # window functions
    void glClearColor(float, float, float, float)
    void glClear(unsigned int)
    void glScissor(int, int, int, int)
    void glEnable(unsigned int)
    void glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
    void glFlush()
    void glFinish()
    void glPixelStorei(GLenum pname, GLint param)
    void glReadPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid * data)


    # shader functions
    unsigned int glCreateProgram()
    void glAttachShader(unsigned int program, unsigned int shader)
    void glLinkProgram(unsigned int program)
    void glDeleteShader(unsigned int shader)
    
    # model functions
    void glGenVertexArrays(int, unsigned int*)
    void glGenBuffers(int count, unsigned int* buffer_array)
    void glBindVertexArray(unsigned int)
    void glBindBuffer(unsigned int, unsigned int)

    void glBufferData(unsigned int target, ptrdiff_t size, const void* data, unsigned int usage)
    void glVertexAttribPointer(unsigned int index, int size, unsigned int type,
                               unsigned char normalized, int stride, const void* pointer)
    void glEnableVertexAttribArray(unsigned int)

    #  texture functions
    void glGenTextures(int n, unsigned int* textures)
    void glBindTexture(unsigned int target, unsigned int texture)  # eg glBindTexture(GL_TEXTURE_2D, texture)
    void glTexImage2D(unsigned int target, int mipmap_level, int internal_format, int width, int height,
                      int must_be_zero, unsigned int data_format, unsigned int data_type, const void* data)
    # data_format: the format you pass in. internal_format: how the data is stored. They should probably be the same
    # (more detail at https://stackoverflow.com/questions/34497195/difference-between-format-and-internalformat)
    void glGenerateMipmap(unsigned int target)

    void glActiveTexture(unsigned int unit)
    void glUniform1i(int location, int value)
    int glGetUniformLocation(unsigned int program, const char* name)
    void glUseProgram(unsigned int program)

    # engine functions
    void glDrawArrays(unsigned int, int, int)
    void glDrawElements(unsigned int mode, int count, unsigned int data_type, void* indices)  # let indices = 0 if EBO

    # misc functions
    void glfwSwapInterval(int)
    void glBlendFunc(unsigned int, unsigned int)


    #***********
    # CONSTANTS
    #***********

    # window constants
    unsigned int GL_SCISSOR_TEST
    unsigned int GL_MULTISAMPLE
    unsigned int GL_COLOR_BUFFER_BIT
    unsigned int GL_DEPTH_BUFFER_BIT
    unsigned int GL_UNPACK_ALIGNMENT
    
    # model constants
    unsigned int GL_ARRAY_BUFFER
    unsigned int GL_STATIC_DRAW
    unsigned int GL_ELEMENT_ARRAY_BUFFER

    # shader constants
    int GL_FRAGMENT_SHADER
    int GL_VERTEX_SHADER
    int GL_GEOMETRY_SHADER

    # texture constants
    unsigned int GL_TEXTURE0
    unsigned int GL_TEXTURE_2D
    unsigned int GL_RGB
    unsigned int GL_RGBA

    # engine constants
    unsigned int GL_TRIANGLES
    unsigned int GL_POINTS
    unsigned int GL_LINES

    # misc constants
    unsigned int GL_UNSIGNED_INT
    unsigned int GL_FLOAT
    unsigned int GL_UNSIGNED_BYTE
    unsigned int GL_BLEND
    unsigned int GL_SRC_ALPHA
    unsigned int GL_ONE_MINUS_SRC_ALPHA
    unsigned int GL_DEPTH_TEST


    #******
    # GLAD
    #******
    ctypedef void* (* GLADloadproc)(const char *name)
    int gladLoadGLLoader(GLADloadproc)

# python accessible constants
RGBA = GL_RGBA
TRIANGLES = GL_TRIANGLES
POINTS = GL_POINTS
LINES = GL_LINES

COLOR_BUFFER_BIT = GL_COLOR_BUFFER_BIT
DEPTH_BUFFER_BIT = GL_DEPTH_BUFFER_BIT
