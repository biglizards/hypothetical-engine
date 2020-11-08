cimport includes.nanogui as nanogui

from contextvars import ContextVar

include 'nanogui/layout.pxi'
include 'nanogui/helper.pxi'
include 'nanogui/widgets.pxi'

# note to self about the way nanogui works
# everything is a widget. Widgets can contain other widgets
# each widget can have its own layout (and needs one for you to add widgets to it)
# technically you can add widgets to buttons but that's dumb and doesnt make any sense (and also crashes it)

# module level globals
with_block_parent = ContextVar('with_block_parent', default=None)
buttons = {}

# util functions
def error_safe_call(function, *args, default=None):
    if glfw_event_errors:
        return default
    try:
        return function(*args)
    except Exception as e:
        glfw_event_errors.append(e)
        return default

def get_parent():
    parent = with_block_parent.get()
    if parent is None:
        raise NestingError("parent must be passed by argument if not in a 'with' block")
    return parent

def file_dialog(save):
    return nanogui.file_dialog([(b"*", b"any file")], save).decode()

class NestingError(RuntimeError):
    pass

# big classes
cdef class Gui:
    cdef nanogui.Screen* screen
    cdef GLFWwindow* window
    cdef readonly list windows

    def __cinit__(self, Window window, *args, **kwargs):
        self.windows = []
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

        # restore gl settings that changed
        set_gl_enables()

    cpdef update_layout(self):
        self.screen.performLayout()

    # handler shims (tbh only one of them actually changes the arguments)
    cpdef handle_cursor_pos(self, double x, double y):
        self.screen.cursorPosCallbackEvent(x, y)
    cpdef handle_mouse_button(self, int button, int action, int modifiers):
        self.screen.mouseButtonCallbackEvent(button, action, modifiers)
    cpdef handle_key(self, int key, int scancode, int action, int mods):
        self.screen.keyCallbackEvent(key, scancode, action, mods)
    cpdef handle_char(self, unsigned int codepoint):
        self.screen.charCallbackEvent(codepoint)
    cpdef handle_drop(self, int count, list filenames):
        cdef const char** filename_array = to_c_array(filenames)
        self.screen.dropCallbackEvent(count, filename_array)
        free(filename_array)
    cpdef handle_scroll(self, double x, double y):
        self.screen.scrollCallbackEvent(x, y)
    cpdef handle_resize(self, int width, int height):
        self.screen.resizeCallbackEvent(width, height)

    def focused(self):
        cdef GuiWindow window
        return any(window.focused() for window in self.windows) \
               or any(window.focused_recursive() for window in self.windows)


cdef class GuiWindow(Widget):  # inherit from widget? would require moving from __cinit__ to __init__, which could cause segfaults
    cdef nanogui.Window* window
    cdef Gui gui

    def __cinit__(self, int x, int y, name, FormHelper form_helper=None, Gui gui=None, Layout layout=None):
        assert not(form_helper and gui), "Either a FormHelper OR Gui must be passed to GuiWindow, not both"
        name = to_bytes(name)
        self.window = NULL
        if form_helper:
            gui = form_helper.gui
            self.window = form_helper.helper.addWindow(nanogui.Vector2i(x, y), name)
        elif gui:
            self.window = new nanogui.Window(gui.screen, name)
            self.window.setPosition(nanogui.Vector2i(x, y))
            if layout is not None:
                self.window.setLayout(layout.ptr)
        gui.windows.append(self)
        self.gui = gui
        self.widget = self.window  # alias for treating Window as Widget
        self.parent = None

    # noinspection PyMissingConstructor
    def __init__(self, int x, int y, name, FormHelper form_helper=None, Gui gui=None, Layout layout=None):
        """included to force valid signature"""
        # note that the call to super is intentionally ignored, as it is also ignored in nanogui. blame C++
        pass

    def focused(self):
        if self.window != NULL:
            return self.window.focused()

    def dispose(self):
        self.gui.windows.remove(self)  # delete references to this window
        self.window.dispose()
        # noinspection PyAttributeOutsideInit
        self.window = NULL

    def set_fixed_width(self, int width):
        self.window.setFixedWidth(width)

    @property
    def width(self):
        return self.window.width()

    @property
    def height(self):
        return self.window.height()

    def set_position(self, int x, int y):
        self.window.setPosition(nanogui.Vector2i(x, y))
