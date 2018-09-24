# distutils: language = c++

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

IF DEBUG == 1:
    print("yes it's debug")
ELSE:
    print("not debug")


cdef class Drawable:
    """
    A drawable thing has
     - a shader program
     - a model
     - textures
    This was originally meant to be a base class for stuff which could be drawn,
    but it became generic enough that i don't even need subclasses.
    I guess stuff can still extend it though, if they want.
    """
    cdef Model model
    cdef public ShaderProgram shader_program
    cdef int no_of_indices
    cdef bint indexed

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, data, indices, data_format, vert_path, frag_path, geo_path=None):
        if indices is None:
            self.indexed = False
            self.no_of_indices = len(data) / sum(data_format)
        else:
            self.indexed = True
            self.no_of_indices = len(indices)

        self.model = Model()
        self.shader_program = ShaderProgram(vert_path, frag_path, geo_path)
        self.model.buffer_packed_data(data, data_format, indices)


    cpdef draw(self):
        if not self.model:
            raise RuntimeError('Drawable was not properly init! Was super() called?')
        self.model.bind()
        self.shader_program.use()
        self.shader_program.bind_textures()
        if self.indexed:
            glDrawElements(GL_TRIANGLES, self.no_of_indices, GL_UNSIGNED_INT, NULL)
        else:
            glDrawArrays(GL_TRIANGLES, 0, self.no_of_indices)


cpdef set_gui_callbacks(Gui gui, Window window):
    cengine.set_callbacks(gui.screen, window.window)

cpdef poll_events():
    glfwPollEvents()

