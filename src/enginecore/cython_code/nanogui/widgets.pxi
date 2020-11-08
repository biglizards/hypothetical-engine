from libcpp.string cimport string
from libcpp cimport bool as c_bool


cdef class Widget:
    cdef nanogui.Widget* widget
    cdef Layout _layout
    cdef readonly list children
    cdef Widget parent
    cdef object _token

    setters = ['layout', 'fixed_width', 'width', 'fixed_height', 'height', 'font_size', 'visible']

    def __cinit__(self, *args, **kwargs):
        self.children = []

    def __init__(self, Widget parent=None, Layout layout=None, *args, **kwargs):
        if parent is None:
            parent = get_parent()
        assert parent is not None, "parent must not be None"
        if type(self) is Widget:  # only generate one if called directly
            assert parent.widget is not NULL, "parent widget is null, was it correctly init?"
            self.widget = new nanogui.Widget(parent.widget)
        parent.children.append(self)
        if layout is not None:
            self.widget.setLayout(layout.ptr)
            self._layout = layout

        # if any arguments were passed for which we have a setter, set them
        # currently the setters are just stored in a list, so remember to update them
        for key, value in kwargs.items():
            if key in self.setters:
                setattr(self, key, value)

        self.parent = parent

    def __enter__(self):
        # I used to raise an error here, since code like the below is confusing, but since sometimes widgets
        # are created by the helper, having the parent with block always be the direct parent was too strict

        # a = Widget()
        # b = Widget()
        # with a:
        #     with b:
        #         Widget()

        # if with_block_parent.get() is not None and self.parent != with_block_parent.get():
        #     raise NestingError(f"'with' blocks must be nested as a direct child of their parent ({self.parent}, "
        #                        f"{with_block_parent.get()})")
        self._token = with_block_parent.set(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with_block_parent.reset(self._token)

    def focused(self):
        return self.widget.focused()

    def focused_recursive(self):
        return self.focused() \
               or any(widget.focused_recursive() for widget in self.children)

    def request_focus(self):
        self.widget.requestFocus()

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

cdef class ScrollPanel(Widget):
    cdef nanogui.VScrollPanel* scroll_panel_ptr
    def __init__(self, Widget parent=None, *args, **kwargs):
        if parent is None:
            parent = get_parent()
        if type(self) is ScrollPanel:
            self.scroll_panel_ptr = new nanogui.VScrollPanel(parent.widget)
            self.widget = self.scroll_panel_ptr
        super(ScrollPanel, self).__init__(parent, *args, **kwargs)

cdef class Button(Widget):
    cdef nanogui.Button* button_ptr
    cdef object callback

    def __cinit__(self, name, callback, FormHelper helper=None, Widget parent=None, int icon=0, *args, **kwargs):
        name = to_bytes(name)
        if parent is None:
            parent = get_parent()

        if helper is None:
            self.button_ptr = new nanogui.Button(parent.widget, name, icon)
            cengine.setButtonCallback(self.button_ptr, <void*>self, self._callback)
        else:
            self.button_ptr = cengine.add_button_(helper.helper, name, <void*>self, self._callback)
        self.callback = callback
        self.widget = self.button_ptr

    def __init__(self, name, callback, FormHelper helper=None, Widget parent=None, int icon=0, **kwargs):
        super().__init__(parent, **kwargs)

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
    cdef object callback

    def __cinit__(self, caption="untitled popup button", int button_icon=0, int side=0, Widget parent=None, callback=None,
                  *args, **kwargs):
        if parent is None:
            parent = get_parent()
        self.popup_button = new nanogui.PopupButton(parent.widget, to_bytes(caption), button_icon)
        self.widget = self.popup_button

        cdef Popup popup = Popup(parent=self)
        popup.widget = self.popup_button.popup()
        popup.popup = self.popup_button.popup()
        self._popup = popup

        self.side = side

        if callback:
            self.callback = callback
            cengine.setButtonCallback(self.popup_button, <void*>self, self._callback)

    @staticmethod
    cdef void _callback(void* _self):
        cdef PopupButton self = <PopupButton>_self
        error_safe_call(self.callback)

    def __init__(self, caption="untitled", int button_icon=0, int side=0, Widget parent=None, callback=None, **kwargs):
        super().__init__(parent, **kwargs)

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
    def __cinit__(self, caption, font="sans-bold", font_size=-1, Widget parent=None, *args, **kwargs):
        if parent is None:
            parent = get_parent()
        self.widget = new nanogui.Label(parent.widget, to_bytes(caption), to_bytes(font), font_size)

    def __init__(self, caption, font="sans-bold", font_size=-1, Widget parent=None, **kwargs):
        super().__init__(parent, **kwargs)

cdef class TextBox(Widget):
    cdef nanogui.TextBox* textBox
    cdef public object callback
    cdef public object key_callback

    def __init__(self, value="", placeholder=None, bint editable=True, callback=None, spinnable=False,
                 Widget parent=None, on_key_callback=None, **kwargs):
        if parent is None:
            parent = get_parent()

        if type(self) is TextBox:
            self.textBox = new nanogui.CustomTextBox(parent.widget, to_bytes(value))
            cengine.setTextBoxCallback(self.textBox, <void*>self, self._callback)
            cengine.setTextBoxKeyCallback(<nanogui.CustomTextBox*>self.textBox, <void*>self, self._key_callback)

        self.callback = callback
        self.key_callback = on_key_callback
        self.editable = editable
        self.spinnable = spinnable
        if placeholder is not None:
            self.placeholder = placeholder

        self.widget = self.textBox
        super().__init__(parent, **kwargs)

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

    @staticmethod
    cdef c_bool _key_callback(void* _self, const string& value):
        cdef TextBox self = <TextBox>_self
        if self.key_callback:
            error_safe_call(self.key_callback, value.decode())
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
    def __init__(self, value=0.0, bint editable=True, callback=None, spinnable=True, Widget parent=None, **kwargs):
        if parent is None:
            parent = get_parent()
        self.floatBox = new nanogui.FloatBox[double](parent.widget, <double>value)
        self.textBox = self.floatBox
        cengine.setFloatBoxCallback[double](<nanogui.FloatBox[double] *>self.textBox, <void*>self, self.float_callback)
        super().__init__(editable=True, callback=callback, spinnable=spinnable, parent=parent, **kwargs)

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

    def __init__(self, images=None, callback=None, Widget parent=None, **kwargs):
        if parent is None:
            parent = get_parent()
        self.image_panel_ptr = new nanogui.ImagePanel(parent.widget)
        self.callback = callback

        if images is not None:
            self.images = images

        super(ImagePanel, self).__init__(parent, **kwargs)
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
