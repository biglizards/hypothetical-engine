# distutils: language = c++

include "config.pxi"
IF WINDOWS:
    cdef extern from "windows.h":
        pass  # force windows header to be included early

cimport cengine
from cengine cimport GLFWwindow, set_callbacks
from glfw_declarations cimport *
cimport nanogui
import glm
from libc.time cimport clock, CLOCKS_PER_SEC
from libc.stdint cimport uintptr_t

include "crash_handler.pxi"
include "gl_declarations.pxi"
include "util.pxi"
include "shader.pxi"
include "model.pxi"
include "window.pxi"
include "texture.pxi"
include "nanogui.pxi"

RGBA = GL_RGBA

cdef char* load_file(const char* path):
    return open(path, 'rb').read()

cpdef int main():
    cengine.demo(load_file)

cdef class Triangle(Model):
    cdef unsigned int shader_program

    def __cinit__(self, data):
        self.buffer_packed_data(data, (3,))
        self.shader_program = load_shader_program('shaders/basic.vert', 'shaders/basic.frag')

    cdef void draw(self):
        self.bind()
        glUseProgram(self.shader_program)
        glDrawArrays(GL_TRIANGLES, 0, 3)


IF DEBUG == 1:
    print("yes it's debug")
ELSE:
    print("not debug")


"""
thinking out loud for a bit here
a drawable thing probably has textures
and it needs to load those textures before it can be drawn
so a drawable needs to manage the textures
and since textures and shaders are pretty linked, it needs to manage both
so maybe something like square -> drawable -> model
i think the issue here is "model" isnt very well defined so i want to stick a load of functionality in it
so i guess i need to be kinda strict about what its use is
ok here it is: the `model` is a wrapper around the VAO (and VBO and EBO)
A drawable has a model and shaders (and textures)
and anything built on top of that can do whatever
"""

cdef class Drawable:
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
            raise RuntimeError('Drawable was not properly init')
        self.model.bind()
        self.shader_program.use()
        self.shader_program.bind_textures()
        if self.indexed:
            glDrawElements(GL_TRIANGLES, self.no_of_indices, GL_UNSIGNED_INT, NULL)
        else:
            glDrawArrays(GL_TRIANGLES, 0, self.no_of_indices)


cdef float* value_ptr(thing):
    return <float*>(<uintptr_t>glm.value_ptr(thing).value)

cpdef set_gui_callbacks(Screen screen, Window window):
    cengine.set_callbacks(screen.screen, window.window)

cpdef poll_events():
    glfwPollEvents()

