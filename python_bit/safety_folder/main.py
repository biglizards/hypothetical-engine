import glm
import engine

import script
import util
from cube import data
from game import Entity
from editor import Editor, Drag
from physics import two_cubes_intersect
import scripts.keys


class CustomEditor(Editor, Drag, script.ScriptGame):
    pass


class Axis(Entity):
    clickable = False

    def __init__(self, *args,  unit_vector, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_vector = unit_vector
        self.parent = None
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False
        # set callbacks
        game.add_callback('on_drag_update', self.move_axis)
        game.add_callback('on_click_entity', self.set_drag_start_pos)
        game.add_callback('on_drag', self.reset_variables)  # once the drag finishes, reset everything to none

    def reset_variables(self, *_args):
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False

    def set_drag_start_pos(self, entity):
        if entity is self:
            self.is_dragging = True
            drag_start_pos = util.get_point_closest_to_cursor(game, self.position,
                                                              self.vector(), self.game.cursor_location)
            self.offset = self.parent.position - drag_start_pos
            self.parent_start_pos = self.parent.position
        elif util.is_clickable(entity):  # todo maybe replace with entity is game.selected_object
            self.parent = entity
        if entity is None:
            self.should_render = False

    def vector(self):
        return glm.normalize(glm.vec3(self.parent.model * self.unit_vector))

    def move_axis(self, *mouse_pos):
        if not self.is_dragging:
            return None
        target = util.get_point_closest_to_cursor(game, self.parent_start_pos, self.vector(), mouse_pos)

        true_target = target + self.offset
        self.parent.position = true_target


game = CustomEditor()

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
        axis.should_render = True


# variables altered by the gui
box_speed = 0
gravity_enabled = False
bounce_enabled = False
draw_dots = False
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
# todo make this standard (but overridable/configurable ofc)
def on_resize(*_args, game=game):
    game.projection = glm.perspective(glm.radians(75), game.width / game.height, 0.01, 100)


game.add_callback('on_resize', on_resize)
game.add_global_script(scripts.keys.CustomKeyPresses)
game.add_global_script(scripts.keys.CustomKeyPresses)

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
unit_vectors = [glm.vec4(1, 0, 0, 0), glm.vec4(0, 1, 0, 0), glm.vec4(0, 0, 1, 0)]

axes = [
    game.create_entity(**crate_attributes, should_render=False, entity_class=Axis,
                       unit_vector=unit_vector) for unit_vector in unit_vectors
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
                if entity is game.selected_object:
                    entity.shader_program.set_value('highlightAmount', 0.6)
                break
        else:
            if entity is game.selected_object:
                game.selected_object.shader_program.set_value('highlightAmount', 0.3)

    try:
        game.property_window_helper.refresh()
    except AttributeError:
        pass


def on_frame_draw_axes(*_args):
    if game.selected_object is not None:
        draw_axes(game.selected_object)


game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)
game.add_callback('on_frame', draw_dots_on_corners)
game.add_callback('before_frame', on_frame_draw_axes)

game.run(True)
