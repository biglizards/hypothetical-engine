cdef extern from "glad/glad.h":
    # force glad to be loaded first (before nanogui tries to load GLFW)
    pass

from nanogui cimport FormHelper, FormWidget, Button, TextBox, FloatBox
from libc.stdint cimport uintptr_t
from libcpp.string cimport string
from libcpp cimport bool

cdef extern from * namespace "nanogui":
    cdef cppclass Screen:
        pass

cdef extern from "../c/engine.h":
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

    void setButtonCallback(Button* button, void* self, void(*callback)(void* self))
    void setTextBoxCallback(TextBox* textBox, void* self, bool(*callback)(void* self, const string& _str)) except +
    void setFloatBoxCallback[T](FloatBox[T]* floatBox, void* self, bool(*callback)(void* self, T value))
    void setMetaCallback[T, U, R](T* box, void* self, R(*callback)(void* self, U value))
