cdef extern from *:
    ctypedef struct GLFWwindow:
        pass
    ctypedef struct GLFWmonitor:
        pass

    ctypedef void* (* GLADloadproc)(const char *name)
    ctypedef void (*GLFWglproc)()

    void glfwInit()
    double glfwGetTime()
    void glfwWindowHint(int hint, int value)
    GLFWwindow* glfwCreateWindow(int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share)
    void glfwMakeContextCurrent(GLFWwindow* window)

    void glClearColor(float, float, float, float)
    void glClear(unsigned int)
    void glScissor(int, int, int, int)
    void glEnable(unsigned int)
    unsigned int GL_SCISSOR_TEST

    int GLFW_CONTEXT_VERSION_MAJOR
    int GLFW_CONTEXT_VERSION_MINOR
    int GLFW_OPENGL_PROFILE
    int GLFW_OPENGL_CORE_PROFILE

    int gladLoadGLLoader(GLADloadproc)
    GLFWglproc glfwGetProcAddress(const char* procname)


cdef GLFWwindow* create_window(int width, int height, const char* name):
    glfwInit()
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    window = glfwCreateWindow(width, height, name, NULL, NULL)

    if window is NULL:
        print("ERROR: FAILED TO CREATE WINDOW")
        return NULL
    glfwMakeContextCurrent(window)

    if not gladLoadGLLoader(<GLADloadproc>glfwGetProcAddress):
        print("ERROR: FAILED TO INIT GLAD")

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    return window

cdef class Window:
    cdef GLFWwindow* window
    cdef void *some_func

    def __cinit__(self, int width=800, int height=600, name='window boi', *args, **kwargs):
        byte_str = name.encode()
        cdef char* c_string = byte_str
        self.window = create_window(width, height, c_string)
        glfwSwapInterval(0)

    def __init__(self, int width=800, int height=600, name='window boi', *args, **kwargs):
        # included to force a valid signature
        pass

    def __dealloc__(self):
        cengine.glfwDestroyWindow(self.window)

    cpdef void swap_buffers(self):
        glfwSwapBuffers(self.window)

    cpdef void clear_colour(self, double a, double b, double c, double d):
        # this line is hella ugly, but i need to do this to prevent an error
        # just pretend the <float>s aren't there
        glClearColor(<float>a, <float>b, <float>c, <float>d)
        glClear(GL_COLOR_BUFFER_BIT)

    cpdef bint should_close(self):
        return glfwWindowShouldClose(self.window)
