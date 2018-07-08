# distutils: language = c++

cimport cengine
from cengine cimport GLFWwindow, set_callbacks
cimport nanogui
from libc.time cimport clock, CLOCKS_PER_SEC

include "shader.pxi"
include "model.pxi"
include "window.pxi"
include "config.pxi"
include "nanogui.pxi"

cdef extern from *:
    void glfwSwapBuffers(GLFWwindow* window)
    void glfwPollEvents()
    int glfwWindowShouldClose(GLFWwindow* window)

    void glfwSwapInterval(int)

    int GL_COLOR_BUFFER_BIT  # haha yes this constant exists
    void glGenVertexArrays(int, unsigned int*)

    # temp
    void glUseProgram(unsigned int)
    void glDrawArrays(unsigned int, int, int)
    int GL_TRIANGLES


cdef char* load_file(const char* path):
    return open(path, 'rb').read()

cpdef int main():
    cengine.demo(load_file)

cdef class Triangle(Model):
    cdef unsigned int shader_program

    def __cinit__(self, data):
        self.buffer_packed_data(data, len(data), (3,))
        self.shader_program = load_shader_program('shaders/basic.vert', 'shaders/basic.frag')

    cdef void draw(self):
        self.bind()
        glUseProgram(self.shader_program)
        glDrawArrays(GL_TRIANGLES, 0, 3)


IF DEBUG == 1:
    print("yes it's debug")
ELSE:
    print("not debug")


cpdef demo():
    cdef Window window = Window()

    cdef Screen screen = Screen(window)   # todo make name make more sense; "screen" is bad, maybe "gui_screen"
    cdef FormHelper gui = FormHelper(screen)
    gui.add_window(10, 10, b"GUI WINDOW (heck yeah)")
    cengine.set_callbacks(screen.screen, window.window)
    screen.update_layout()

    cdef Triangle triangle1, triangle2

    data = [-0.75, -0.75, 0.0,
            -0.25, -0.75, 0.0,
            -0.5,  -0.25, 0.0,]
    triangle1 = Triangle(data)

    data = [0.75, 0.75, 0.0,
            0.25, 0.75, 0.0,
            0.5,  0.25, 0.0,]
    triangle2 = Triangle(data)

    cdef unsigned int i = 0
    cdef long duration
    cdef long start_time = clock()

    while not window.should_close():
        window.clear_colour(0.3, 0.5, 0.8, 1)

        # draw triangles
        triangle1.draw()
        triangle2.draw()

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

