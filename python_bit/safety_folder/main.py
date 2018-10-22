import glm

import engine

from cube import data
from game import Game, Entity
from physics import two_cubes_intersect

game = Game()

# create cube data/attributes
cube_positions = [
    glm.vec3(0.0, 0.0, 0.0),
    #glm.vec3(0.1, 0.1, 0.1),
    glm.vec3(2.0, 5.0, -15.0),
    glm.vec3(-1.5, -2.2, -2.33),
    glm.vec3(-3.8, -2.0, -12.3),
    glm.vec3(2.4, -0.4, -3.5),
    glm.vec3(-1.7, 3.0, -7.5),
    glm.vec3(1.3, -2.0, -2.3),
    glm.vec3(1.5, 2.0, -2.6),
    glm.vec3(1.5, 0.2, -1.4),
    glm.vec3(-1.3, 1.0, -1.7)
]

crate_attributes = {
    'data': data, 'indices': None, 'data_format': (3, 2),
    'textures': [('resources/container.jpg', 'container'), ('resources/duck.png', 'face')],
    'vert_path': 'shaders/perspective.vert', 'frag_path': 'shaders/perspective.frag'
}


# @@@@@
# gui
def reset_camera(*args, **kwargs):
    game.camera.position = glm.vec3(0, 0, 3)
    game.camera.front = glm.vec3(0, 0, -1)
    game.camera.up = glm.vec3(0, 1, 0)


def draw_dots_on_corners(*args):
    if not draw_dots:
        return
    for box in game.entities[1:]:
        corners = box.get_corners()
        for corner in corners:
            dot.position = corner
            dot.set_model()
            dot.draw()


# variables altered by the gui
box_speed = 0
gravity_enabled = False
bounce_enabled = False
draw_dots = False
dot = game.create_entity(**crate_attributes, scalar=glm.vec3(0.1, 0.1, 0.1))

# create the gui
helper = engine.FormHelper(game.gui)
gui_window = helper.add_window(10, 10, b"GUI WINDOW (heck yeah)")

# todo make you not have to declare everything as a variable (ie save a reference in helper and/or gui
helper.add_group("box control")
speed_widget = helper.add_variable(b'speed', float, linked_var="box_speed")
helper.add_group("gravity")
gravity_switch = helper.add_variable(b'enable gravity', bool, linked_var='gravity_enabled')
bounce_switch = helper.add_variable(b'enable bouncing', bool, linked_var='bounce_enabled')
dot_switch = helper.add_variable(b'draw dots', bool, linked_var='draw_dots')
reset_button = helper.add_button(b'reset', reset_camera)

game.gui.update_layout()


# @@@@@
# callbacks
def custom_key_callback(game, key, scancode, action, mods):
    if key == engine.KEY_Z:
        game.close()
    if key == engine.KEY_X:
        game.set_cursor_capture('disabled')
        game.camera.first_frame = True  # prevent the camera from jumping when switching between
        # normal and disabled without moving the mouse
    if key == engine.KEY_C:
        game.set_cursor_capture('normal')

    if key == engine.KEY_V:
        print(game.camera.up, game.camera.front)


game.key_callback = custom_key_callback

# @@@@@
# create crates
crates = []
for pos in cube_positions:
    crate = game.create_entity(**crate_attributes, position=pos, has_gravity=True)
    crates.append(crate)
floor_crate = game.create_entity(**crate_attributes, position=glm.vec3(0, -10, 0), scalar=glm.vec3(10, 1, 10),
                                 has_gravity=False)


# @@@@@
# on_frame callbacks
def spin_crates(delta_t):
    for i, crate in enumerate(crates):
        angle = box_speed * delta_t * glm.radians(15 * (i + 1))
        crate.orientation = glm.rotate(crate.orientation, angle, glm.vec3(0.5, 1, 0))


gravity = glm.vec3(0, -1, 0)
physics_delta_t = 0


def do_gravity(delta_t):
    global physics_delta_t
    if not gravity_enabled:
        return

    # only run every 1/60th of a second or so
    global physics_delta_t
    physics_delta_t += delta_t
    if physics_delta_t < (1/60):
        return
    delta_t, physics_delta_t = physics_delta_t, 0

    for entity in game.entities:
        if not entity.has_gravity:
            continue

        entity.velocity += gravity * delta_t
        entity.position += entity.velocity * delta_t
        entity.set_model()

        for other_entity in game.entities:
            if other_entity is entity:
                continue
            if two_cubes_intersect(entity, other_entity):
                # don't
                entity.position -= entity.velocity * delta_t
                entity.velocity = glm.vec3(0, 0, 0)


game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)
game.add_callback('on_frame', draw_dots_on_corners)

game.run(True)
