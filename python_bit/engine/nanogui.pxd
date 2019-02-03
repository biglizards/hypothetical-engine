from libcpp.string cimport string
from libcpp.functional cimport function
from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "nanogui/nanogui.h" namespace "nanogui::detail":
    cpdef cppclass FormWidget[T]:
        T value() except +
        void setItems(const vector[string]& items) except +

cdef extern from "nanogui/nanogui.h" namespace "nanogui::Orientation":
    cdef enum Orientation "nanogui::Orientation":
        Horizontal,
        Vertical

cdef extern from "nanogui/nanogui.h" namespace "nanogui::Alignment":
    cdef enum Alignment "nanogui::Alignment":
        Minimum,
        Middle,
        Maximum,
        Fill

cdef extern from "nanogui/nanogui.h" namespace "nanogui":
    ctypedef struct GLFWwindow:
        pass

    cdef cppclass Vector2i:
        Vector2i(int, int) except +

    cdef cppclass Widget:
        Widget(Widget *parent) except +
        Widget *parent() except +
        void setParent(Widget *parent) except +
        Layout *layout() except +
        void setLayout(Layout *layout) except +
        # theme stuff
        const Vector2i &position() except +
        void setPosition(const Vector2i &pos)  except +
        Vector2i absolutePosition() except +
        const Vector2i &size() except +
        void setSize(const Vector2i &size) except +
        int width() except +
        void setWidth(int width) except +
        int height() except +
        void setHeight(int height) except +
        const Vector2i &fixedSize() except +
        void setFixedSize(const Vector2i &fixedSize) except +
        int fixedWidth() except +
        void setFixedWidth(int width) except +
        int fixedHeight() except +
        void setFixedHeight(int width) except +
        bool visible() except +
        bool visibleRecursive() except +
        void setVisible(bool visible) except +
        int childCount() except +
        const vector[Widget *] &children() except +
        bint focused() except +

    cdef cppclass Label(Widget):
        Label(Widget *parent, const string &caption) except +
        Label(Widget *parent, const string &caption, const string &font) except +
        Label(Widget *parent, const string &caption, const string &font, int fontSize) except +

    cdef cppclass TextBox(Widget):
        TextBox(Widget *parent) except +
        TextBox(Widget *parent, const string &value) except +

    cdef cppclass FloatBox[T](TextBox):
        FloatBox(Widget *parent) except +
        FloatBox(Widget *parent, T value) except +

    cdef cppclass Layout:
        pass

    cdef cppclass BoxLayout(Layout):
        BoxLayout(Orientation orientation) except +
        BoxLayout(Orientation orientation, Alignment alignment) except +
        BoxLayout(Orientation orientation, Alignment alignment, int margin) except +
        BoxLayout(Orientation orientation, Alignment alignment, int margin, int spacing) except +
        # also more getters/setters but i cba
    cdef cppclass GroupLayout(Layout):
        GroupLayout(int margin, ) except +
        GroupLayout(int margin, int spacing) except +
        GroupLayout(int margin, int spacing, int groupSpacing) except +
        GroupLayout(int margin, int spacing, int groupSpacing, int groupIndent) except +

    cdef cppclass Screen(Widget):
        Screen() except +
        void initialize(GLFWwindow *window, bint shutdownGLFWOnDestruct) except +
        void setVisible(bint) except +
        void performLayout() except +
        void drawContents() except +
        void drawWidgets() except +

        # callback events
        bint cursorPosCallbackEvent(double x, double y) except +
        bint mouseButtonCallbackEvent(int button, int action, int modifiers) except +
        bint keyCallbackEvent(int key, int scancode, int action, int mods) except +
        bint charCallbackEvent(unsigned int codepoint) except +
        bint dropCallbackEvent(int count, const char** filenames) except +
        bint scrollCallbackEvent(double x, double y) except +
        bint resizeCallbackEvent(int width, int height) except +
        
        double mLastInteraction

    cpdef cppclass Window(Widget):
        # Window(Widget* parent, const string& title = "Untitled") except +  # for some reason default argument breaks it
        Window(Widget* parent, const string& title) except +
        Window(Widget* parent) except +
        const string& title() except +
        void setTitle(const string& title) except +
        # modal
        Widget* buttonPanel() except +
        void dispose() except +
        void center() except +

    cdef cppclass Button(Widget):
        Button(Widget *parent)
        Button(Widget *parent, const string &caption)
        Button(Widget *parent, const string &caption, int icon)
        void setCallback(const function[void()] &callback)

    cdef cppclass FormHelper:
        FormHelper(Screen*) except +
        Window* addWindow(const Vector2i& pos, const string& title) except +

        #FormWidget[T] addVariable[T](const string& label, T& value) except +
        #FormWidget[T] addVariable[T](const string& label, T& value, bint editable) except +

        void addGroup(const string&) except +
        Button* addButton(const string&, const function[void()]) except +
        void setWindow(Window* window) except +
        Window* window() except +
        void refresh() except +

