# distutils: language = c++

include "config.pxi"
IF WINDOWS:
    cdef extern from "windows.h":
        pass  # force windows header to be included early


cimport cengine
from cengine cimport GLFWwindow, set_callbacks
cimport nanogui
import glm
from libc.time cimport clock, CLOCKS_PER_SEC


include "crash_handler.pxi"
include "gl_declarations.pxi"
include "util.pxi"
include "shader.pxi"
include "model.pxi"
include "window.pxi"
include "texture.pxi"
include "nanogui.pxi"


cdef extern from *:
    void glfwSwapBuffers(GLFWwindow* window)
    void glfwPollEvents()
    int glfwWindowShouldClose(GLFWwindow* window)

    void glfwSwapInterval(int)

    int GL_COLOR_BUFFER_BIT  # haha yes this constant exists
    void glGenVertexArrays(int, unsigned int*)

    # temp
    void glDrawArrays(unsigned int, int, int)
    void glDrawElements(unsigned int mode, int count, unsigned int data_type, void* indices)  # let indices = 0 if EBO
    int GL_TRIANGLES
    int GL_UNSIGNED_INT
    unsigned int GL_BLEND
    unsigned int GL_SRC_ALPHA
    unsigned int GL_ONE_MINUS_SRC_ALPHA
    void glBlendFunc(unsigned int, unsigned int)



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
    cdef ShaderProgram shader_program
    cdef int no_of_indices

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, data, indices, data_format, vert_path, frag_path, geo_path=None):
        self.model = Model()
        self.no_of_indices = len(indices)
        self.shader_program = ShaderProgram(vert_path, frag_path, geo_path)
        self.model.buffer_packed_data(data, data_format, indices)


    cpdef draw(self):
        if not self.model:
            raise RuntimeError('Drawable was not properly init')
        self.model.bind()
        self.shader_program.use()
        glDrawElements(GL_TRIANGLES, self.no_of_indices, GL_UNSIGNED_INT, NULL)


cdef float* value_ptr(thing):
    return <float*>(<int>glm.value_ptr(thing).value)

cpdef demo():
    cdef Window window = Window()

    cdef Screen screen = Screen(window)   # todo make name make more sense; "screen" is bad, maybe "gui_screen"
    cdef FormHelper gui = FormHelper(screen)
    gui.add_window(10, 10, b"GUI WINDOW (heck yeah)")
    cengine.set_callbacks(screen.screen, window.window)
    screen.update_layout()

    cdef Triangle triangle1, triangle2
    cdef Drawable rect

    data = [-0.75, -0.75, 0.0,
            -0.25, -0.75, 0.0,
            -0.5,  -0.25, 0.0,]
    triangle1 = Triangle(data)

    data = [0.75, 0.75, 0.0,
            0.25, 0.75, 0.0,
            0.5,  0.25, 0.0,]
    triangle2 = Triangle(data)

    data = [ # positions      colors           texture coords
            0.5,  0.5, 0.0,   1.0, 0.0, 0.0,   1.0, 1.0,   # top right
            0.5, -0.5, 0.0,   0.0, 1.0, 0.0,   1.0, 0.0,   # bottom right
           -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0,   # bottom left
           -0.5,  0.5, 0.0,   1.0, 1.0, 0.0,   0.0, 1.0    # top left
    ]
    indices = [0, 1, 3, 1, 2, 3]
    rect = Drawable(data, indices, data_format=(3, 3, 2),
                    vert_path='shaders/texture.vert',
                    frag_path='shaders/texture.frag')

    cdef Texture crate = Texture('container.jpg')
    cdef Texture face =  Texture('awesomeface.png', data_format=GL_RGBA)
    rect.shader_program.set_value("texture1", 0)
    rect.shader_program.set_value("texture2", 1)

    cdef unsigned int i = 0
    cdef long duration
    cdef long start_time = clock()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while not window.should_close():
        window.clear_colour(0.3, 0.5, 0.8, 1)

        trans = glm.translate(glm.mat4(1), glm.vec3(.5, -.5, 0))
        trans = glm.rotate(trans, glfwGetTime(), glm.vec3(0, 0, 1))
        rect.shader_program.set_value("transform", trans)

        crate.bind_to_unit(unit=0)
        face.bind_to_unit(unit=1)
        rect.draw()

        # draw gui yo
        screen.draw()

        window.swap_buffers()
        poll_events()


        i += 1
        if i > 2**14:
            duration = clock() - start_time
            print(duration, (2**14 * CLOCKS_PER_SEC)/duration, "fps")
            start_time = clock()
            i = 0


cpdef poll_events():
    glfwPollEvents()

