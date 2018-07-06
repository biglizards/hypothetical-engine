#include "engine.h"

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <time.h>

#include <nanogui/nanogui.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

nanogui::Screen* gl_screen = NULL;

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

    glfwSetFramebufferSizeCallback(window,
        [](GLFWwindow *, int width, int height) {
            gl_screen->resizeCallbackEvent(width, height);
        }
    );
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
            std::cerr << "META-ERROR: the following error message was too long to be printed:\n";

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

int demo(file_load_func foo)
{
    GLFWwindow* window = create_window(800, 600, "mr window");
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
    clock_t start_time = clock();
    int i = 0;

    char* shaderSource;
    shaderSource = foo("shaders/basic.frag");
    GLuint fragmentShader = load_shader(shaderSource, GL_FRAGMENT_SHADER);

    shaderSource = foo("shaders/basic.vert");
    GLuint vertexShader = load_shader(shaderSource, GL_VERTEX_SHADER);

    unsigned int shaderProgram;
    shaderProgram = glCreateProgram();
    glAttachShader(shaderProgram, vertexShader);
    glAttachShader(shaderProgram, fragmentShader);
    glLinkProgram(shaderProgram);
    // and here

    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);

    glUseProgram(shaderProgram);

    float vertices[] =
    {
        -0.5f, -0.5f, 0.0f,
        0.5f, -0.5f, 0.0f,
        0.0f,  0.5f, 0.0f
    };

    // create a vao
    unsigned int VAO;
    glGenVertexArrays(1, &VAO);

    // create a vbo to go inside our vao
    unsigned int VBO;
    glGenBuffers(1, &VBO);

    // bind vao (need to do this first so it picks up the vbo)
    glBindVertexArray(VAO);

    // bind vbo (linking it to the vao) then buffer data to it
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // add format info
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    while(!glfwWindowShouldClose(window))
    {
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        glUseProgram(shaderProgram);
        glBindVertexArray(VAO);
        glDrawArrays(GL_TRIANGLES, 0, 3);

        glfwSwapBuffers(window);
        glfwPollEvents();

        if (++i > 16384)
        {
            float total_time = (float)(clock() - start_time) / CLOCKS_PER_SEC;
            std::cout << total_time << " " << 16384/total_time << " fps\n";
            start_time = clock();
            i = 0;
        }

    }
    return 0;
}
