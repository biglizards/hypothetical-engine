cdef extern from "glad/glad.h":
    # force glad to be loaded first (before nanogui tries to load GLFW)
    pass

from nanogui cimport FormHelper, FormWidget, Button
from libc.stdint cimport uintptr_t

cdef extern from * namespace "nanogui":
    cdef cppclass Screen:
        pass

cdef extern from "../../engine/engine.h":
    ctypedef char* (*file_load_func)(const char*)

    ctypedef struct GLFWwindow:
        pass

    GLFWwindow* create_window(int width, int height, const char* name)
    unsigned int load_shader(const char* shaderSource, unsigned int shaderType)

    void glfwDestroyWindow(GLFWwindow* window) except +
    void set_callbacks(Screen* screen, GLFWwindow* window) except +

    # void addVariable[T](FormHelper* helper, void(*setter)(const T&), T(*getterFunc)())
    FormWidget[T]* add_variable[T](FormHelper* helper, const char* name,
                                   void(*setter)(const T&, uintptr_t), T(*getterFunc)(uintptr_t), uintptr_t)
    Button* add_button_(FormHelper* helper, const char* name, void* self, void(*callback)(void* self))
