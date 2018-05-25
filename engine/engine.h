#ifndef ENGINE_H_INCLUDED
#define ENGINE_H_INCLUDED

#include <glad/glad.h>
#include <GLFW/glfw3.h>

typedef int (*func)(int, int, void*f);

int add_two_ints(int, int);
int call_func(func some_func, int a, int b, void* f);
GLFWwindow* create_window(int width, int height, const char* name);

#endif // ENGINE_H_INCLUDED
