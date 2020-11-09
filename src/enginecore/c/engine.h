#ifndef ENGINE_H_INCLUDED
#define ENGINE_H_INCLUDED

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <nanogui/nanogui.h>

typedef char* (*file_load_func)(const char* path);

GLFWwindow* create_window(int width, int height, const char* name);
GLuint load_shader(const char* shaderSource, GLenum shaderType);

void set_callbacks(nanogui::Screen* screen, GLFWwindow* window);


// the NanoGUI helper allows you to add arbitrary variables to a UI
// this function is called in helper.pxi to do so
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

// set callback on types that support callbacks (eg TestBox, FloatBox). Should also support non-box types.
template <typename BoxType, typename T, typename R=bool>
void setMetaCallback(BoxType* box, void* self, R(*callback)(void* self, T value))
{
    box->setCallback([callback, self](T value) {return callback(self, value);});
}


nanogui::Button* add_button_(nanogui::FormHelper* helper, const char* name, void* self, void(*callback)(void* self));
void setButtonCallback(nanogui::Button* button, void* self, void(*callback)(void* self));
void setTextBoxCallback(nanogui::TextBox* textBox, void* self, bool(*callback)(void* self, const std::string& str));

// there is no callback for a key being pressed in a text box, so we make one ourselves.
class CustomTextBox : public nanogui::TextBox {
    public:
        CustomTextBox(nanogui::Widget* parent, const std::string &value = "Untitled")
            : nanogui::TextBox(parent, value) {}
        void setKeyCallback(const std::function<bool(const std::string& str)> &callback) {
            keyCallback = callback;
        }
        virtual bool keyboardEvent(int key, int scancode, int action, int modifiers) {
            bool rv = nanogui::TextBox::keyboardEvent(key, scancode, action, modifiers);
            if (keyCallback)
                keyCallback(mValueTemp);
            return rv;
        }
    private:
        std::function<bool(const std::string &str)> keyCallback;
};

void setTextBoxKeyCallback(CustomTextBox* textBox, void* self, bool(*callback)(void* self, const std::string& str));


#endif // ENGINE_H_INCLUDED
