cdef extern from "../../engine/engine.h":
    ctypedef int (*func)(int, int, void*)
    int add_two_ints(int a, int b)
    int call_func(func callback, int a, int b, void *f)
    ctypedef struct GLFWwindow:
        pass


    GLFWwindow* create_window(int width, int height, const char* name)
    void glfwDestroyWindow(GLFWwindow* window)
