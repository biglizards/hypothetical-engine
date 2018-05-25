#include "engine.h"

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <time.h>

#include <iostream>
#include <fstream>
#include <string>

int add_two_ints(int a, int b)
{
    return a+b+9;
}

int call_func(func some_func, int a, int b, void* f)
{
    std::cout << "pointless c++" << std::endl;
    return some_func(a, b, f);
}

const char* load_shader_file(const char* path)
{
    std::string shaderSourceString;

    std::ifstream shaderFile;
    shaderFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);  // raise exception on failure

    shaderFile.open(path);
    shaderFile >> shaderSourceString;  // load source from file

    return shaderSourceString.c_str();

}

GLuint load_shader(const char* path, GLenum shaderType)
{
    const char* shaderSource;
    try
    {
        std::string shaderSourceString;

        std::ifstream shaderFile;
        shaderFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);  // raise exception on failure

        shaderFile.open(path);
        shaderFile >> shaderSourceString;  // load source from file

        shaderSource = shaderSourceString.c_str();
    }
    catch (std::basic_ios::clear &e)
    {
        std::cerr << "SHADER ERROR: FAILED TO OPEN FILE \"" << path
                  << "\n ERROR CODE: " << e.what() << std::endl;
        return -1;
    }

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

        char errorLog[maxLength];
        glGetShaderInfoLog(shaderObject, maxLength, &maxLength, &errorLog[0]);

        std::cerr << "SHADER ERROR: FAILED TO COMPILE: " << errorLog << std::endl;

        glDeleteShader(shaderObject);
        return -1;
    }

    return shaderObject;

}

GLFWwindow* create_window(int width, int height, const char* name)
{
    glfwInit();
    //glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    //glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    //glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
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

int main()
{
    GLFWwindow* window = create_window(800, 600, "mr window");
    clock_t start_time = clock();
    int i = 0;

    const char* shaderSource = "#version 330 core\n"
                               "layout (location = 0) in vec3 aPos;\n"
                               "void main()\n"
                               "{\n"
                               "   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n"
                               "}\0";

    auto fragSource = "#version 330 core\n"
                      "out vec4 FragColor;\n"
                      "void main()\n"
                      "{\n"
                      "   FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);\n"
                      "}\n\0";

    GLuint vertexShader = load_shader("shaders/basic.vert", GL_VERTEX_SHADER);
    /*
    vertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader, 1, &shaderSource, nullptr);
    glCompileShader(vertexShader);

    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);

    if(!success)
    {
        glGetShaderInfoLog(vertexShader, 512, NULL, infoLog);
        std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
    } */

    unsigned int fragmentShader;
    fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader, 1, &fragSource, nullptr);
    glCompileShader(fragmentShader);

    int  success;
    char infoLog[512];


    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);

    if(!success)
    {
        glGetShaderInfoLog(vertexShader, 512, NULL, infoLog);
        std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
    }

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

        if (++i == 16384)
        {
            float total_time = (float)(clock() - start_time) / CLOCKS_PER_SEC;
            std::cout << total_time << " " << 16384/total_time << " fps\n";
            start_time = clock();
            i = 0;
        }

    }
}
