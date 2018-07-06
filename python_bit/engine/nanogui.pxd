from libcpp.string cimport string

cdef extern from "nanogui/nanogui.h" namespace "nanogui":
    ctypedef struct GLFWwindow:
        pass

    cdef cppclass Vector2i:
        Vector2i(int, int) except +

    cdef cppclass Widget:
        pass

    cdef cppclass Screen(Widget):
        Screen() except +
        void initialize(GLFWwindow *window, bint shutdownGLFWOnDestruct) except +
        void setVisible(bint) except +
        void performLayout() except +
        void drawContents() except +
        void drawWidgets() except +
        double mLastInteraction

    cpdef cppclass Window(Widget):
        pass

    cdef cppclass FormHelper:
        FormHelper(Screen*) except +
        Window* addWindow(const Vector2i& pos, const string& title) except +


