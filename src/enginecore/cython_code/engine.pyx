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

cimport cengine
from cengine cimport GLFWwindow, set_callbacks
cimport nanogui

include "crash_handler.pxi"
include "gl_declarations.pxi"
include "glfw_declarations.pxd"
include "util.pxi"
include "shader.pxi"
include "model.pxi"
include "window.pxi"
include "texture.pxi"
include "nanogui.pxi"
include "physics.pxi"

IF DEBUG == 1:
    print("yes it's debug")
ELSE:
    print("not debug")

cpdef set_gui_callbacks(Gui gui, Window window):
    cengine.set_callbacks(gui.screen, window.window)

cpdef poll_events():
    """
    An unreasonably complex wrapper around glfwPollEvents for what it is. 
    Processes any events in the event queue, and calls the appropriate function.
    
    WARNING: if any functions called raise an error, the event queue will be cleared, but some events
    may not be processed. This is because glfwPollEvents is a C function, so exceptions cannot
    propagate through it. If an exception is raised, it is stored, and any more events in the queue
    are ignored. This prevents code from being called while user data is potentially in an error state.
    (and also ensures that a maximum of one exception is raised per call to poll_events)
    """
    glfwPollEvents()
    while glfw_event_errors:
        raise glfw_event_errors.pop()

cpdef wait_until_finished():
    glFlush()
    glFinish()

