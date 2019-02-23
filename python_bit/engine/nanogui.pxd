from libcpp.string cimport string
from libcpp cimport bool
from libcpp.functional cimport function
from libcpp.vector cimport vector
from libcpp.pair cimport pair

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

cdef extern from "nanogui/nanogui.h" namespace "nanogui::TextBox":
    cdef enum TextBoxAlignment "nanogui::TextBox::Alignment":
        Left,
        Center,
        Right

cdef extern from "nanogui/nanogui.h" namespace "nanogui::Popup":
    cdef enum PopupSide "nanogui::Popup::Side":
        PopupLeft "Left",
        PopupRight "Right",

cdef extern from "nanogui/nanogui.h" namespace "nanogui::ImagePanel":
    ctypedef vector[pair[int, string]] Images

cdef extern from "nanogui/nanogui.h" namespace "nanogui::AdvancedGridLayout":
    cdef cppclass Anchor:
        Anchor() except +
        Anchor(int x, int y, Alignment horiz, Alignment vert) except +
        Anchor(int x, int y, int w, int h, Alignment horiz, Alignment vert) except +

# yes i know this isnt nanogui stuff but they're basically the same shut up
cdef extern from "nanovg.h":
    ctypedef struct NVGcontext
    int nvgCreateImage(NVGcontext* ctx, const char* filename, int imageFlags)
    int nvgCreateImageMem(NVGcontext* ctx, int imageFlags, unsigned char* data, int ndata);


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

        int fontSize() except +
        void setFontSize(int fontSize) except +

        Widget *findWidget(const Vector2i &p)

    cdef cppclass Label(Widget):
        Label(Widget *parent, const string &caption) except +
        Label(Widget *parent, const string &caption, const string &font) except +
        Label(Widget *parent, const string &caption, const string &font, int fontSize) except +

    cdef cppclass TextBox(Widget):
        TextBox(Widget *parent) except +
        TextBox(Widget *parent, const string &value) except +
        bool editable() except +
        void setEditable(bool editable) except +
        bool spinnable() except +
        void setSpinnable(bool spinnable) except +
        const string &value() except +
        void setValue(const string &value) except +
        TextBoxAlignment alignment() except +
        void setAlignment(TextBoxAlignment align) except +
        const string &placeholder() except +
        void setPlaceholder(const string &placeholder) except +

    cdef cppclass FloatBox[T](TextBox):
        FloatBox(Widget *parent) except +
        FloatBox(Widget *parent, T value) except +
        T floatValue "value"() except +
        void setValue(const T) except +

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

    cdef cppclass AdvancedGridLayout(Layout):
        AdvancedGridLayout() except +
        AdvancedGridLayout(const vector[int] &cols) except +
        AdvancedGridLayout(const vector[int] &cols, const vector[int] &rows) except +
        AdvancedGridLayout(const vector[int] &cols, const vector[int] &rows, int margin) except +
        void setAnchor(const Widget *widget, const Anchor &anchor) except +
        int rowCount() except +
        void appendRow(int size) except +
        void appendRow(int size, float stretch) except +
        void appendCol(int size) except +
        void appendCol(int size, float stretch) except +

        void setMargin(int margin) except +
        void setColStretch(int index, float stretch) except +

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
        NVGcontext *nvgContext() except +

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

    cdef cppclass VScrollPanel(Widget):
         VScrollPanel(Widget *parent) except +
         float scroll() except +
         void setScroll(float scroll) except +

    cdef cppclass ImagePanel(Widget):
        ImagePanel(Widget *parent) except +
        void setImages(const Images &data) except +
        const Images &images() except +
        function[void(int)] callback() except +
        void setCallback(const function[void(int)] &callback) except +

    cdef cppclass PopupButton(Button):
        PopupButton(Widget *parent) except +
        PopupButton(Widget *parent, const string &caption) except +
        PopupButton(Widget *parent, const string &caption, int buttonIcon) except +
        Widget* popup() except +
        void setSide(PopupSide popupSide) except +
        PopupSide side() except +



    Images loadImageDirectory(NVGcontext *ctx, const string &path) except +

cdef extern from "nanogui/nanogui.h" namespace "nanogui::detail":
    cpdef cppclass FormWidget[T](Widget):
        T value() except +
        void setItems(const vector[string]& items) except +
