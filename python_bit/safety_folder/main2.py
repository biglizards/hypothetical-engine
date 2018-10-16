import glm
import math
import time

import engine


def rotate_vec3(vec, angle, axis):
    return glm.vec3(glm.vec4(vec, 1) * glm.rotate(glm.mat4(1), angle, axis))


window = engine.Window(name="hi there")


## gui

# variables altered by the gui
box_speed = 1
name = "not chris"
gravity_enabled = True

# create the gui
helper = engine.FormHelper(window.gui)
gui_window = helper.add_window(10, 10, b"GUI WINDOW (heck yeah)")

helper.add_group("box control")

speed_widget = helper.add_variable(b'speed', float, linked_var="box_speed")
name_w = helper.add_variable(b'name', str, linked_var="name", getter=lambda x: "chris", setter=print)
helper.add_group("gravity")
gravity_switch = helper.add_variable(b'enable gravity', bool, linked_var='gravity_enabled')

#engine.set_gui_callbacks(window.gui, window)
window.gui.update_layout()
#window.set_cursor_capture('disabled')


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
        camera.first_frame = True  # prevent the camera from jumping when switching between
                                   # normal and disabled without moving the mouse
    if key == engine.KEY_C:
        window.set_cursor_capture('normal')


#window.key_callback = custom_key_callback


class Camera:
    def __init__(self, window: engine.Window):
        self.window = window

        self.position = glm.vec3(0, 0, 3)
        self.velocity = glm.vec3(0, 0, 0)
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

    def handle_cursor_pos(self, x, y):
        if self.first_frame:  # prevent jump in camera position when initialising the last positions
            self.first_frame = False
            self.last_cursor_x = x
            self.last_cursor_y = y

        if window.cursor_mode == 'normal':
            return

        delta_x = (x - self.last_cursor_x) * self.sensitivity
        delta_y = (y - self.last_cursor_y) * self.sensitivity

        self.rotate_camera_with_clamping(delta_x, delta_y)
        self.right = glm.normalize(glm.cross(self.front, self.up))

        self.last_cursor_x = x
        self.last_cursor_y = y

    def rotate_camera_with_clamping(self, delta_x, delta_y):
        """Since the camera glitches out if you look too far up or down (ie bending over backwards)
           it is restricted to not be able to do that
           TODO allow that to happen
         """
        old_front = self.front
        self.front = rotate_vec3(self.front, axis=self.right, angle=delta_y)
        # if the camera went below (or over) the y axis, one of the x and z signs would flip
        # old_z * z is negative if they have different signs, positive otherwise
        if old_front.x * self.front.x < 0 or old_front.z * self.front.z < 0:
            self.front = old_front  # since it crossed the z axis, restore the old one instead

        # also rotate it horizontally, but with no restrictions
        self.front = rotate_vec3(self.front, axis=self.up, angle=delta_x)

    def view_matrix(self):
        target = self.position + self.front  # target is just in front of the camera
        return glm.lookAt(self.position, target, self.up)


# main loop
st = time.time()
frame_count = 0
start_time = time.time()
camera = Camera(window)

while not window.should_close():
    window.gui.draw()
    last_frame_time = time.time()
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
    projection = glm.perspective(glm.radians(75), window.width / window.height, 0.1, 100)
    crate.shader_program.set_value("projection", projection)

    for i, position in enumerate(cube_positions):
        # model = local->world
        model = glm.translate(glm.mat4(1), position)
        model = glm.rotate(model, box_speed * time.time() * glm.radians(15 * (i + 1) + (i/5)**1.5), glm.vec3(0.5, 1, 0))
        crate.shader_program.set_value("model", model)
        crate.draw()

    model = glm.translate(glm.mat4(1), glm.vec3(0, -10, 0))
    model = glm.scale(model, glm.vec3(10, 1, 10))
    crate.shader_program.set_value("model", model)
    crate.draw()

    window.gui.draw()

    window.swap_buffers()
    engine.poll_events()
    camera.handle_input()

    # physics engine
    delta_t = time.time() - last_frame_time
    if gravity_enabled:
        camera.velocity += glm.vec3(0, -9.8, 0) * delta_t
        camera.position += camera.velocity * delta_t
        if camera.position.y < -8:
            camera.position.y = -8
            camera.velocity = glm.vec3(0, 10, 0)

    frame_count += 1
    if frame_count > 2**13:
        duration = time.time() - start_time
        print(duration, 2**13/duration, "fps", name)
        start_time = time.time()
        frame_count = 0
