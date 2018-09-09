cimport nanogui

cdef extern from *:
    double glfwGetTime()

cdef class Screen:
    cdef nanogui.Screen* screen
    cdef GLFWwindow* window

    def __cinit__(self, Window window, *args, **kwargs):
        self.screen = new nanogui.Screen()
        self.screen.initialize(window.window, False)

    def __init__(self, window):
        pass

    def __dealloc__(self):
        del self.screen

    cpdef draw(self):
        # not sure about which way round these are meant to go
        # guess we'll see
        self.screen.drawContents()
        self.screen.drawWidgets()

        # fix transparancy, since nanogui disables it
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    cpdef update_layout(self):
        self.screen.performLayout()

cdef class FormHelper:
    cdef nanogui.FormHelper* gui

    def __cinit__(self, Screen screen, *args, **kwargs):
        # takes a cython Screen object
        self.gui = new nanogui.FormHelper(screen.screen)

    def __init__(self, Screen screen, *args, **kwargs):
        pass

    cpdef add_window(self, x, y, name):
        self.gui.addWindow(nanogui.Vector2i(x, y), name)

