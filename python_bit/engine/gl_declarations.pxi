cdef extern from *:
    ctypedef int GLint
    ctypedef unsigned int GLuint
    ctypedef unsigned int GLsizei
    ctypedef float GLfloat
    ctypedef char GLchar
    ctypedef unsigned char GLboolean

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