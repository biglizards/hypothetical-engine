from libcpp.string cimport string
from libcpp.functional cimport function
from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "nanogui/nanogui.h" namespace "nanogui::detail":
    cpdef cppclass FormWidget[T]:
        T value() except +
        void setItems(const vector[string]& items) except +

cdef extern from "nanogui/nanogui.h" namespace "nanogui":
    ctypedef struct GLFWwindow:
        pass

    cdef cppclass Vector2i:
        Vector2i(int, int) except +

    cdef cppclass Widget:
        bint focused() except +
        pass

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
        pass

    cdef cppclass Button(Widget):
        pass

    cdef cppclass FormHelper:
        FormHelper(Screen*) except +
        Window* addWindow(const Vector2i& pos, const string& title) except +

        #FormWidget[T] addVariable[T](const string& label, T& value) except +
        #FormWidget[T] addVariable[T](const string& label, T& value, bint editable) except +

        void addGroup(const string&) except +
        Button* addButton(const string&, const function[void()])

