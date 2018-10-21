import glm
import math
import time

import engine
from camera import Camera
from cube import data




def reset_camera(*args, **kwargs):
    print("reset", args, kwargs)
    camera.position = glm.vec3(0, 0, 3)
    camera.front = glm.vec3(0, 0, -1)
    camera.up = glm.vec3(0, 1, 0)

window = engine.Window(name="game demo")


## gui

# variables altered by the gui
box_speed = 1
name = "not chris"
gravity_enabled = False
bounce_enabled = False

# create the gui
helper = engine.FormHelper(window.gui)
gui_window = helper.add_window(10, 10, b"GUI WINDOW (heck yeah)")

helper.add_group("box control")

speed_widget = helper.add_variable(b'speed', float, linked_var="box_speed")
name_w = helper.add_variable(b'name', str, linked_var="name", getter=lambda x: "chris", setter=print)
helper.add_group("gravity")
gravity_switch = helper.add_variable(b'enable gravity', bool, linked_var='gravity_enabled')
bounce_switch = helper.add_variable(b'enable bouncing', bool, linked_var='bounce_enabled')
button = helper.add_button(b'reset', reset_camera)



#engine.set_gui_callbacks(window.gui, window)
window.gui.update_layout()
#window.set_cursor_capture('disabled')


# create objects

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


# TODO remove data, data_format once model loading is added
class Entity(engine.Drawable):
    def __init__(self, data, indices, data_format, textures, vert_path, frag_path, geo_path=None, location=None, orientation=None, scaler=None):
        super().__init__(data, indices, data_format, vert_path, frag_path, geo_path)
        for i, (texture, texture_name) in enumerate(textures):
            self.shader_program.add_texture(texture, texture_name, i)
        self.location = location if location is not None else glm.vec3(0, 0, 0)
        self.orientation = orientation if orientation is not None else glm.quat(1, 0, 0, 0)
        self.scaler = scaler

    def set_model(self):
        # model = local->world
        model = glm.translate(glm.mat4(1), self.location)
        #model = glm.rotate(model, box_speed * time.time() * glm.radians(15 * (i + 1) + (i/5)**1.5), glm.vec3(0.5, 1, 0))
        model = model * glm.mat4_cast(self.orientation) # rotate by orientation
        if self.scaler is not None:
            model = glm.scale(model, self.scaler)
        self.shader_program.set_value("model", model)


crate_texture = engine.Texture('resources/container.jpg')
face_texture = engine.Texture('resources/duck.png', data_format=engine.RGBA)

crates = []
for pos in cube_positions:
    crate = Entity(data, indices=None, data_format=(3, 2), textures=((crate_texture, 'container'),(face_texture, 'face')),
                   vert_path='shaders/perspective.vert', frag_path='shaders/perspective.frag', location=pos)
    crates.append(crate)

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

    if key == engine.KEY_V:
        print(camera.up, camera.front)


window.key_callback = custom_key_callback



# main loop
st = time.time()
frame_count = 0
start_time = time.time()
camera = Camera(window)

last_frame_time = time.time()

# view = world->camera
view = camera.view_matrix()

# projection = camera->clip (adds perspective)
projection = glm.perspective(glm.radians(75), window.width / window.height, 0.1, 10)

while not window.should_close():
    delta_t = time.time() - last_frame_time
    last_frame_time = time.time()
    window.clear_colour(0.3, 0.5, 0.8, 1)


    #for i, crate in enumerate(crates):
    #    crate.shader_program.set_value('view', view)
    #    crate.shader_program.set_value("projection", projection)
    #    crate.orientation = glm.rotate(crate.orientation, box_speed * delta_t * glm.radians(15 * (i+1)), glm.vec3(0.5, 1, 0))
    #    crate.set_model()
    #    crate.draw()

    #model = glm.translate(glm.mat4(1), glm.vec3(0, -10, 0))
    #model = glm.scale(model, glm.vec3(10, 1, 10))
    #crate.shader_program.set_value("model", model)
    #crate.draw()

    #window.gui.draw()

    #window.swap_buffers()
    #engine.poll_events()
    #camera.handle_input()

    # physics engine
    if gravity_enabled:
        camera.velocity += glm.vec3(0, -9.8, 0) * delta_t
        camera.position += camera.velocity * delta_t
        if camera.position.y < -8.5:
            camera.position.y = -8.5
            camera.velocity = glm.vec3(0, 10, 0) if bounce_enabled else glm.vec3(0, 0, 0)

    frame_count += 1
    if frame_count > 2**10:
        duration = time.time() - start_time
        print(duration, 2**10/duration, "fps", name)
        start_time = time.time()
        frame_count = 0
