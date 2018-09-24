cdef GLFWwindow* create_window(int width, int height, const char* name):
    glfwInit()
    glfwWindowHint(GLFW_SAMPLES, 4)
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

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)

    return window

window_objects_by_pointer = {}

cdef void key_callback(GLFWwindow* window_ptr, int key, int scancode, int action, int mods):
    cdef Window window = window_objects_by_pointer[<uintptr_t>window_ptr]
    if window.key_callback is None:
        return
    window.key_callback(window, key, scancode, action, mods)

cdef void framebuffer_size_callback(GLFWwindow* window_ptr, int width, int height):
    cdef Window window = window_objects_by_pointer[<uintptr_t>window_ptr]
    glViewport(0, 0, width, height)
    window.width = width
    window.height = height

cdef class Window:
    cdef GLFWwindow* window
    cdef void *some_func
    cdef object key_callback

    cdef public int width
    cdef public int height
    cdef public Gui gui

    def __cinit__(self, int width=800, int height=600, name='window boi', *args, **kwargs):
        byte_str = name.encode()
        cdef char* c_string = byte_str
        self.window = create_window(width, height, c_string)
        self.width = width
        self.height = height
        glfwSwapInterval(0)

        self.key_callback = None
        window_objects_by_pointer[<uintptr_t>self.window] = self
        glfwSetKeyCallback(self.window, key_callback)

        self.gui = Gui(self)

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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cpdef bint should_close(self):
        return glfwWindowShouldClose(self.window)

    cpdef set_key_callback(self, callback_function):
        self.key_callback = callback_function
        glfwSetKeyCallback(self.window, <GLFWkeyfun>key_callback)

    cpdef bint is_pressed(self, key):
        return glfwGetKey(self.window, key) == GLFW_PRESS