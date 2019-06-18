cimport nanogui
from nanogui cimport FormWidget
from libcpp cimport bool as c_bool
from libcpp.string cimport string
from libcpp.vector cimport vector


def file_dialog(save):
    return nanogui.file_dialog([(b"*", b"any file")], save).decode()

# note to self about the way nanogui works
# everything is a widget. Widgets can contain other widgets
# each widget can have its own layout (and needs one for you to add widgets to it)
# technically you can add widgets to buttons but that's dumb and doesnt make any sense (and also crashes it)

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


cdef class Widget:
    cdef nanogui.Widget* widget
    cdef Layout _layout
    cdef readonly list children

    def __cinit__(self, *args, **kwargs):
        self.children = []

    def __init__(self, Widget parent, Layout layout=None, *args, **kwargs):
        assert parent is not None, "parent must not be None"
        if type(self) is Widget:  # only generate one if called directly
            assert parent.widget is not NULL, "parent widget is null, was it correctly init?"
            self.widget = new nanogui.Widget(parent.widget)
        parent.children.append(self)
        if layout is not None:
            self.widget.setLayout(layout.ptr)
            self._layout = layout

    def set_layout(self, Layout layout):
        self.widget.setLayout(layout.ptr)

    def focused(self):
        return self.widget.focused()

    def focused_recursive(self):
        return self.focused() \
               or any(widget.focused_recursive() for widget in self.children)

    @property
    def layout(self):
        if self._layout:
            return self._layout
        print("[WARNING] Layout not found in {0}, generating one manually".format(self))
        self._layout = Layout()
        self._layout.ptr = self.widget.layout()
        return self._layout

    @layout.setter
    def layout(self, Layout layout):
        self.widget.setLayout(layout.ptr)
        self._layout = layout

    @property
    def fixed_width(self):
        return self.widget.fixedWidth()

    @fixed_width.setter
    def fixed_width(self, int value):
        self.widget.setFixedWidth(value)

    @property
    def width(self):
        return self.widget.width()

    @width.setter
    def width(self, int value):
        self.widget.setWidth(value)

    @property
    def fixed_height(self):
        return self.widget.fixedHeight()

    @fixed_height.setter
    def fixed_height(self, int value):
        self.widget.setFixedHeight(value)

    @property
    def height(self):
        return self.widget.height()

    @height.setter
    def height(self, int value):
        self.widget.setHeight(value)

    @property
    def font_size(self):
        return self.widget.fontSize()

    @font_size.setter
    def font_size(self, int value):
        self.widget.setFontSize(value)

    @property
    def visible(self):
        return self.widget.visible()

    @visible.setter
    def visible(self, bint value):
        self.widget.setVisible(value)

    cpdef visibleRecursive(self):
        return self.widget.visibleRecursive()

    cdef nanogui.Widget* find_widget(self, int x, int y):
        return self.widget.findWidget(nanogui.Vector2i(x, y))


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

cdef class AdvancedGridLayout(Layout):
    cdef nanogui.AdvancedGridLayout* advanced_ptr

    def __init__(self, list cols=None, list rows=None, int margin=0, set_helper_stuff=True):
        cdef vector[int] cols_ = cols if cols else []
        cdef vector[int] rows_ = rows if rows else []
        self.advanced_ptr = new nanogui.AdvancedGridLayout(cols_, rows_, margin)
        self.ptr = self.advanced_ptr

        if set_helper_stuff:
            self.advanced_ptr.setMargin(10)
            self.advanced_ptr.setColStretch(2, 1)

    # note: have not written an init because i'm lazy and dont need this other than to wrap it internally
    def set_anchor(self, Widget widget, Anchor anchor):
        self.advanced_ptr.setAnchor(widget.widget, anchor.ptr)

    @property
    def row_count(self):
        return self.advanced_ptr.rowCount()

    cpdef append_row(self, int size=0, float stretch=0.0):
        self.advanced_ptr.appendRow(size, stretch)

cdef class Anchor:
    cdef nanogui.Anchor ptr
    def __init__(self, int x, int y, w=None, h=None,
                 int horiz=<int>nanogui.Fill, int vert=<int>nanogui.Fill):
        if w is not None and h is not None:
            self.ptr = nanogui.Anchor(x, y, w, h, <nanogui.Alignment>horiz, <nanogui.Alignment>vert)
        else:
            self.ptr = nanogui.Anchor(x, y, <nanogui.Alignment>horiz, <nanogui.Alignment>vert)

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

    def set_layout(self, Layout layout):
        self.window.setLayout(layout.ptr)


cdef class FormHelper:
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

cdef class ScrollPanel(Widget):
    cdef nanogui.VScrollPanel* scroll_panel_ptr
    def __init__(self, Widget parent):
        if type(self) is ScrollPanel:
            self.scroll_panel_ptr = new nanogui.VScrollPanel(parent.widget)
            self.widget = self.scroll_panel_ptr
        super(ScrollPanel, self).__init__(parent)

buttons = {}  #

def error_safe_call(function, *args, default=None):
    if glfw_event_errors:
        return default
    try:
        return function(*args)
    except Exception as e:
        glfw_event_errors.append(e)
        return default


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
        self.widget = self.button_ptr

    def __init__(self, name, callback, FormHelper helper=None, Widget parent=None, int icon=0, *args, **kwargs):
        if parent:
            super().__init__(parent)

    @staticmethod
    cdef void _callback(void* _self):
        cdef Button self = <Button>_self
        error_safe_call(self.callback)

    @property
    def text(self):
        return self.button_ptr.caption().decode()

    @text.setter
    def text(self, value):
        self.button_ptr.setCaption(to_bytes(value))


cdef class PopupButton(Widget):  # doesnt inherit from button since there isn't a callback
    cdef nanogui.PopupButton* popup_button
    cdef Widget _popup

    def __cinit__(self, Widget parent, caption="untitled", int button_icon=0, int side=0):
        self.popup_button = new nanogui.PopupButton(parent.widget, to_bytes(caption), button_icon)
        self.widget = self.popup_button

        cdef Popup popup = Popup(parent=self)
        popup.widget = self.popup_button.popup()
        popup.popup = self.popup_button.popup()
        self._popup = popup

        self.side = side


    def __init__(self, Widget parent, caption="untitled", int button_icon=0, int side=0):
        super().__init__(parent)

    @property
    def popup(self):
        return self._popup

    @property
    def side(self):
        return <int>self.popup_button.side()

    @side.setter
    def side(self, int value):
        self.popup_button.setSide(<nanogui.PopupSide>value)


cdef class Popup(Widget):
    cdef nanogui.Popup* popup

    @property
    def anchor_pos(self):
        cdef const nanogui.Vector2i* pos = &self.popup.anchorPos()
        return pos.x(), pos.y()

    @anchor_pos.setter
    def anchor_pos(self, value):
        self.popup.setAnchorPos(nanogui.Vector2i(value[0], value[1]))

    @property
    def anchor_height(self):
        return self.popup.anchorHeight()

    @anchor_height.setter
    def anchor_height(self, int height):
        self.popup.setAnchorHeight(height)

cdef class Label(Widget):
    def __cinit__(self, Widget parent, caption, font="sans-bold", font_size=-1):
        self.widget = new nanogui.Label(parent.widget, to_bytes(caption), to_bytes(font), font_size)

    def __init__(self, Widget parent, caption, font="sans-bold", font_size=-1):
        super().__init__(parent)

cdef class TextBox(Widget):
    cdef nanogui.TextBox* textBox
    cdef public object callback

    def __init__(self, Widget parent, value="", placeholder=None, bint editable=True, callback=None, spinnable=False):
        if type(self) is TextBox:
            self.textBox = new nanogui.TextBox(parent.widget, to_bytes(value))
            cengine.setTextBoxCallback(self.textBox, <void*>self, self._callback)
        self.callback = callback
        self.editable = editable
        self.spinnable = spinnable
        if placeholder is not None:
            self.placeholder = placeholder

        self.widget = self.textBox
        super().__init__(parent)

    @property
    def editable(self):
        return self.textBox.editable()

    @editable.setter
    def editable(self, bint value):
        self.textBox.setEditable(value)

    @property
    def spinnable(self):
        return self.textBox.spinnable()

    @spinnable.setter
    def spinnable(self, bint value):
        self.textBox.setSpinnable(value)

    @property
    def value(self):
        return self.textBox.value().decode()

    @value.setter
    def value(self, value):
        self.textBox.setValue(to_bytes(value))

    # noinspection PyMethodParameters
    @staticmethod
    cdef c_bool _callback(void* _self, const string& value):
        cdef TextBox self = <TextBox>_self
        if self.callback:
            error_safe_call(self.callback, value.decode())
        return True

    @property
    def alignment(self):
        return <int>self.textBox.alignment()

    @alignment.setter
    def alignment(self, int value):
        self.textBox.setAlignment(<nanogui.TextBoxAlignment>value)

    @property
    def placeholder(self):
        return self.textBox.placeholder()

    @placeholder.setter
    def placeholder(self, value):
        self.textBox.setPlaceholder(to_bytes(value))


cdef class FloatBox(TextBox):
    cdef nanogui.FloatBox[double]* floatBox
    def __init__(self, Widget parent, value=0.0, bint editable=True, callback=None, spinnable=True):
        self.floatBox = new nanogui.FloatBox[double](parent.widget, <double>value)
        self.textBox = self.floatBox
        cengine.setFloatBoxCallback[double](<nanogui.FloatBox[double] *>self.textBox, <void*>self, self.float_callback)
        super().__init__(self, editable=True, callback=callback, spinnable=spinnable)

    @staticmethod
    cdef c_bool float_callback(void* _self, double value):
        cdef FloatBox self = <FloatBox>_self
        if self.callback:
            error_safe_call(self.callback, value)
        return True

    @property
    def value(self):
        return self.floatBox.floatValue()

    @value.setter
    def value(self, double value):
        self.floatBox.setValue(value)

cdef class ImagePanel(Widget):
    cdef nanogui.ImagePanel* image_panel_ptr
    cdef nanogui.Images c_images
    cdef object callback

    def __init__(self, Widget parent, images=None, callback=None):
        self.image_panel_ptr = new nanogui.ImagePanel(parent.widget)
        self.callback = callback

        if images is not None:
            self.images = images

        super(ImagePanel, self).__init__(parent)
        cengine.setMetaCallback[nanogui.ImagePanel, int, void](self.image_panel_ptr, <void*>self, self._callback)

    @staticmethod
    def load_images(Gui gui, dirname):
        return nanogui.loadImageDirectory(gui.screen.nvgContext(), to_bytes(dirname))

    @property
    def images(self):
        return self.image_panel_ptr.images()

    @images.setter
    def images(self, images):
        self.c_images = [(i, to_bytes(name)) for i, name in images]
        self.image_panel_ptr.setImages(self.c_images)

    @staticmethod
    cdef void _callback(void* _self, int selected):
        cdef ImagePanel self = <ImagePanel>_self
        error_safe_call(self.callback, selected)

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
