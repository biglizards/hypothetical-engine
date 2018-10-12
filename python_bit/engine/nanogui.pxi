cimport nanogui
from nanogui cimport FormWidget
from libcpp cimport bool as c_bool
from libcpp.string cimport string
import inspect
from cpython cimport array
import array

cdef class Gui:
    cdef nanogui.Screen* screen
    cdef GLFWwindow* window
    cdef object windows

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
        print("[GUI] handling key", scancode, action)
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


cdef class GuiWindow:
    cdef nanogui.Window* window

    def __cinit__(self, FormHelper form_helper, x, y, name):
        form_helper.gui.windows.append(self)
        self.window = form_helper.helper.addWindow(nanogui.Vector2i(x, y), name)

    def focused(self):
        return self.window.focused()



cdef class FormHelper:
    cdef nanogui.FormHelper* helper
    cdef readonly int myint
    cdef Gui gui

    def __cinit__(self, Gui gui, *args, **kwargs):
        # takes a cython Gui object
        self.gui = gui
        self.helper = new nanogui.FormHelper(gui.screen)
        myint = 1

    def __init__(self, Gui gui, *args, **kwargs):
        pass

    cpdef GuiWindow add_window(self, x, y, name):
        return GuiWindow(self, x, y, name)

    cpdef add_variable(self, name, variable_type, linked_var=None, getter=None, setter=None):
        """
        a wrapper function for creating the [Type]Widget class
        """
        if not isinstance(linked_var, str):
            raise ValueError("linked_var must be of type str (you probably passed the variable directly)")
        if variable_type is int:
            return IntWidget(self, name, getter, setter, linked_var)
        elif variable_type is bool:
            return BoolWidget(self, name, getter, setter, linked_var)
        elif variable_type is float:
            ext_locals = get_locals()
            return FloatWidget(self, name, getter, setter, linked_var)
        elif variable_type is str:
            return StringWidget(self, name, getter, setter, linked_var)

    cpdef add_combobox(self, name, items, linked_var=None, getter=None, setter=None):
        return ComboBoxWidget(self, name, list(map(to_bytes, items)), getter, setter, linked_var)

    cpdef add_button(self, name, callback):
        return Button(self, name, callback)

    cpdef add_group(self, name):
        self.helper.addGroup(to_bytes(name))

buttons = {}  #

cdef class Button:
    cdef nanogui.Button* button_ptr
    cdef object callback

    def __cinit__(self, FormHelper helper, name, callback, *args, **kwargs):
        self.button_ptr = cengine.add_button_(helper.helper, name, <void*>self, self._callback)
        self.callback = callback

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
            self.value = self.getter(self)
        return self.value

    @staticmethod
    cdef void setter_callback(const int& new_value, uintptr_t self_ptr):
        cdef IntWidget self = widgets[self_ptr]
        cdef int old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(self, new_value, old_value)

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
            self.value = self.getter(self)
        return self.value

    @staticmethod
    cdef void setter_callback(const double& new_value, uintptr_t self_ptr):
        cdef FloatWidget self = widgets[self_ptr]
        cdef double old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(self, new_value, old_value)

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
            self.value = self.getter(self)
        return self.c_value

    @staticmethod
    cdef void setter_callback(const string& new_value, uintptr_t self_ptr):
        cdef StringWidget self = widgets[self_ptr]
        cdef str old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(self, self.value, old_value)

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
            self.value = self.getter(self)
        return self.value

    @staticmethod
    cdef void setter_callback(const c_bool& new_value, uintptr_t self_ptr):
        cdef BoolWidget self = widgets[self_ptr]
        cdef bint old_value = self.value
        self.value = new_value
        if self.linked_var:
            self.ext_locals[self.linked_var] = self.value
        if self.setter is not None:
            self.setter(self, new_value, old_value)

cdef extern from *:
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
            getter_result = self.getter(self)
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
            self.setter(self, self.value, old_value)

    @property
    def value(self):
        return self.items[self.index].decode()

    @value.setter
    def value(self, new_value):
        self.index = self.items.index(to_bytes(new_value))
