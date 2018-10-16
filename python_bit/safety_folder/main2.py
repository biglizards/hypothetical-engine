import math

import engine
import glm
import time


def normalize(v):
    return v / (v.x**2+v.y**2+v.z**2)**0.5


glm.normalize = normalize

window = engine.Window(name="hi there")


## gui

# variables altered by the gui
box_speed = 1
name = "not chris"

# create the gui
helper = engine.FormHelper(window.gui)
gui_window = helper.add_window(10, 10, b"GUI WINDOW (heck yeah)")

helper.add_group("box control")

speed_widget = helper.add_variable(b'speed', float, linked_var="box_speed")
name_w = helper.add_variable(b'name', str, linked_var="name", getter=lambda x: "chris", setter=print)

#engine.set_gui_callbacks(window.gui, window)
window.gui.update_layout()
window.set_cursor_capture('disabled')


# create objects

# NOTE/TODO: this data will eventually be generated dynamically or from a file or something
data = [
    -0.5, -0.5, -0.5, 0.0, 0.0,
    0.5, -0.5, -0.5, 1.0, 0.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    -0.5, 0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 0.0,

    -0.5, -0.5, 0.5, 0.0, 0.0,
    0.5, -0.5, 0.5, 1.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 1.0,
    0.5, 0.5, 0.5, 1.0, 1.0,
    -0.5, 0.5, 0.5, 0.0, 1.0,
    -0.5, -0.5, 0.5, 0.0, 0.0,

    -0.5, 0.5, 0.5, 1.0, 0.0,
    -0.5, 0.5, -0.5, 1.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, 0.5, 0.0, 0.0,
    -0.5, 0.5, 0.5, 1.0, 0.0,

    0.5, 0.5, 0.5, 1.0, 0.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    0.5, -0.5, -0.5, 0.0, 1.0,
    0.5, -0.5, -0.5, 0.0, 1.0,
    0.5, -0.5, 0.5, 0.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 0.0,

    -0.5, -0.5, -0.5, 0.0, 1.0,
    0.5, -0.5, -0.5, 1.0, 1.0,
    0.5, -0.5, 0.5, 1.0, 0.0,
    0.5, -0.5, 0.5, 1.0, 0.0,
    -0.5, -0.5, 0.5, 0.0, 0.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,

    -0.5, 0.5, -0.5, 0.0, 1.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    0.5, 0.5, 0.5, 1.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 0.0,
    -0.5, 0.5, 0.5, 0.0, 0.0,
    -0.5, 0.5, -0.5, 0.0, 1.0
]

cube_positions = [
    glm.vec3(0.0, 0.0, 0.0),
    glm.vec3(2.0, 5.0, -15.0),
    glm.vec3(-1.5, -2.2, -2.5),
    glm.vec3(-3.8, -2.0, -12.3),
    glm.vec3(2.4, -0.4, -3.5),
    glm.vec3(-1.7, 3.0, -7.5),
    glm.vec3(1.3, -2.0, -2.5),
    glm.vec3(1.5, 2.0, -2.5),
    glm.vec3(1.5, 0.2, -1.5),
    glm.vec3(-1.3, 1.0, -1.5)
]

crate_texture = engine.Texture('resources/container.jpg')
face_texture = engine.Texture('resources/duck.png', data_format=engine.RGBA)

crate = engine.Drawable(data, indices=None, data_format=(3, 2),
                        vert_path='shaders/perspective.vert',
                        frag_path='shaders/perspective.frag')
crate.shader_program.add_texture(crate_texture, "container", 0)
crate.shader_program.add_texture(face_texture, "face", 1)


# add key callback
def custom_key_callback(window, key, scancode, action, mods):
    if key == engine.KEY_Z:
        window.close()
    if key == engine.KEY_X:
        window.set_cursor_capture('disabled')
        camera.first_frame = True
    if key == engine.KEY_C:
        window.set_cursor_capture('normal')


window.key_callback = custom_key_callback


class Camera:
    def __init__(self, window: engine.Window):
        self.window = window

        self.position = glm.vec3(0, 0, 3)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.normalize(glm.cross(self.front, self.up))

        self.last_cursor_x = 0
        self.last_cursor_y = 0
        self.first_frame = True
        self.sensitivity = 0.01

        self.last_frame_time = time.time()
        #window.cursor_pos_callback = self.handle_cursor_pos

    def handle_input(self):
        if self.window.gui.focused():
            # don't handle input if the gui is focused
            return

        delta_t = time.time() - self.last_frame_time
        self.last_frame_time = time.time()
        speed = 5 * delta_t

        if self.window.is_pressed(engine.KEY_W):
            self.position += self.front * speed  # move forward slightly
        if self.window.is_pressed(engine.KEY_S):
            self.position -= self.front * speed  # move backwards slightly
        if self.window.is_pressed(engine.KEY_A):
            self.position -= self.right * speed
        if self.window.is_pressed(engine.KEY_D):
            self.position += self.right * speed

        if self.window.is_pressed(engine.KEY_SPACE):
            self.position += self.up * speed
        if self.window.is_pressed(engine.KEY_LEFT_CONTROL):
            self.position -= self.up * speed

        if self.window.is_pressed(engine.KEY_E):
            self.up = glm.vec3(glm.vec4(self.up, 1) * glm.rotate(glm.mat4(1), speed/4, self.front))
            self.right = glm.normalize(glm.cross(self.front, self.up))
        self.handle_cursor_pos(self.window, *self.window.cursor_location)

    def handle_cursor_pos(self, window, x, y):
        print("handle cursor", window.cursor_location)
        if self.first_frame:  # prevent jump in camera position when initialising the last positions
            self.first_frame = False
            self.last_cursor_x = x
            self.last_cursor_y = y

        delta_x = (x - self.last_cursor_x) * self.sensitivity
        delta_y = (y - self.last_cursor_y) * self.sensitivity
        print('[py,cur]', y, self.last_cursor_y, delta_x, delta_y)

        #if window.cursor_mode == 'normal':
            #return

        # rotate front by delta_x rads around the right vector (the local x axis)
        self.front = glm.vec3(glm.vec4(self.front, 1) * glm.rotate(glm.mat4(1), delta_y, self.right))
        self.front = glm.vec3(glm.vec4(self.front, 1) * glm.rotate(glm.mat4(1), delta_x, self.up))

        self.right = glm.normalize(glm.cross(self.front, self.up))

        self.last_cursor_x = x
        self.last_cursor_y = y

    def view_matrix(self):
        target = self.position + self.front  # target is just in front of the camera
        return glm.lookAt(self.position, target, self.up)


# main loop
st = time.time()
frame_count = 0
start_time = time.time()
camera = Camera(window)

while not window.should_close():
    window.clear_colour(0.3, 0.5, 0.8, 1)

    # view = world->camera
    '''
    x = time.time()-st
    camera_position = glm.vec3(0, 0, x)
    camera_target = glm.vec3(math.sin(x)*3, 0, 0)
    # camera_direction is the direction of the camera FROM the origin
    camera_direction = glm.normalize(camera_position-camera_target)

    world_up = glm.vec3(0, 1, 0)
    camera_right = glm.normalize(glm.cross(world_up, camera_direction))  # this works, but only if roll is always 0
    camera_up = glm.cross(camera_direction, camera_right)

    view = glm.lookAt(camera_position, camera_target, world_up)
    '''
    crate.shader_program.set_value("view", camera.view_matrix())

    # projection = camera->clip (adds perspective)
    projection = glm.perspective(glm.radians(45), window.width / window.height, 0.1, 100)
    #projection = glm.ortho(-5, 5, -5, 5, 0.1, 100)
    crate.shader_program.set_value("projection", projection)

    for i, position in enumerate(cube_positions):
        # model = local->world
        model = glm.translate(glm.mat4(1), position)
        model = glm.rotate(model, box_speed * time.time() * glm.radians(15 * (i + 1) + (i/5)**1.5), glm.vec3(0.5, 1, 0))
        crate.shader_program.set_value("model", model)
        crate.draw()

    window.gui.draw()

    window.swap_buffers()
    engine.poll_events()
    camera.handle_input()

    frame_count += 1
    if frame_count > 2**12:
        duration = time.time() - start_time
        print(duration, 2**12/duration, "fps", name)
        start_time = time.time()
        frame_count = 0
