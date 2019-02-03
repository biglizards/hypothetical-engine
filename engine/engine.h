#ifndef ENGINE_H_INCLUDED
#define ENGINE_H_INCLUDED

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <nanogui/nanogui.h>

typedef char* (*file_load_func)(const char* path);

GLFWwindow* create_window(int width, int height, const char* name);
GLuint load_shader(const char* shaderSource, GLenum shaderType);

void set_callbacks(nanogui::Screen* screen, GLFWwindow* window);


template <typename T>
using setterFunc = void(*)(const T&, uintptr_t PyWidget);
template <typename T>
using getterFunc = T(*)(uintptr_t PyWidget);

template <typename T>
nanogui::detail::FormWidget<T>* add_variable(nanogui::FormHelper* helper, const char* name,
                                             setterFunc<T> setter, getterFunc<T> getter, uintptr_t PyWidget)
{
    return helper->addVariable<T>(name, [setter, PyWidget](const T& v) { setter(v, PyWidget); },
                                        [getter, PyWidget]() -> T { return getter(PyWidget); }
                                 );
}

nanogui::Button* add_button_(nanogui::FormHelper* helper, const char* name, void* self, void(*callback)(void* self));
void setButtonCallback(nanogui::Button* button, void* self, void(*callback)(void* self));

#endif // ENGINE_H_INCLUDED
