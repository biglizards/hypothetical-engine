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

// callbacks must be callable, but Cython can't easily create lambdas like this
void setTextBoxCallback(nanogui::TextBox* textBox, void* self, bool(*callback)(void* self, const std::string& str))
{
    textBox->setCallback([callback, self](const std::string& str) {return callback(self, str);});
}

void setTextBoxKeyCallback(CustomTextBox* textBox, void* self, bool(*callback)(void* self, const std::string& str))
{
    textBox->setKeyCallback([callback, self](const std::string& str) {return callback(self, str);});
}

nanogui::Button* add_button_(nanogui::FormHelper* helper, const char* name, void* self, void(*callback)(void* self))
{
    return helper->addButton(name, [callback, self]() {callback(self);});
}

void setButtonCallback(nanogui::Button* button, void* self, void(*callback)(void* self)) {
    button->setCallback([callback, self]() {callback(self);});
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