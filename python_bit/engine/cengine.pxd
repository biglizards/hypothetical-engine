cdef extern from "../../engine/engine.h":
    ctypedef char* (*file_load_func)(const char*)

    ctypedef struct GLFWwindow:
        pass

    GLFWwindow* create_window(int width, int height, const char* name)
    unsigned int load_shader(const char* shaderSource, unsigned int shaderType)

    void glfwDestroyWindow(GLFWwindow* window)
    int demo(file_load_func)
