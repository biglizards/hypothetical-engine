import weakref

cursor_caputre_modes = {'normal': GLFW_CURSOR_NORMAL, 'hidden': GLFW_CURSOR_HIDDEN,
                        'disabled': GLFW_CURSOR_DISABLED}
inv_capture_modes = {v: k for k, v in cursor_caputre_modes.items()}

cdef GLFWwindow* create_window(int width, int height, const char* name):
    glfwInit()
    glfwWindowHint(GLFW_SAMPLES, 4)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    window = glfwCreateWindow(width, height, name, NULL, NULL)

    if window is NULL:
        print("ERROR: FAILED TO CREATE WINDOW")
        return NULL
    glfwMakeContextCurrent(window)

    if not gladLoadGLLoader(<GLADloadproc>glfwGetProcAddress):
        print("ERROR: FAILED TO INIT GLAD")

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    return window


cdef class Window:
    """
    The Window object wraps the GLFWWindow class, as well as functions taking GLFWWindow
    as arguments, like callbacks, swapping buffers, etc
    """
    cdef GLFWwindow* window

    # when the window no longer has any strong references (ie from user code), deallocate the window
    cdef object __weakref__

    # callbacks
    cdef public object cursor_pos_callback
    cdef public object mouse_button_callback
    cdef public object key_callback
    cdef public object char_callback
    cdef public object drop_file_callback
    cdef public object scroll_callback
    cdef public object resize_callback

    cdef public int width
    cdef public int height
    cdef public Gui gui
    cdef public bint handle_gui_callbacks

    def __cinit__(self, int width=800, int height=600, name='window boi', *args, **kwargs):
        byte_str = name.encode()
        cdef char* c_string = byte_str
        self.window = create_window(width, height, c_string)
        self.width = width
        self.height = height
        self.handle_gui_callbacks = True

        # set callbacks
        self.key_callback = None  # todo why is this here, either remove it or add all the others. dont be inconsistent
        window_objects_by_pointer[<uintptr_t>self.window] = weakref.ref(self)

        glfwSetCharCallback(self.window, char_callback)
        #glfwSetCursorEnterCallback(self.window, cursor_enter_callback)  # this doesnt exist yet
        glfwSetCursorPosCallback(self.window, cursor_pos_callback)
        glfwSetDropCallback(self.window, drop_file_callback)
        glfwSetKeyCallback(self.window, key_callback)
        glfwSetMouseButtonCallback(self.window, mouse_button_callback)
        glfwSetScrollCallback(self.window, scroll_callback)
        glfwSetFramebufferSizeCallback(self.window, resize_callback)

        # this shouldn't really be here - it modifies the global gl state, not the windows
        set_gl_enables()

        # create a gui object for the window
        self.gui = Gui(self)

    def __init__(self, int width=800, int height=600, name='window boi', *args, **kwargs):
        # included to force a valid signature
        pass

    def __dealloc__(self):
        cengine.glfwDestroyWindow(self.window)

    cpdef void swap_buffers(self):
        glfwSwapBuffers(self.window)

    cpdef void clear_colour(self, double a, double b, double c, double d):
        # this line is hella ugly, but i need to do this to prevent an error
        # just pretend the <float>s aren't there
        # also the loss of precision is fine since the values should only ever be between 0 and 1
        glClearColor(<float>a, <float>b, <float>c, <float>d)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cpdef void clear(self, int code):
        glClear(code)

    cpdef bint should_close(self):
        return glfwWindowShouldClose(self.window)

    cpdef bint is_pressed(self, key):
        return glfwGetKey(self.window, key) == GLFW_PRESS

    cpdef void close(self):
        glfwSetWindowShouldClose(self.window, True)

    cpdef void set_cursor_capture(self, mode: str):
        cdef unsigned int cursor_mode = cursor_caputre_modes[mode]
        glfwSetInputMode(self.window, GLFW_CURSOR, cursor_mode)

    @property
    def cursor_mode(self):
        cdef int mode = glfwGetInputMode(self.window, GLFW_CURSOR)
        return inv_capture_modes[mode]

    @property
    def cursor_location(self):
        cdef double x, y
        glfwGetCursorPos(self.window, &x, &y)
        return x, y

    @property
    def cursor_location_ndc(self):
        cdef double x, y
        glfwGetCursorPos(self.window, &x, &y)
        return ((x/self.width)-0.5)*2, ((y/self.height)-0.5)*-2

    cpdef read_pixel(self, int x, int y):
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)  # i have no idea why this is needed
        cdef unsigned char data[4]
        glReadPixels(x, y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, data)
        return data[0], data[1], data[2], data[3]

    cpdef bint gui_under_mouse(self):
        cdef int x, y
        x, y = self.cursor_location
        return self.gui.screen.findWidget(nanogui.Vector2i(x, y)) is not self.gui.screen

    cpdef void set_swap_interval(self, int interval):
        """a wrapper around glfwSwapInterval. Sets the number of screen updates between frames, aka vsync.
        set to 0 to disable"""
        glfwSwapInterval(interval)

    cpdef void set_vsync(self, bint status):
        """a more user friendly way to interact with glfwSwapInterval"""
        glfwSwapInterval(1 if status else 0)

# instead of creating a custom wrapper in c++ using lambdas (which i very well could, like
# in the nanogui wrapper), since every glfw function returns a pointer to the window, and there
# is a one to one correspondence between Window objects and GLFWWindows, I just store them
# in a dict instead - this saves having to write a custom wrapper for every callback function
# also of note -- there's very rarely any more than one (glfw) window object
window_objects_by_pointer = {}

#cdef void key_callback(GLFWwindow* window_ptr, int key, int scancode, int action, int mods):
#    cdef Window window = window_objects_by_pointer[<uintptr_t>window_ptr]
#    if window.key_callback is not None:
#        window.key_callback(window, key, scancode, action, mods)
#    else:  # default
#        window.gui.handle_key(key, scancode, action, mods)

cdef Window get_window(GLFWwindow* window_ptr):
    return window_objects_by_pointer[<uintptr_t>window_ptr]()

glfw_event_errors = []

def abstract_callback(Window window, object callback_func, object gui_callback_func, *args):
    if glfw_event_errors: return
    try:
        if window.handle_gui_callbacks or callback_func is None:
            gui_callback_func(*args)
        if callback_func is not None and not (window.handle_gui_callbacks and window.gui.focused()):
            callback_func(window, *args)
    except Exception as e:
        glfw_event_errors.append(e)

cdef void key_callback(GLFWwindow* window_ptr, int key, int scancode, int action, int mods):
    cdef Window window = get_window(window_ptr)
    abstract_callback(window, window.key_callback, window.gui.handle_key, key, scancode, action, mods)

cdef void char_callback(GLFWwindow* window_ptr, unsigned int codepoint):
    cdef Window window = get_window(window_ptr)
    abstract_callback(window, window.char_callback, window.gui.handle_char, codepoint)

cdef void cursor_pos_callback(GLFWwindow* window_ptr, double x, double y):
    cdef Window window = get_window(window_ptr)
    abstract_callback(window, window.cursor_pos_callback, window.gui.handle_cursor_pos, x, y)

cdef void drop_file_callback(GLFWwindow* window_ptr, int count, const char** filenames):
    # this one has different from default behavior - that is, if a file is dropped, always tell the user,
    # and call the gui unless the "i'll handle it manually" flag is set
    cdef Window window = get_window(window_ptr)
    try:
        if window.handle_gui_callbacks:
            window.gui.handle_drop(count, to_list(count, filenames))
        if window.drop_file_callback is not None:
            window.drop_file_callback(window, to_list(count, filenames))
    except Exception as e:
        glfw_event_errors.append(e)

cdef void scroll_callback(GLFWwindow* window_ptr, double x, double y):
    cdef Window window = get_window(window_ptr)
    abstract_callback(window, window.scroll_callback, window.gui.handle_scroll, x, y)

'''
cdef void mouse_button_callback(GLFWwindow* window_ptr, int button, int action, int modifiers):
    # this one also has different from default behaviour - obviously you can click anywhere if the gui is focused,
    # since that's how you de-focus the gui.
    # todo think about making this style an abstract callback as well (and letting the user chose?)
    cdef Window window = get_window(window_ptr)
    if window.handle_gui_callbacks:
        window.gui.handle_mouse_button(button, action, modifiers)
    if window.mouse_button_callback is not None:
        window.mouse_button_callback(window, button, action, modifiers)
'''

cdef void mouse_button_callback(GLFWwindow* window_ptr, int button, int action, int modifiers):
    cdef Window window = get_window(window_ptr)
    cdef int x, y
    try:
        if window.handle_gui_callbacks or window.mouse_button_callback is None:
            window.gui.handle_mouse_button(button, action, modifiers)
        # todo try to simplify logic, it's getting a bit out of hand
        if window.mouse_button_callback is not None and not (window.handle_gui_callbacks and window.gui.focused()):
            if action != MOUSE_DOWN:
                window.mouse_button_callback(window, button, action, modifiers)
            elif not window.gui_under_mouse():
                window.mouse_button_callback(window, button, action, modifiers)
    except Exception as e:
        glfw_event_errors.append(e)


cdef void resize_callback(GLFWwindow* window_ptr, int width, int height):
    cdef Window window = get_window(window_ptr)
    try:
        # always handle resize changes
        old_width, old_height = window.width, window.height
        glViewport(0, 0, width, height)
        window.width = width
        window.height = height
        if window.resize_callback is not None:
            window.resize_callback(window, old_width, old_height)
        else:
            window.gui.handle_resize(width, height)
    except Exception as e:
        glfw_event_errors.append(e)



cdef set_gl_enables():
    """
    call glEnable on stuff
    used after the nanogui draw since it resets stuff, as well as on window creation
    tbh i should just call this before every draw, but that might be wasteful
    TODO benchmark that
    """
    glEnable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# TODO make the call_gui_event_handlers thing consistently there or not there
