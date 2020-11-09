from libcpp.string cimport string
from libcpp cimport bool as c_bool
from libc.stdint cimport uintptr_t

from includes.nanogui cimport FormWidget


cdef class FormHelper:
    """
    the form helper is a utility class provided to simplify the process of making list-like guis, eg for allowing
    the editing of the attributes of an object.

    example:
        my_object.foo = 2

        helper = engine.FormHelper(self.gui)
        new_gui = helper.add_window(0, 0, 'entity properties')
        helper.add_variable("foo", int, getter=lambda: return my_object.foo,
                            setter=lambda x: setattr(my_object, 'foo', x))
    """
    cdef nanogui.FormHelper* helper
    cdef Gui gui
    cdef object widgets
    cdef list manual_getters

    def __cinit__(self, Gui gui, *args, **kwargs):
        # takes a cython Gui object
        self.gui = gui
        self.helper = new nanogui.FormHelper(gui.screen)
        self.widgets = []
        self.manual_getters = []

    def __init__(self, Gui gui, *args, **kwargs):
        pass

    cpdef GuiWindow add_window(self, x, y, name):
        cdef GuiWindow window = GuiWindow(x, y, name, self)
        # manually create and wrap the layout for the window
        cdef AdvancedGridLayout layout = AdvancedGridLayout.__new__(AdvancedGridLayout)
        layout.advanced_ptr = <nanogui.AdvancedGridLayout*>window.widget.layout()
        layout.ptr = layout.advanced_ptr
        window._layout = layout
        return window

    cpdef set_window(self, GuiWindow window):
        self.helper.setWindow(window.window)

    cpdef set_window_unsafe(self, Widget window):
        self.helper.setWindow(<nanogui.Window*>window.widget)

    cpdef GuiWindow window(self):
        cdef nanogui.Window* window = self.helper.window()
        cdef GuiWindow gui_window
        for gui_window in self.gui.windows:
            if gui_window.window is window:
                return gui_window

    cpdef add_variable(self, name, variable_type, getter=None, setter=None):
        """
        a wrapper function for creating the [Type]Widget class
        """
        name = to_bytes(name)
        widget = None
        if variable_type is int:
            widget = IntWidget(self, name, getter, setter)
        elif variable_type is bool:
            widget = BoolWidget(self, name, getter, setter)
        elif variable_type is float:
            widget = FloatWidget(self, name, getter, setter)
        elif variable_type is str:
            widget = StringWidget(self, name, getter, setter)
        self.widgets.append(widget)
        return widget

    cpdef add_combobox(self, name, items, getter=None, setter=None):
        widget = ComboBoxWidget(self, name, list(map(to_bytes, items)), getter, setter)
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
        for box, getter in self.manual_getters:
            box.value = getter()

    cpdef add_manual_getter(self, box, getter):
        self.manual_getters.append((box, getter))


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@ it's just widgets from here on down
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

widgets = {}  # <uintptr_t>&Widget : Widget

cdef class IntWidget:
    cdef readonly int value
    cdef FormWidget[int]* widget_ptr
    cdef public object getter
    cdef public object setter

    def __cinit__(IntWidget self, FormHelper helper, name, getter=None, setter=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        self.widget_ptr = cengine.add_variable[int](helper.helper, name, self.setter_callback,
                                                    self.getter_callback, self_ptr)

    @staticmethod
    cdef int getter_callback(uintptr_t self_ptr):
        cdef IntWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = error_safe_call(self.getter, default=self.value)
        return self.value

    @staticmethod
    cdef void setter_callback(const int& new_value, uintptr_t self_ptr):
        cdef IntWidget self = widgets[self_ptr]
        cdef int old_value = self.value
        self.value = new_value
        if self.setter is not None:
            error_safe_call(self.setter, new_value, old_value)

cdef class FloatWidget:
    cdef readonly double value
    cdef FormWidget[double]* widget_ptr
    cdef public object getter
    cdef public object setter

    def __cinit__(FloatWidget self, FormHelper helper, name, getter=None, setter=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        self.widget_ptr = cengine.add_variable[double](helper.helper, name, self.setter_callback,
                                                       self.getter_callback, self_ptr)

    @staticmethod
    cdef double getter_callback(uintptr_t self_ptr):
        cdef FloatWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = error_safe_call(self.getter, default=self.value)
        return self.value

    @staticmethod
    cdef void setter_callback(const double& new_value, uintptr_t self_ptr):
        cdef FloatWidget self = widgets[self_ptr]
        cdef double old_value = self.value
        self.value = new_value
        if self.setter is not None:
            error_safe_call(self.setter, new_value, old_value)

cdef class StringWidget(Widget):
    cdef string c_value
    cdef FormWidget[string]* widget_ptr
    cdef public object getter
    cdef public object setter

    def __cinit__(StringWidget self, FormHelper helper, name, getter=None, setter=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        self.widget_ptr = cengine.add_variable[string](helper.helper, name, self.setter_callback,
                                                    self.getter_callback, self_ptr)
        self.widget = self.widget_ptr

    def __init__(StringWidget self, FormHelper helper, name, getter=None, setter=None, *args, **kwargs):
        pass

    @staticmethod
    cdef string getter_callback(uintptr_t self_ptr):
        cdef StringWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = error_safe_call(self.getter, default=self.value)
        return self.c_value

    @staticmethod
    cdef void setter_callback(const string& new_value, uintptr_t self_ptr):
        cdef StringWidget self = widgets[self_ptr]
        cdef str old_value = self.value
        self.value = new_value
        if self.setter is not None:
            error_safe_call(self.setter, self.value, old_value)

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

    def __cinit__(BoolWidget self, FormHelper helper, name, getter=None, setter=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.getter = getter
        self.setter = setter
        self.widget_ptr = cengine.add_variable[c_bool](helper.helper, name, self.setter_callback,
                                                       self.getter_callback, self_ptr)

    @staticmethod
    cdef c_bool getter_callback(uintptr_t self_ptr):
        cdef BoolWidget self = widgets[self_ptr]
        if self.getter is not None:
            self.value = error_safe_call(self.getter, default=self.value)
        return self.value

    @staticmethod
    cdef void setter_callback(const c_bool& new_value, uintptr_t self_ptr):
        cdef BoolWidget self = widgets[self_ptr]
        cdef bint old_value = self.value
        self.value = new_value
        if self.setter is not None:
            error_safe_call(self.setter, new_value, old_value)

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

    def __cinit__(ComboBoxWidget self, FormHelper helper, name, items, getter=None, setter=None, *args, **kwargs):
        cdef uintptr_t self_ptr = <uintptr_t><void*>self
        widgets[self_ptr] = self
        self.items = items
        self.getter = getter
        self.setter = setter
        self.widget_ptr = cengine.add_variable[DummyEnum](helper.helper, name, self.setter_callback,
                                                    self.getter_callback, self_ptr)
        self.widget_ptr.setItems(items)

    @staticmethod
    cdef DummyEnum getter_callback(uintptr_t self_ptr):
        cdef ComboBoxWidget self = widgets[self_ptr]
        if self.getter is not None:
            getter_result = error_safe_call(self.getter)
            if isinstance(getter_result, int):
                self.index = getter_result
            elif getter_result is not None:  # todo should None be allowed as a value? what would that mean?
                self.value = getter_result
        return self.index

    @staticmethod
    cdef void setter_callback(const DummyEnum& new_index, uintptr_t self_ptr):
        cdef ComboBoxWidget self = widgets[self_ptr]
        old_value = self.value
        self.index = new_index
        if self.setter is not None:
            error_safe_call(self.setter, self.value, old_value)

    @property
    def value(self):
        return self.items[self.index].decode()

    @value.setter
    def value(self, new_value):
        self.index = self.items.index(to_bytes(new_value))
