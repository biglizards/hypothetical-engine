from libcpp.string cimport string

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

    cdef cppclass FormHelper:
        FormHelper(Screen*) except +
        Window* addWindow(const Vector2i& pos, const string& title) except +


