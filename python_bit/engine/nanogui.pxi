cimport nanogui

cdef class Gui:
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
        glEnable(GL_DEPTH_TEST)

    cpdef update_layout(self):
        self.screen.performLayout()

    cpdef handle_key(self, int key, int scancode, int action, int mods):
        self.screen.keyCallbackEvent(key, scancode, action, mods)

cdef class FormHelper:
    cdef nanogui.FormHelper* gui

    def __cinit__(self, Gui gui, *args, **kwargs):
        # takes a cython Gui object
        self.gui = new nanogui.FormHelper(gui.screen)

    def __init__(self, Gui gui, *args, **kwargs):
        pass

    cpdef GuiWindow add_window(self, x, y, name):
        return GuiWindow(self, x, y, name)

cdef class GuiWindow:
    cdef nanogui.Window* window

    def __cinit__(self, FormHelper form_helper, x, y, name):
        self.window = form_helper.gui.addWindow(nanogui.Vector2i(x, y), name)

    def focused(self):
        return self.window.focused()
