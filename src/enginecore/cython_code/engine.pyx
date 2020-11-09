# distutils: language = c++
# distutils: define_macros=CYTHON_TRACE=1

include "config.pxi"
IF WINDOWS:
    cdef extern from "windows.h":
        """
        #undef max  // for some reason, windows.h defines these as macros,
        #undef min  // which break nanogui
        """
        pass  # force windows header to be included early

cimport includes.cengine as cengine
from includes.cengine cimport GLFWwindow, set_callbacks
cimport includes.nanogui as nanogui

include "crash_handler.pxi"
include "includes/gl_declarations.pxi"
include "includes/glfw_declarations.pxd"
include "util.pxi"
include "shader.pxi"
include "model.pxi"
include "window.pxi"
include "texture.pxi"
include "nanogui.pxi"

# the physics module is now pure python (the speedup was only around 20% so I'm not too fussed)
# include "physics.pxi"

include "tests/test_window.pxi"

cpdef poll_events():
    """
    An unreasonably complex wrapper around glfwPollEvents for what it is. 
    Processes any events in the event queue, and calls the appropriate function.
    If an exception is raised in a handler, it is caught and re-raised in this function
    """
    # Since glfwPollEvents is a C function and python exceptions cannot propagate through it
    # if an error is raised in a python function, and it gets high enough it would reach C code,
    # we catch it, then store any other events dispatched by glfwPollEvents (it can dispatch multiple per call)
    # as a result, whenever we call this function, we may have 0 or more stored events
    # (but any exceptions are handled at the end of this function, so there should be none to start with)

    # general steps:
    # 1. handle all events that got ignored last time (if any exist)
    # 2. handle new events
    # 3. either 1 or 0 exceptions should have been caught, if there is one, raise it

    cdef GLFWwindow* window_ptr

    for window, callback_func, gui_callback_func, args, always_call_callback_func in glfw_ignored_events:
        abstract_callback(window, callback_func, gui_callback_func, *args,
                          always_call_callback_func=always_call_callback_func)

    for window_ptr_as_int, button, action, modifiers in glfw_ignored_events_mouse:
        window_ptr = <GLFWwindow*>window_ptr_as_int
        mouse_button_callback(window_ptr, button, action, modifiers)
    for window_ptr_as_int, width, height in glfw_ignored_events_resize:
        window_ptr = <GLFWwindow*>window_ptr_as_int
        resize_callback(window_ptr, width, height)

    glfwPollEvents()

    assert len(glfw_event_errors) < 2, "more than one exception was raised at the same time -- this is a bug"
    while glfw_event_errors:
        raise glfw_event_errors.pop()

cpdef wait_until_finished():
    glFlush()
    glFinish()

