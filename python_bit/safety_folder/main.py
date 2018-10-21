import glm

import engine

import cube
from cube import data
from game import Game, Entity

game = Game()

# create cube data/attributes
cube_positions = [
    glm.vec3(0.0, 0.0, 0.0),
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
    print("reset", args, kwargs)
    game.camera.position = glm.vec3(0, 0, 3)
    game.camera.front = glm.vec3(0, 0, -1)
    game.camera.up = glm.vec3(0, 1, 0)


# variables altered by the gui
box_speed = 1
gravity_enabled = False
bounce_enabled = False

# create the gui
helper = engine.FormHelper(game.gui)
gui_window = helper.add_window(10, 10, b"GUI WINDOW (heck yeah)")

helper.add_group("box control")
speed_widget = helper.add_variable(b'speed', float, linked_var="box_speed")
helper.add_group("gravity")
gravity_switch = helper.add_variable(b'enable gravity', bool, linked_var='gravity_enabled')
bounce_switch = helper.add_variable(b'enable bouncing', bool, linked_var='bounce_enabled')
button = helper.add_button(b'reset', reset_camera)

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
        crate.orientation = glm.rotate(crate.orientation, box_speed * delta_t * glm.radians(15 * (i + 1)),
                                       glm.vec3(0.5, 1, 0))

'''
def do_gravity(delta_t):
    if not gravity_enabled:
        return
    game.camera.velocity += glm.vec3(0, -9.8, 0) * delta_t
    game.camera.position += game.camera.velocity * delta_t
    if game.camera.position.y < -8.5:
        game.camera.position.y = -8.5
        game.camera.velocity = glm.vec3(0, 10, 0) if bounce_enabled else glm.vec3(0, 0, 0)
'''
gravity = glm.vec3(0, -1, 0)


def do_gravity(delta_t):
    if not gravity_enabled:
        return
    entity: Entity
    other_entity: Entity
    for entity in game.entities:
        if not entity.has_gravity:
            continue
        entity.velocity += gravity * delta_t
        entity.position += entity.velocity * delta_t

        aabb_min, aabb_max = generate_aabb(entity)
        for other_entity in game.entities:
            if other_entity is entity:
                continue
            other_aabb_min, other_aabb_max = generate_aabb(other_entity)
            if aabb_intersect(aabb_min, aabb_max, other_aabb_min, other_aabb_max):
                # don't
                entity.position -= entity.velocity * delta_t
                entity.velocity = glm.vec3(0, 0, 0)


def generate_aabb(entity: Entity):
    model = entity.generate_model(ignore_orientation=True)
    aabb_min = model * glm.vec4(cube.aabb_min, 1)
    aabb_max = model * glm.vec4(cube.aabb_max, 1)
    return aabb_min, aabb_max


def aabb_intersect(min1, max1, min2, max2):
    return min1.x <= max2.x and max1.x >= min2.x and \
           min1.y <= max2.y and max1.y >= min2.y and \
           min1.z <= max2.z and max1.z >= min2.z


#game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)

game.run(True)
