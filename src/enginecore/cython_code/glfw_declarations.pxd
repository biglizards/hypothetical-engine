cdef extern from *:
    ctypedef struct GLFWwindow:
        pass
    ctypedef struct GLFWmonitor:
        pass
    ctypedef void (*GLFWglproc)()

    # callback function types
    ctypedef void(* GLFWcharfun) (GLFWwindow *, unsigned int codepoint)
    ctypedef void(* GLFWcursorenterfun) (GLFWwindow *, int)
    ctypedef void(* GLFWcursorposfun) (GLFWwindow *, double, double)
    ctypedef void(* GLFWdropfun) (GLFWwindow *, int, const char **)
    ctypedef void(* GLFWkeyfun) (GLFWwindow* window, int key, int scancode, int action, int mods)
    ctypedef void(* GLFWmousebuttonfun) (GLFWwindow* , int, int, int)
    ctypedef void(* GLFWscrollfun) (GLFWwindow *, double, double)
    ctypedef void(* GLFWframebuffersizefun) (GLFWwindow* window, int width, int height)

    void glfwSwapBuffers(GLFWwindow* window)
    void glfwPollEvents()
    int glfwWindowShouldClose(GLFWwindow* window)
    void glfwSetWindowShouldClose(GLFWwindow* window, int value)

    void glfwInit()
    double glfwGetTime()
    void glfwWindowHint(int hint, int value)
    GLFWwindow* glfwCreateWindow(int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share)
    void glfwMakeContextCurrent(GLFWwindow* window)

    GLFWglproc glfwGetProcAddress(const char* procname)

    int glfwGetKey(GLFWwindow* window, int key)
    void glfwGetCursorPos(GLFWwindow* window, double* xpos, double* ypos)
    void glfwGetWindowSize(GLFWwindow* window, int* width, int* height)
    void glfwSetWindowSize(GLFWwindow* window, int width, int height)

    void glfwSetInputMode(GLFWwindow* window, int mode, int value)
    int glfwGetInputMode(GLFWwindow* window, int mode)

    # callback functions
    GLFWcharfun glfwSetCharCallback(GLFWwindow* window, GLFWcharfun cbfun)
    GLFWcursorenterfun glfwSetCursorEnterCallback(GLFWwindow* window, GLFWcursorenterfun cbfun)
    GLFWcursorposfun glfwSetCursorPosCallback(GLFWwindow* window, GLFWcursorposfun cbfun)
    GLFWdropfun glfwSetDropCallback(GLFWwindow* window, GLFWdropfun cbfun)
    GLFWkeyfun glfwSetKeyCallback(GLFWwindow* window, GLFWkeyfun cbfun)
    GLFWmousebuttonfun glfwSetMouseButtonCallback(GLFWwindow* window, GLFWmousebuttonfun cbfun)
    GLFWscrollfun glfwSetScrollCallback(GLFWwindow* window, GLFWscrollfun cbfun)
    GLFWframebuffersizefun glfwSetFramebufferSizeCallback(GLFWwindow* window, GLFWframebuffersizefun cbfun)

    # constants
    unsigned int GLFW_CONTEXT_VERSION_MAJOR
    unsigned int GLFW_CONTEXT_VERSION_MINOR
    unsigned int GLFW_OPENGL_PROFILE
    unsigned int GLFW_OPENGL_CORE_PROFILE
    unsigned int GLFW_SAMPLES
    unsigned int GLFW_PRESS
    unsigned int GLFW_RELEASE
    unsigned int GLFW_CURSOR, GLFW_CURSOR_NORMAL, GLFW_CURSOR_HIDDEN, GLFW_CURSOR_DISABLED

    # keyboard keys (this is the last section)
    int GLFW_KEY_SPACE
    int GLFW_KEY_APOSTROPHE
    int GLFW_KEY_COMMA
    int GLFW_KEY_MINUS
    int GLFW_KEY_PERIOD
    int GLFW_KEY_SLASH
    int GLFW_KEY_0
    int GLFW_KEY_1
    int GLFW_KEY_2
    int GLFW_KEY_3
    int GLFW_KEY_4
    int GLFW_KEY_5
    int GLFW_KEY_6
    int GLFW_KEY_7
    int GLFW_KEY_8
    int GLFW_KEY_9
    int GLFW_KEY_SEMICOLON
    int GLFW_KEY_EQUAL
    int GLFW_KEY_A
    int GLFW_KEY_B
    int GLFW_KEY_C
    int GLFW_KEY_D
    int GLFW_KEY_E
    int GLFW_KEY_F
    int GLFW_KEY_G
    int GLFW_KEY_H
    int GLFW_KEY_I
    int GLFW_KEY_J
    int GLFW_KEY_K
    int GLFW_KEY_L
    int GLFW_KEY_M
    int GLFW_KEY_N
    int GLFW_KEY_O
    int GLFW_KEY_P
    int GLFW_KEY_Q
    int GLFW_KEY_R
    int GLFW_KEY_S
    int GLFW_KEY_T
    int GLFW_KEY_U
    int GLFW_KEY_V
    int GLFW_KEY_W
    int GLFW_KEY_X
    int GLFW_KEY_Y
    int GLFW_KEY_Z
    int GLFW_KEY_LEFT_BRACKET
    int GLFW_KEY_BACKSLASH
    int GLFW_KEY_RIGHT_BRACKET
    int GLFW_KEY_GRAVE_ACCENT
    int GLFW_KEY_WORLD_1
    int GLFW_KEY_WORLD_2

    # Function keys (by last section i meant last section that isnt just keys)
    int GLFW_KEY_ESCAPE
    int GLFW_KEY_ENTER
    int GLFW_KEY_TAB
    int GLFW_KEY_BACKSPACE
    int GLFW_KEY_INSERT
    int GLFW_KEY_DELETE
    int GLFW_KEY_RIGHT
    int GLFW_KEY_LEFT
    int GLFW_KEY_DOWN
    int GLFW_KEY_UP
    int GLFW_KEY_PAGE_UP
    int GLFW_KEY_PAGE_DOWN
    int GLFW_KEY_HOME
    int GLFW_KEY_END
    int GLFW_KEY_CAPS_LOCK
    int GLFW_KEY_SCROLL_LOCK
    int GLFW_KEY_NUM_LOCK
    int GLFW_KEY_PRINT_SCREEN
    int GLFW_KEY_PAUSE
    int GLFW_KEY_F1
    int GLFW_KEY_F2
    int GLFW_KEY_F3
    int GLFW_KEY_F4
    int GLFW_KEY_F5
    int GLFW_KEY_F6
    int GLFW_KEY_F7
    int GLFW_KEY_F8
    int GLFW_KEY_F9
    int GLFW_KEY_F10
    int GLFW_KEY_F11
    int GLFW_KEY_F12
    int GLFW_KEY_F13
    int GLFW_KEY_F14
    int GLFW_KEY_F15
    int GLFW_KEY_F16
    int GLFW_KEY_F17
    int GLFW_KEY_F18
    int GLFW_KEY_F19
    int GLFW_KEY_F20
    int GLFW_KEY_F21
    int GLFW_KEY_F22
    int GLFW_KEY_F23
    int GLFW_KEY_F24
    int GLFW_KEY_F25
    int GLFW_KEY_KP_0
    int GLFW_KEY_KP_1
    int GLFW_KEY_KP_2
    int GLFW_KEY_KP_3
    int GLFW_KEY_KP_4
    int GLFW_KEY_KP_5
    int GLFW_KEY_KP_6
    int GLFW_KEY_KP_7
    int GLFW_KEY_KP_8
    int GLFW_KEY_KP_9
    int GLFW_KEY_KP_DECIMAL
    int GLFW_KEY_KP_DIVIDE
    int GLFW_KEY_KP_MULTIPLY
    int GLFW_KEY_KP_SUBTRACT
    int GLFW_KEY_KP_ADD
    int GLFW_KEY_KP_ENTER
    int GLFW_KEY_KP_EQUAL
    int GLFW_KEY_LEFT_SHIFT
    int GLFW_KEY_LEFT_CONTROL
    int GLFW_KEY_LEFT_ALT
    int GLFW_KEY_LEFT_SUPER
    int GLFW_KEY_RIGHT_SHIFT
    int GLFW_KEY_RIGHT_CONTROL
    int GLFW_KEY_RIGHT_ALT
    int GLFW_KEY_RIGHT_SUPER
    int GLFW_KEY_MENU

    int GLFW_MOUSE_BUTTON_1
    int GLFW_MOUSE_BUTTON_2
    int GLFW_MOUSE_BUTTON_3
    int GLFW_MOUSE_BUTTON_4
    int GLFW_MOUSE_BUTTON_5
    int GLFW_MOUSE_BUTTON_6
    int GLFW_MOUSE_BUTTON_7
    int GLFW_MOUSE_BUTTON_8
    int GLFW_MOUSE_BUTTON_LAST
    int GLFW_MOUSE_BUTTON_LEFT
    int GLFW_MOUSE_BUTTON_MIDDLE
    int GLFW_MOUSE_BUTTON_RIGHT

# make sure all the constants are also available in python

KEY_SPACE = GLFW_KEY_SPACE
KEY_APOSTROPHE = GLFW_KEY_APOSTROPHE
KEY_COMMA = GLFW_KEY_COMMA
KEY_MINUS = GLFW_KEY_MINUS
KEY_PERIOD = GLFW_KEY_PERIOD
KEY_SLASH = GLFW_KEY_SLASH
KEY_0 = GLFW_KEY_0
KEY_1 = GLFW_KEY_1
KEY_2 = GLFW_KEY_2
KEY_3 = GLFW_KEY_3
KEY_4 = GLFW_KEY_4
KEY_5 = GLFW_KEY_5
KEY_6 = GLFW_KEY_6
KEY_7 = GLFW_KEY_7
KEY_8 = GLFW_KEY_8
KEY_9 = GLFW_KEY_9
KEY_SEMICOLON = GLFW_KEY_SEMICOLON
KEY_EQUAL = GLFW_KEY_EQUAL
KEY_A = GLFW_KEY_A
KEY_B = GLFW_KEY_B
KEY_C = GLFW_KEY_C
KEY_D = GLFW_KEY_D
KEY_E = GLFW_KEY_E
KEY_F = GLFW_KEY_F
KEY_G = GLFW_KEY_G
KEY_H = GLFW_KEY_H
KEY_I = GLFW_KEY_I
KEY_J = GLFW_KEY_J
KEY_K = GLFW_KEY_K
KEY_L = GLFW_KEY_L
KEY_M = GLFW_KEY_M
KEY_N = GLFW_KEY_N
KEY_O = GLFW_KEY_O
KEY_P = GLFW_KEY_P
KEY_Q = GLFW_KEY_Q
KEY_R = GLFW_KEY_R
KEY_S = GLFW_KEY_S
KEY_T = GLFW_KEY_T
KEY_U = GLFW_KEY_U
KEY_V = GLFW_KEY_V
KEY_W = GLFW_KEY_W
KEY_X = GLFW_KEY_X
KEY_Y = GLFW_KEY_Y
KEY_Z = GLFW_KEY_Z
KEY_LEFT_BRACKET = GLFW_KEY_LEFT_BRACKET
KEY_BACKSLASH = GLFW_KEY_BACKSLASH
KEY_RIGHT_BRACKET = GLFW_KEY_RIGHT_BRACKET
KEY_GRAVE_ACCENT = GLFW_KEY_GRAVE_ACCENT
KEY_WORLD_1 = GLFW_KEY_WORLD_1
KEY_WORLD_2 = GLFW_KEY_WORLD_2
KEY_ESCAPE = GLFW_KEY_ESCAPE
KEY_ENTER = GLFW_KEY_ENTER
KEY_TAB = GLFW_KEY_TAB
KEY_BACKSPACE = GLFW_KEY_BACKSPACE
KEY_INSERT = GLFW_KEY_INSERT
KEY_DELETE = GLFW_KEY_DELETE
KEY_RIGHT = GLFW_KEY_RIGHT
KEY_LEFT = GLFW_KEY_LEFT
KEY_DOWN = GLFW_KEY_DOWN
KEY_UP = GLFW_KEY_UP
KEY_PAGE_UP = GLFW_KEY_PAGE_UP
KEY_PAGE_DOWN = GLFW_KEY_PAGE_DOWN
KEY_HOME = GLFW_KEY_HOME
KEY_END = GLFW_KEY_END
KEY_CAPS_LOCK = GLFW_KEY_CAPS_LOCK
KEY_SCROLL_LOCK = GLFW_KEY_SCROLL_LOCK
KEY_NUM_LOCK = GLFW_KEY_NUM_LOCK
KEY_PRINT_SCREEN = GLFW_KEY_PRINT_SCREEN
KEY_PAUSE = GLFW_KEY_PAUSE
KEY_F1 = GLFW_KEY_F1
KEY_F2 = GLFW_KEY_F2
KEY_F3 = GLFW_KEY_F3
KEY_F4 = GLFW_KEY_F4
KEY_F5 = GLFW_KEY_F5
KEY_F6 = GLFW_KEY_F6
KEY_F7 = GLFW_KEY_F7
KEY_F8 = GLFW_KEY_F8
KEY_F9 = GLFW_KEY_F9
KEY_F10 = GLFW_KEY_F10
KEY_F11 = GLFW_KEY_F11
KEY_F12 = GLFW_KEY_F12
KEY_F13 = GLFW_KEY_F13
KEY_F14 = GLFW_KEY_F14
KEY_F15 = GLFW_KEY_F15
KEY_F16 = GLFW_KEY_F16
KEY_F17 = GLFW_KEY_F17
KEY_F18 = GLFW_KEY_F18
KEY_F19 = GLFW_KEY_F19
KEY_F20 = GLFW_KEY_F20
KEY_F21 = GLFW_KEY_F21
KEY_F22 = GLFW_KEY_F22
KEY_F23 = GLFW_KEY_F23
KEY_F24 = GLFW_KEY_F24
KEY_F25 = GLFW_KEY_F25
KEY_KP_0 = GLFW_KEY_KP_0
KEY_KP_1 = GLFW_KEY_KP_1
KEY_KP_2 = GLFW_KEY_KP_2
KEY_KP_3 = GLFW_KEY_KP_3
KEY_KP_4 = GLFW_KEY_KP_4
KEY_KP_5 = GLFW_KEY_KP_5
KEY_KP_6 = GLFW_KEY_KP_6
KEY_KP_7 = GLFW_KEY_KP_7
KEY_KP_8 = GLFW_KEY_KP_8
KEY_KP_9 = GLFW_KEY_KP_9
KEY_KP_DECIMAL = GLFW_KEY_KP_DECIMAL
KEY_KP_DIVIDE = GLFW_KEY_KP_DIVIDE
KEY_KP_MULTIPLY = GLFW_KEY_KP_MULTIPLY
KEY_KP_SUBTRACT = GLFW_KEY_KP_SUBTRACT
KEY_KP_ADD = GLFW_KEY_KP_ADD
KEY_KP_ENTER = GLFW_KEY_KP_ENTER
KEY_KP_EQUAL = GLFW_KEY_KP_EQUAL
KEY_LEFT_SHIFT = GLFW_KEY_LEFT_SHIFT
KEY_LEFT_CONTROL = GLFW_KEY_LEFT_CONTROL
KEY_LEFT_ALT = GLFW_KEY_LEFT_ALT
KEY_LEFT_SUPER = GLFW_KEY_LEFT_SUPER
KEY_RIGHT_SHIFT = GLFW_KEY_RIGHT_SHIFT
KEY_RIGHT_CONTROL = GLFW_KEY_RIGHT_CONTROL
KEY_RIGHT_ALT = GLFW_KEY_RIGHT_ALT
KEY_RIGHT_SUPER = GLFW_KEY_RIGHT_SUPER
KEY_MENU = GLFW_KEY_MENU

KEY_PRESS = GLFW_PRESS
KEY_RELEASE = GLFW_RELEASE

MOUSE_PRESS = GLFW_PRESS  # yes i know its the same as KEY_PRESS but gotta get that consistency
MOUSE_CLICK = GLFW_PRESS
MOUSE_DOWN = GLFW_PRESS
MOUSE_RELEASE = GLFW_RELEASE
MOUSE_UNCLICK = GLFW_RELEASE
MOUSE_UP = GLFW_RELEASE
MOUSE_1 = GLFW_MOUSE_BUTTON_1
MOUSE_2 = GLFW_MOUSE_BUTTON_2
MOUSE_3 = GLFW_MOUSE_BUTTON_3
MOUSE_4 = GLFW_MOUSE_BUTTON_4
MOUSE_5 = GLFW_MOUSE_BUTTON_5
MOUSE_6 = GLFW_MOUSE_BUTTON_6
MOUSE_7 = GLFW_MOUSE_BUTTON_7
MOUSE_8 = GLFW_MOUSE_BUTTON_8
MOUSE_LEFT = GLFW_MOUSE_BUTTON_LEFT
MOUSE_MIDDLE = GLFW_MOUSE_BUTTON_MIDDLE
MOUSE_RIGHT = GLFW_MOUSE_BUTTON_RIGHT

