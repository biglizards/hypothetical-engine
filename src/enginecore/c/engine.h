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

template <typename Scalar>
void setFloatBoxCallback(nanogui::FloatBox<Scalar>* floatBox, void* self, bool(*callback)(void* self, Scalar value))
{
    floatBox->setCallback([callback, self](Scalar value) {return callback(self, value);});
}

template <typename BoxType, typename T, typename R=bool>
void setMetaCallback(BoxType* box, void* self, R(*callback)(void* self, T value))
{
    box->setCallback([callback, self](T value) {return callback(self, value);});
}


nanogui::Button* add_button_(nanogui::FormHelper* helper, const char* name, void* self, void(*callback)(void* self));
void setButtonCallback(nanogui::Button* button, void* self, void(*callback)(void* self));
void setTextBoxCallback(nanogui::TextBox* textBox, void* self, bool(*callback)(void* self, const std::string& str));


#endif // ENGINE_H_INCLUDED