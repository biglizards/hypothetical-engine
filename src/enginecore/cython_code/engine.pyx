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
import glm
from libc.time cimport clock, CLOCKS_PER_SEC
from libc.stdint cimport uintptr_t

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
    glfwPollEvents()

cpdef wait_until_finished():
    glFlush()
    glFinish()

