import glm
import engine

import util
from cube import data
from game import Game, Entity
from physics import two_cubes_intersect

proj = glm.frustum(-1.0, 1.0, -1.0, 1.0, 1.0, 100.0)
game = Game()

# create cube data/attributes
cube_positions = [
    glm.vec3(0.0, 0.0, 0.0),
    # glm.vec3(0.1, 0.1, 0.1),
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

# for x in range(15):
#     cube_positions.append(glm.vec3((random.random()-0.5)*40, (random.random()-0.5)*40, (random.random()-0.5)*40))

crate_attributes = {
    'data': data, 'indices': None, 'data_format': (3, 2),
    'textures': [('resources/container.jpg', 'container'), ('resources/duck.png', 'face')],
    'vert_path': 'shaders/perspective.vert', 'frag_path': 'shaders/highlight.frag'
}


# @@@@@
# gui
def reset_camera(*_args, **_kwargs):
    game.camera.position = glm.vec3(0, 0, 3)
    game.camera.front = glm.vec3(0, 0, -1)
    game.camera.up = glm.vec3(0, 1, 0)


def draw_dots_on_corners(*_args):
    if not draw_dots:
        return
    proj_times_view = game.projection * game.camera.view_matrix()  # i'm unpacking it for performance reasons
    for box in game.entities[1:]:
        corners = box.get_corners()
        for corner in corners:
            dot.position = corner
            transformation_matrix = proj_times_view * dot.generate_model()
            dot.shader_program.set_value('transformMat', transformation_matrix)
            dot.draw()


def draw_axes(entity: Entity):  # as in, the plural of axis
    w = (entity.set_transform_matrix(game) * glm.vec4(0, 0, 0, 1)).w * 0.3
    world_axes = [glm.vec3(1, 0, 0), glm.vec3(0, 1, 0), glm.vec3(0, 0, 1)]

    for world_axis, vector, axis in zip(world_axes, entity.local_unit_vectors(), axes):
        vector = glm.normalize(vector)
        axis.scalar = glm.vec3(0.10, 0.10, 0.10) + world_axis  # make the axis the right shape

        # calculate the length of the axis
        axis.position = entity.position
        thing = (axis.generate_model() * glm.vec4(w * vector, 1)) - glm.vec4(entity.position, 0)
        length = glm.length(thing.xyz)
        axis.position = entity.position + (0.5 * vector * entity.scalar) + (0.5 * length * vector)
        axis.orientation = entity.orientation

        # # # anything below this is shit i added to test dragging; feel free to delete later
        # # # (apart from the axis.should_render bit)

        # put dot at where 0, 0 is in screen space
        # algorithm:
        #  - take vector, project onto screen
        #  - also project box + vector*2 onto screen to get the direction vector
        #  - normalize the direction vector, then {move 0.1 units that direction}{move however much is specified by the mouse}
        #  - project the final location back into world space by:
        #    - set the camera pos to (0, 0, 0) [i dont know why i need to do this, but i do]
        #    - take the final_direction_vector = (proj * view)^-1 * screenSpaceLocation
        #    - solve simultaneously (camera_pos + lambda*final_dir) and (box_pos + mu*vector_dir) to get the point of intersection
        #  - {print it out}{move the box there}
        # TODO move this out of the draw routine, what's it even doing here smh
        '''
        screen_vector, pos_in_world_space = get_world_space_vector(game, game.cursor_location_ndc)

        point_of_intersection = solve(axis.position, vector, game.camera.position, screen_vector.xyz)
        print(game.camera.position, screen_vector.xyz)

        dot.position = point_of_intersection
        dot.should_render = True
        '''

        axis.should_render = True


def change_highlighted_object(entity: Entity):
    global selected_object
    if selected_object is not None:
        selected_object.shader_program.set_value('highlightAmount', 0.0)
    if entity is not None:
        entity.shader_program.set_value('highlightAmount', 0.3)
    selected_object = entity


def select_entity(entity: Entity or None):
    target_entity = entity
    change_highlighted_object(target_entity)
    create_object_gui(target_entity)


def create_object_gui(entity: Entity):
    # todo wrap and use advanced grid layout to get the x, y, z things all on one line
    # https://nanogui.readthedocs.io/en/latest/api/class_nanogui__AdvancedGridLayout.html#class-nanogui-advancedgridlayout
    global selected_gui
    if selected_gui is not None:
        selected_gui.dispose()
        selected_gui = None
    if entity is None:
        return

    helper = engine.FormHelper(game.gui)
    new_gui = helper.add_window(640, 10, 'entity properties')

    for key, item in entity.__dict__.items():
        if key.startswith('_'):
            continue
        if isinstance(item, glm.vec3):
            helper.add_group(key)
            for i in range(3):
                def setter(new_val, _old_val, i=i, item=item):  # the keyword args save the value (otherwise all
                    item[i] = new_val                           # functions would use the last value in the loop)

                def getter(i=i, key=key, entity=entity):
                    return entity.__dict__[key][i]
                letter = ['x', 'y', 'z'][i]
                helper.add_variable(letter, float, setter=setter, getter=getter)

        elif isinstance(item, (int, float, bool, str)):
            helper.add_group(key)

            def setter(new_val, _old_val, key=key, entity=entity):
                entity.__dict__[key] = new_val

            def getter(key=key, entity=entity):
                return entity.__dict__[key]
            helper.add_variable(key, type(item), setter=setter, getter=getter)

        elif isinstance(item, (glm.mat4, glm.quat)):
            pass
        else:
            print('warning: unknown variable type {}'.format(type(item)))

    selected_gui = new_gui
    game.gui.update_layout()
    new_gui.set_position(game.width - new_gui.width - 10, 10)

    global property_window_helper
    property_window_helper = helper


# variables altered by the gui
box_speed = 0
gravity_enabled = False
bounce_enabled = False
draw_dots = False
selected_object = None
selected_gui = None
property_window_helper = None
dot = game.create_entity(**crate_attributes, scalar=glm.vec3(0.1, 0.1, 0.1), should_render=False)

# create the gui
helper = engine.FormHelper(game.gui)
gui_window = helper.add_window(10, 10, 'GUI WINDOW (heck yeah)')

# todo make you not have to declare everything as a variable (ie save a reference in helper and/or gui)
helper.add_group('box control')
helper.add_variable('speed', float, linked_var='box_speed')

helper.add_group('gravity')
helper.add_variable('enable gravity', bool, linked_var='gravity_enabled')
helper.add_variable('enable bouncing', bool, linked_var='bounce_enabled')
helper.add_variable('draw dots', bool, linked_var='draw_dots')
helper.add_button('reset', reset_camera)

game.gui.update_layout()


# @@@@@
# callbacks
def custom_key_callback(game, key, _scancode, action, _mods):
    if action != engine.KEY_PRESS:
        return

    if key == engine.KEY_Z:
        game.close()
    if key == engine.KEY_X:
        game.set_cursor_capture('disabled')
        game.camera.first_frame = True  # prevent the camera from jumping when switching between
        # normal and disabled without moving the mouse
    if key == engine.KEY_C:
        game.set_cursor_capture('normal')
    if key == engine.KEY_ESCAPE:
        select_entity(None)


def on_click(game, button, action, *_args, **_kwargs):
    if not (button == engine.MOUSE_LEFT and action == engine.MOUSE_PRESS):
        return

    entity = util.get_entity_at_pos(game, *game.cursor_location)
    if entity not in axes:  # todo have separate logic for this kind of thing. Maybe entity.on_click_in_editor()
        select_entity(entity)


def on_resize(game, *args):
    game.projection = glm.perspective(glm.radians(75), game.width / game.height, 0.01, 100)


game.resize_callback = on_resize
game.key_callback = custom_key_callback
game.mouse_button_callback = on_click

# @@@@@
# create crates
crates = []
for pos in cube_positions:
    crate = game.create_entity(**crate_attributes, position=pos, do_gravity=True, do_collisions=True)
    crates.append(crate)
floor_crate = game.create_entity(**crate_attributes, position=glm.vec3(0, -10, 0), scalar=glm.vec3(10, 1, 10),
                                 do_gravity=False, do_collisions=True)

# axes crates
crate_attributes['vert_path'] = 'shaders/axes.vert'
axes = [
    game.create_entity(**crate_attributes, should_render=False) for _ in range(3)
]


# @@@@@
# on_frame callbacks
def spin_crates(delta_t):
    for i, crate in enumerate(crates):
        angle = box_speed * delta_t * glm.radians(15 * (0 + 1))
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
        if not entity.do_gravity:
            continue

        entity.velocity += gravity * delta_t
        entity.position += entity.velocity * delta_t
        entity.set_transform_matrix(game)

        for other_entity in game.entities:
            if other_entity is entity:
                continue
            if two_cubes_intersect(entity, other_entity):
                # don't
                entity.position -= entity.velocity * delta_t
                entity.velocity = glm.vec3(0, 0, 0)
                if entity is selected_object:
                    entity.shader_program.set_value('highlightAmount', 0.6)
                break
        else:
            if entity is selected_object:
                selected_object.shader_program.set_value('highlightAmount', 0.3)

    if property_window_helper is not None:
        property_window_helper.refresh()


def on_frame_draw_axes(*_args):
    if selected_object is not None:
        draw_axes(selected_object)


game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)
game.add_callback('on_frame', draw_dots_on_corners)
game.add_callback('before_frame', on_frame_draw_axes)

game.run(True)
