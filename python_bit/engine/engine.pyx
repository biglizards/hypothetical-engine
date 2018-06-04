# distutils: language = c++

cimport cengine
from cengine cimport GLFWwindow
from cengine cimport load_shader as c_load_shader
from engine.shader cimport load_shader_from_file
NO DONT USE THAT USE .PXI INSTEAD
ITS WAY BETTER
ALSO YES THIS IS MEANT TO CAUSE A SyntaxError
DEAL WITH IT THANKS
ALSO BEFORE YOU DO THAT COMMIT Y'KNOW


cpdef uuu(path, shader_type):
    return load_shader_from_file(path, shader_type)

cpdef foo():
    cdef unsigned int a = 0
    return glGenVertexArrays(0, &a)

cdef extern from *:
    void glfwSwapBuffers(GLFWwindow* window)
    void glfwPollEvents()
    int glfwWindowShouldClose(GLFWwindow* window)

    void glClearColor(float, float, float, float)
    void glClear(unsigned int)
    void glfwSwapInterval(int)

    int GL_COLOR_BUFFER_BIT  # haha yes this constant exists
    int GL_FRAGMENT_SHADER

    void glGenVertexArrays(int, unsigned int*)


cdef char* load_file(const char* path):
    return open(path, 'rb').read()

cpdef int main():
    cengine.demo(load_file)

cpdef try_to_create_shader():
    cdef char* shader_source = load_file('shaders/basic.frag')
    cdef unsigned int frag_shader = c_load_shader(shader_source, GL_FRAGMENT_SHADER)

cpdef unsigned int load_shader(path, int shader_type):
    shader_source = open(path, 'rb').read()
    return cengine.load_shader(shader_source, shader_type)


cdef class Window:
    cdef GLFWwindow* window
    cdef void *some_func

    def __cinit__(self, int width=800, int height=600, name='window boi', *args, **kwargs):
        byte_str = name.encode()
        cdef char* c_string = byte_str
        self.window = cengine.create_window(width, height, c_string)
        glfwSwapInterval(0)

    def __init__(self, int width=800, int height=600, name='window boi'):  # included to force a valid signature
        pass

    def __dealloc__(self):
        cengine.glfwDestroyWindow(self.window)

    cpdef void swap_buffers(self):
        glfwSwapBuffers(self.window)

    cpdef void clear_colour(self, float a, float b, float c, float d):
        glClearColor(a, b, c, d)
        glClear(GL_COLOR_BUFFER_BIT)

    cpdef bint should_close(self):
        return glfwWindowShouldClose(self.window)


cpdef poll_events():
    glfwPollEvents()
