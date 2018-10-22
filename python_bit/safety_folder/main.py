import glm
import itertools
from math import inf

import engine

import cube
from cube import data
from game import Game, Entity
from util import multiply_vec3

game = Game()

# create cube data/attributes
cube_positions = [
    glm.vec3(0.0, 0.0, 0.0),
    glm.vec3(0.1, 0.1, 0.1),
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
box_speed = 0
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

        for other_entity in game.entities:
            if other_entity is entity:
                continue
            if two_cubes_intersect(entity, other_entity):
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


def two_cubes_intersect(cube1, cube2):
    corners1 = cube.gen_corners(cube1.model)
    corners2 = cube.gen_corners(cube2.model)
    return unaligned_intersect(corners1, cube1.model, corners2, cube2.model)


def unaligned_intersect(corners1, model1, corners2, model2):
    """ adapted from explanation at
    https://gamedev.stackexchange.com/questions/44500/how-many-and-which-axes-to-use-for-3d-obb-collision-with-sat
    According to that, this is sufficient to show they do (or don't) intersect
    """
    i_vector = glm.vec4(1, 0, 0, 0)
    j_vector = glm.vec4(0, 1, 0, 0)
    k_vector = glm.vec4(0, 0, 1, 0)
    unit_vectors = (i_vector, j_vector, k_vector)

    local_vectors_1 = [glm.vec3(model1 * unit_vector) for unit_vector in unit_vectors]
    local_vectors_2 = [glm.vec3(model2 * unit_vector) for unit_vector in unit_vectors]

    # generate all local unit vectors
    for axis in itertools.chain(local_vectors_1, local_vectors_2):
        if intersects_on_projection(corners1, corners2, axis) is False:
            return False

    # generate all cross products of local unit vectors
    for unit_vector_1, unit_vector_2 in itertools.product(local_vectors_1, local_vectors_2):
        axis = glm.cross(unit_vector_1, unit_vector_2)
        if axis == glm.vec3(0, 0, 0):
            continue
        if intersects_on_projection(corners1, corners2, axis) is False:
            return False
    return True


def intersects_on_projection(corners1, corners2, axis):
    min1, max1 = get_min_and_max(corners1, axis)
    min2, max2 = get_min_and_max(corners2, axis)

    # if they overlap, the sum of the two lengths will be less than the length between the biggest and the smallest
    total_length = max(max1, max2) - min(min1, min2)
    sum_of_both = (max1 - min1) + (max2 - min2)
    return total_length < sum_of_both   # can change to =< if you want touching to count as overlapping


def get_min_and_max(corners, axis):
    # declare min and max as the wrong infinities so any the first data overwrites it
    min_val = inf
    max_val = -inf
    for corner in corners:
        dist = glm.dot(corner, axis)
        if dist < min_val:
            min_val = dist
        elif dist > max_val:
            max_val = dist
        min_val = min(min_val, dist)
        max_val = max(max_val, dist)
    return min_val, max_val


game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)

game.run(True)
