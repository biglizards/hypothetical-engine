import glm
import random

import engine

import script
import util
from cube import data
from editor import Editor, Drag
from game import ManualEntity
from physics import two_cubes_intersect
import scripts.keys


class CustomEditor(Editor, Drag, script.ScriptGame):
    pass


class Axis(ManualEntity):
    clickable = False

    def __init__(self, *args, game, data, unit_vector, **kwargs):
        # awful hack to set the origin in the right place, todo remove when you add model loading
        # convert the unit vector into an index (ie x: 0, y:1, z:2)
        index = int(glm.length(glm.vec4(0, 1, 2, 1) * unit_vector))
        # mutate the data so the origin of the object is in the centre.
        data = [d + (0.5 if i % 5 == index else 0) for i, d in enumerate(data)]

        super().__init__(*args, game, data, **kwargs)
        self.game = game
        self.unit_vector = unit_vector
        self.scalar = glm.vec3(0.10, 0.10, 0.10) + (unit_vector.xyz * 0.9)
        self.parent = None
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False
        # set callbacks
        game.add_callback('on_drag_update', self.move_axis)
        game.add_callback('on_click_entity', self.set_drag_start_pos)
        game.add_callback('on_drag', self.reset_variables)  # once the drag finishes, reset everything to none
        game.add_callback('before_frame', self.update_variables)

    def reset_variables(self, *_args):
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False

    def update_variables(self, *_args):
        if self.parent is not None:
            self.position = self.parent.position
            self.orientation = self.parent.orientation
            self.should_render = True

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
        return glm.normalize(glm.vec3(self.parent.model_mat * self.unit_vector))

    def move_axis(self, *mouse_pos):
        if not self.is_dragging:
            return None
        target = util.get_point_closest_to_cursor(game, self.parent_start_pos, self.vector(), mouse_pos)

        true_target = target + self.offset
        self.parent.position = true_target


game = CustomEditor()


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
            transformation_matrix = proj_times_view * dot.generate_model_mat()
            dot.shader_program.set_trans_mat(transformation_matrix)
            dot.draw()


# variables altered by the gui
box_speed = 0
gravity_enabled = False
bounce_enabled = False
draw_dots = False

# create the gui
# helper = engine.FormHelper(game.gui)
# gui_window = helper.add_window(10, 10, 'GUI WINDOW (example)')
#
# helper.add_group('box control')
# helper.add_variable('speed', float, linked_var='box_speed')
#
# helper.add_group('gravity')
# helper.add_variable('enable gravity', bool, linked_var='gravity_enabled')
# helper.add_variable('enable bouncing', bool, linked_var='bounce_enabled')
# helper.add_variable('draw dots', bool, linked_var='draw_dots')
# helper.add_button('reset', reset_camera)

# ######
# new custom gui
new_gui_window = engine.GuiWindow(100, 100, "steve", gui=game.gui, layout=engine.GroupLayout())
engine.Label(new_gui_window, "Some example buttons")
new_widget = engine.Widget(new_gui_window, layout=engine.BoxLayout(orientation=0, spacing=6))
engine.Button("info", lambda: print("pressed!"), parent=new_widget)
engine.Button("warn", lambda: print("pressed!"), parent=new_widget)
engine.Button("ask", lambda: print("pressed!"), parent=new_widget)
a = engine.TextBox(parent=new_gui_window, value="Ya mum", callback=lambda x: setattr(b, "editable", True))
b = engine.FloatBox(parent=new_gui_window, value=3.14159)
b.callback = lambda x: print("float", x)
b.spinnable = True
b.editable = False
a.spinnable = "False"
a.value = "foobar"
b.value = 34.99
print(type(b.value), b.value)

game.gui.update_layout()

# @@@@@
# create crates
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
crate_attributes = {
    'data': data, 'indices': None, 'data_format': (3, 2),
    'textures': [('resources/container.jpg', 'container'), ('resources/duck.png', 'face')],
    'vert_path': 'shaders/perspective.vert', 'frag_path': 'shaders/highlight.frag', 'entity_class': ManualEntity
}

# for x in range(1500):
#     cube_positions.append(glm.vec3((-0.5)*40, (-0.5)*40, (-0.5)*40))

crates = []
for pos in cube_positions:
    crate = game.create_entity(**crate_attributes, position=pos, do_gravity=True, do_collisions=True)
    crates.append(crate)
floor_crate = game.create_entity(**crate_attributes, position=glm.vec3(0, -10, 0), scalar=glm.vec3(10, 1, 10),
                                 do_gravity=False, do_collisions=True)

dot = game.create_entity(**crate_attributes, scalar=glm.vec3(0.1, 0.1, 0.1), should_render=False)

# axes crates
crate_attributes['vert_path'] = 'shaders/axes.vert'
crate_attributes['entity_class'] = Axis
unit_vectors = [glm.vec4(1, 0, 0, 0), glm.vec4(0, 1, 0, 0), glm.vec4(0, 0, 1, 0)]

axes = [
    game.create_entity(**crate_attributes, should_render=False,
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
        entity.set_transform_matrix()

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


game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)
game.add_callback('on_frame', draw_dots_on_corners)

game.add_global_script(scripts.keys.CustomKeyPresses)

#test_model = game.create_entity(model_path="/home/dave/git/LearnOpenGL/resources/objects/bc/Sketchfab_2017_02_12_14_36_10.obj",
#                   vert_path='shaders/fuckme.vert', frag_path='shaders/highlight.frag')

game.run(True)
