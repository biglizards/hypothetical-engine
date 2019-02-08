#include "engine.h"

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <time.h>

#include <nanogui/nanogui.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

#include <assimp/Importer.hpp>
#include <assimp/scene.h>
#include <assimp/postprocess.h>

nanogui::Screen* gl_screen = NULL;

void setTextBoxCallback(nanogui::TextBox* textBox, void* self, bool(*callback)(void* self, const std::string& str))
{
    textBox->setCallback([callback, self](const std::string& str) {return callback(self, str);});
}


nanogui::Button* add_button_(nanogui::FormHelper* helper, const char* name, void* self, void(*callback)(void* self))
{
    return helper->addButton(name, [callback, self]() {callback(self);});
}

void setButtonCallback(nanogui::Button* button, void* self, void(*callback)(void* self)) {
    button->setCallback([callback, self]() {callback(self);});
}

void framebuffer_size_callback(GLFWwindow*, int width, int height)
{
    glViewport(0, 0, width, height);
}

const char* load_shader_file(const char* path)
{
    std::string shaderSourceString;

    std::ifstream shaderFile;
    shaderFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);  // raise exception on failure

    shaderFile.open(path);
    std::stringstream buffer;
    buffer << shaderFile.rdbuf();

    return buffer.str().c_str();
}

void set_callbacks(nanogui::Screen* screen_, GLFWwindow* window)
{
    gl_screen = screen_;
    glfwSetCursorPosCallback(window,
        [](GLFWwindow *, double x, double y) {
            gl_screen->cursorPosCallbackEvent(x, y);
        }
    );

    glfwSetMouseButtonCallback(window,
        [](GLFWwindow *, int button, int action, int modifiers) {
            gl_screen->mouseButtonCallbackEvent(button, action, modifiers);
        }
    );

    glfwSetKeyCallback(window,
        [](GLFWwindow *, int key, int scancode, int action, int mods) {
            gl_screen->keyCallbackEvent(key, scancode, action, mods);
        }
    );

    glfwSetCharCallback(window,
        [](GLFWwindow *, unsigned int codepoint) {
            gl_screen->charCallbackEvent(codepoint);
        }
    );

    glfwSetDropCallback(window,
        [](GLFWwindow *, int count, const char **filenames) {
            gl_screen->dropCallbackEvent(count, filenames);
        }
    );

    glfwSetScrollCallback(window,
        [](GLFWwindow *, double x, double y) {
            gl_screen->scrollCallbackEvent(x, y);
       }
    );

    //glfwSetFramebufferSizeCallback(window,
    //    [](GLFWwindow *, int width, int height) {
    //        gl_screen->resizeCallbackEvent(width, height);
    //    }
    //);
}

GLuint load_shader(const char* shaderSource, GLenum shaderType)
{
    GLuint shaderObject = glCreateShader(shaderType);
    glShaderSource(shaderObject, 1, &shaderSource, nullptr);
    glCompileShader(shaderObject);

    // error handling
    GLint success = 0;
    glGetShaderiv(shaderObject, GL_COMPILE_STATUS, &success);

    if (success == GL_FALSE)
    {
        GLint maxLength = 0;
        glGetShaderiv(shaderObject, GL_INFO_LOG_LENGTH, &maxLength);
        if (1024 < maxLength)
            std::cerr << "META-ERROR: the following error message was too long to be fully printed:\n";

        char errorLog[1024];
        glGetShaderInfoLog(shaderObject, 1024, nullptr, &errorLog[0]);

        std::cerr << "SHADER ERROR: FAILED TO COMPILE: " << errorLog << std::endl;

        glDeleteShader(shaderObject);
        return -1;
    }

    return shaderObject;

}

GLFWwindow* create_window(int width, int height, const char* name)
{
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    GLFWwindow* window = glfwCreateWindow(width, height, name, NULL, NULL);

    if (window == nullptr)
    {
        std::cerr << "Could not create window" << std::endl;
        return nullptr;
    }

    glfwMakeContextCurrent(window);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "could not initialize GLAD" << std::endl;
        return nullptr;
    }


    return window;
}