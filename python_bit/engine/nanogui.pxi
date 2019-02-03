cimport nanogui
from nanogui cimport FormWidget
from libcpp cimport bool as c_bool
from libcpp.string cimport string
import inspect

# note to self about the way nanogui works
# everything is a widget. Widgets can contain other widgets
# each widget can have its own layout (and needs one for you to add widgets to it)
# technically you can add widgets to buttons but that's dumb and doesnt make any sense (and also crashes it)

cdef class Gui:
    cdef nanogui.Screen* screen
    cdef GLFWwindow* window
    cdef list windows

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
        return any(window.focused() for window in self.windows)


cdef class Widget:
    cdef nanogui.Widget* widget
    cdef list children

    def __cinit__(self, *args, **kwargs):
        self.children = []

    def __init__(self, Widget parent, Layout layout = None, *args, **kwargs):
        if type(self) is Widget:  # only generate one if called directly
            self.widget = new nanogui.Widget(parent.widget)
        else:
            parent.children.append(self)
        if layout is not None:
            self.widget.setLayout(layout.ptr)

    def set_layout(self, Layout layout):
        self.widget.setLayout(layout.ptr)

cdef class Layout:
    cdef nanogui.Layout* ptr
    pass

cdef class BoxLayout(Layout):
    #cdef nanogui.BoxLayout* ptr
    def __init__(self, int orientation, int alignment = <int>nanogui.Middle,
                  int margin = 0, int spacing = 0):
        self.ptr = new nanogui.BoxLayout(<nanogui.Orientation>orientation, <nanogui.Alignment>alignment,
                                         margin, spacing)
cdef class GroupLayout(Layout):
    #cdef nanogui.BoxLayout* ptr
    def __init__(self, int margin=15, int spacing=6, int groupSpacing=14, int groupIndent=20):
        self.ptr = new nanogui.GroupLayout(margin, spacing, groupSpacing, groupIndent)



cdef class GuiWindow(Widget):  # inherit from widget? would require moving from __cinit__ to __init__, which could cause segfaults
    cdef nanogui.Window* window
    cdef Gui gui

    def __cinit__(self, int x, int y, name, FormHelper form_helper=None, Gui gui=None, Layout layout=None):
        assert not(form_helper and gui), "Either a FormHelper OR Gui must be passed to GuiWindow, not both"
        name = to_bytes(name)
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

    def set_layout(self, Layout layout):
        self.window.setLayout(layout.ptr)


cdef class FormHelper:
    cdef nanogui.FormHelper* helper
    cdef Gui gui
    cdef object widgets

    def __cinit__(self, Gui gui, *args, **kwargs):
        # takes a cython Gui object
        self.gui = gui
        self.helper = new nanogui.FormHelper(gui.screen)
        self.widgets = []

    def __init__(self, Gui gui, *args, **kwargs):
        pass

    cpdef GuiWindow add_window(self, x, y, name):
        return GuiWindow(x, y, name, self)

    cpdef set_window(self, GuiWindow window):
        self.helper.setWindow(window.window)

    cpdef GuiWindow window(self):
        cdef nanogui.Window* window = self.helper.window()
        cdef GuiWindow gui_window
        for gui_window in self.gui.windows:
            if gui_window.window is window:
                return gui_window

    cpdef add_variable(self, name, variable_type, linked_var=None, getter=None, setter=None):
        """
        a wrapper function for creating the [Type]Widget class
        """
        name = to_bytes(name)
        widget = None
        if linked_var is not None and not isinstance(linked_var, str):
            raise ValueError("linked_var must be of type str (you probably passed the variable directly)")
        if variable_type is int:
            widget = IntWidget(self, name, getter, setter, linked_var)
        elif variable_type is bool:
            widget = BoolWidget(self, name, getter, setter, linked_var)
        elif variable_type is float:
            ext_locals = get_locals()
            widget = FloatWidget(self, name, getter, setter, linked_var)
        elif variable_type is str:
            widget = StringWidget(self, name, getter, setter, linked_var)
        self.widgets.append(widget)
        return widget

    cpdef add_combobox(self, name, items, linked_var=None, getter=None, setter=None):
        widget = ComboBoxWidget(self, name, list(map(to_bytes, items)), getter, setter, linked_var)
        self.widgets.append(widget)
        return widget

    cpdef add_button(self, name, callback):
        button = Button(name, callback, helper=self)
        self.widgets.append(button)
        return button

    cpdef add_group(self, name):
        self.helper.addGroup(to_bytes(name))

    cpdef refresh(self):
        self.helper.refresh()

buttons = {}  #

cdef class Button(Widget):
    cdef nanogui.Button* button_ptr
    cdef object callback

    def __cinit__(self, name, callback, FormHelper helper=None, Widget parent=None, int icon=0, *args, **kwargs):
        name = to_bytes(name)
        if helper is None:
            self.button_ptr = new nanogui.Button(parent.widget, name, icon)
            cengine.setButtonCallback(self.button_ptr, <void*>self, self._callback)
        else:
            self.button_ptr = cengine.add_button_(helper.helper, name, <void*>self, self._callback)
        self.callback = callback

    def __init__(self, name, callback, FormHelper helper=None, Widget parent=None, int icon=0, *args, **kwargs):
        if parent:
            super().__init__(parent)

    @staticmethod
    cdef void _callback(void* _self):
        cdef Button self = <Button>_self
        self.callback()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@ it's just widgets from here on down
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

widgets = {}  # <uintptr_t>&Widget : Widget

def get_locals():
    # TODO change name from locals to globals
    # for, uhh, reasons, locals() is only sometimes mutable
    # as in, it's only mutable when it returns module level vars
    # which is the same thing globals() returns - so i'm just using that instead
    return inspect.stack()[0][0].f_globals

cdef class IntWidget:
    cdef readonly int value
    cdef FormWidget[int]* widget_ptr
    cdef public object getter
    cdef public object setter
    cdef object ext_locals
    cdef str linked_var

    def __cinit__(IntWidget self, FormHelper helper, name, getter=None, setter=None, linked_var=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        if linked_var:
            self.ext_locals = get_locals()
            self.linked_var = linked_var
        else:
            self.linked_var = ""
        self.widget_ptr = cengine.add_variable[int](helper.helper, name, self.setter_callback,
                                                    self.getter_callback, self_ptr)

    @staticmethod
    cdef int getter_callback(uintptr_t self_ptr):
        cdef IntWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = self.getter()
        return self.value

    @staticmethod
    cdef void setter_callback(const int& new_value, uintptr_t self_ptr):
        cdef IntWidget self = widgets[self_ptr]
        cdef int old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(new_value, old_value)

cdef class FloatWidget:
    cdef readonly double value
    cdef FormWidget[double]* widget_ptr
    cdef public object getter
    cdef public object setter
    cdef object ext_locals
    cdef str linked_var

    def __cinit__(FloatWidget self, FormHelper helper, name, getter=None, setter=None, linked_var=None,
                  *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        if linked_var:
            self.ext_locals = get_locals()
            self.linked_var = linked_var
        else:
            self.linked_var = ""
        self.widget_ptr = cengine.add_variable[double](helper.helper, name, self.setter_callback,
                                                       self.getter_callback, self_ptr)

    @staticmethod
    cdef double getter_callback(uintptr_t self_ptr):
        cdef FloatWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = self.getter()
        return self.value

    @staticmethod
    cdef void setter_callback(const double& new_value, uintptr_t self_ptr):
        cdef FloatWidget self = widgets[self_ptr]
        cdef double old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(new_value, old_value)

cdef class StringWidget:
    cdef string c_value
    cdef FormWidget[string]* widget_ptr
    cdef public object getter
    cdef public object setter
    cdef object ext_locals
    cdef str linked_var

    def __cinit__(StringWidget self, FormHelper helper, name, getter=None, setter=None, linked_var=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        if linked_var:
            self.ext_locals = get_locals()
            self.linked_var = linked_var
        else:
            self.linked_var = ""
        self.widget_ptr = cengine.add_variable[string](helper.helper, name, self.setter_callback,
                                                    self.getter_callback, self_ptr)

    @staticmethod
    cdef string getter_callback(uintptr_t self_ptr):
        cdef StringWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = self.getter()
        return self.c_value

    @staticmethod
    cdef void setter_callback(const string& new_value, uintptr_t self_ptr):
        cdef StringWidget self = widgets[self_ptr]
        cdef str old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(self.value, old_value)

    @property
    def value(self):
        return self.c_value.decode()

    @value.setter
    def value(self, new_value):
        self.c_value = to_bytes(new_value)


cdef class BoolWidget:
    cdef readonly c_bool value
    cdef FormWidget[c_bool]* widget_ptr
    cdef public object getter
    cdef public object setter
    cdef object ext_locals
    cdef str linked_var

    def __cinit__(BoolWidget self, FormHelper helper, name, getter=None, setter=None, linked_var=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        if linked_var:
            self.ext_locals = get_locals()
            self.linked_var = linked_var
        else:
            self.linked_var = ""
        self.widget_ptr = cengine.add_variable[c_bool](helper.helper, name, self.setter_callback,
                                                       self.getter_callback, self_ptr)

    @staticmethod
    cdef c_bool getter_callback(uintptr_t self_ptr):
        cdef BoolWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = self.getter()
        return self.value

    @staticmethod
    cdef void setter_callback(const c_bool& new_value, uintptr_t self_ptr):
        cdef BoolWidget self = widgets[self_ptr]
        cdef bint old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(new_value, old_value)

cdef extern from *:
    """enum DummyEnum { };"""
    # pycharm things this is a syntax error; its not, it compiles fine, and needs this here
    cdef enum DummyEnum:
        pass

cdef class ComboBoxWidget:
    cdef readonly DummyEnum index
    cdef FormWidget[DummyEnum]* widget_ptr
    cdef public object getter
    cdef public object setter
    cdef public object items
    cdef object ext_locals
    cdef str linked_var

    def __cinit__(ComboBoxWidget self, FormHelper helper, name, items, getter=None, setter=None,
                  linked_var=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.items = items
        self.getter = getter
        self.setter = setter
        if linked_var:
            self.ext_locals = get_locals()
            self.linked_var = linked_var
        else:
            self.linked_var = ""
        self.widget_ptr = cengine.add_variable[DummyEnum](helper.helper, name, self.setter_callback,
                                                    self.getter_callback, self_ptr)
        self.widget_ptr.setItems(items)

    @staticmethod
    cdef DummyEnum getter_callback(uintptr_t self_ptr):
        cdef ComboBoxWidget self = widgets[self_ptr]
        if self.getter is not None:
            getter_result = self.getter()
            if isinstance(getter_result, int):
                self.index = getter_result
            else:
                self.value = getter_result
        return self.index

    @staticmethod
    cdef void setter_callback(const DummyEnum& new_index, uintptr_t self_ptr):
        cdef ComboBoxWidget self = widgets[self_ptr]
        old_value = self.value
        self.index = new_index
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(self.value, old_value)

    @property
    def value(self):
        return self.items[self.index].decode()

    @value.setter
    def value(self, new_value):
        self.index = self.items.index(to_bytes(new_value))
