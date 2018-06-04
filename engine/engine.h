#ifndef ENGINE_H_INCLUDED
#define ENGINE_H_INCLUDED
//ri there
#include <glad/glad.h>
#include <GLFW/glfw3.h>

typedef char* (*file_load_func)(const char* path);

GLFWwindow* create_window(int width, int height, const char* name);
GLuint load_shader(const char* shaderSource, GLenum shaderType);

int demo(file_load_func);
#endif // ENGINE_H_INCLUDED
