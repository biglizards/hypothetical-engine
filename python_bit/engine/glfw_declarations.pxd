cdef extern from *:
    ctypedef struct GLFWwindow:
        pass
    ctypedef struct GLFWmonitor:
        pass
    ctypedef void (*GLFWglproc)()

    void glfwSwapBuffers(GLFWwindow* window)
    void glfwPollEvents()
    int glfwWindowShouldClose(GLFWwindow* window)

    void glfwInit()
    double glfwGetTime()
    void glfwWindowHint(int hint, int value)
    GLFWwindow* glfwCreateWindow(int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share)
    void glfwMakeContextCurrent(GLFWwindow* window)

    GLFWglproc glfwGetProcAddress(const char* procname)

    # constants
    unsigned int GLFW_CONTEXT_VERSION_MAJOR
    unsigned int GLFW_CONTEXT_VERSION_MINOR
    unsigned int GLFW_OPENGL_PROFILE
    unsigned int GLFW_OPENGL_CORE_PROFILE
    unsigned int GLFW_SAMPLES
