import glm

import engine

import script
import scripts.editor_scripts
import scripts.keys
import util
from editor import Editor, Drag
from enginelib.level import save
from enginelib.level import load
from game import ManualEntity
from physics import two_cubes_intersect


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
helper = engine.FormHelper(game.gui)
gui_window = helper.add_window(10, 10, 'GUI WINDOW (example)')

helper.add_group('box control')
helper.add_variable('speed', float, linked_var='box_speed')

helper.add_group('gravity')
helper.add_variable('enable gravity', bool, linked_var='gravity_enabled')
helper.add_variable('enable bouncing', bool, linked_var='bounce_enabled')
helper.add_variable('draw dots', bool, linked_var='draw_dots')
helper.add_button('reset', reset_camera)
helper.add_button('save', lambda: save.save_level('save.json', game))

# ######
# new custom gui
model_loader_window = engine.GuiWindow(185, 10, "model loader 4000", gui=game.gui, layout=engine.GroupLayout())

path_box = engine.TextBox(parent=model_loader_window, value="resources/")
model_loader_window.fixed_width = 225

engine.Button("load model", parent=model_loader_window,
              callback=lambda: game.create_entity(model_path=path_box.value,
                                                  vert_path='shaders/fuckme.vert', frag_path='shaders/highlight.frag'))


def make_entity_list():
    entity_list_window = engine.GuiWindow(185, 135, "entity list 3000", gui=game.gui, layout=engine.GroupLayout())
    entity_list_window.fixed_width = 225
    scroll_panel_holder = engine.ScrollPanel(entity_list_window)
    scroll_panel = engine.Widget(scroll_panel_holder, layout=engine.GroupLayout())
    scroll_panel.fixed_height = 1000
    scroll_panel_holder.fixed_height = 100

    for i, entity in enumerate(game.entities):
        # engine.Label(caption=f"{x}th button", parent=scroll_panel)
        name = entity.name if entity.name is not '' else f'{i}th entity'
        button = engine.Button(name, lambda target=entity: game.select_entity(target), parent=scroll_panel)
        button.fixed_height = 20

    game.gui.update_layout()


def make_resource_list():
    entity_list_window = engine.GuiWindow(185, 135, "resource list 6000", gui=game.gui, layout=engine.GroupLayout())
    entity_list_window.fixed_width = 500

    def update_resource_list(text):
        if text == '':
            image_panel.images = resource_images
            return
        text = text.encode()  # todo remove
        image_panel.images = [x for x in resource_images if text in x[1]]

    _search_box = engine.TextBox(parent=entity_list_window, placeholder="search box",
                                 callback=update_resource_list)

    scroll_panel_holder = engine.ScrollPanel(entity_list_window)
    scroll_panel = engine.Widget(scroll_panel_holder, layout=engine.GroupLayout())
    scroll_panel.fixed_height = 1000
    scroll_panel_holder.fixed_height = 200

    image_panel = engine.ImagePanel(parent=scroll_panel, images=resource_images,
                                    callback=lambda x: print(x))
    game.gui.update_layout()


resource_images = engine.ImagePanel.load_images(game.gui, "resources")

game.gui.update_layout()


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


game.add_callback('on_frame', spin_crates)
game.add_callback('on_frame', do_gravity)
game.add_callback('on_frame', draw_dots_on_corners)

game.add_global_script(scripts.keys.CustomKeyPresses)
game.add_global_script(scripts.editor_scripts.EditorScripts)

make_entity_list()
make_resource_list()
load.load_level('save.json', game)
crates = []
dot = [x for x in game.entities if x.name == 'dot'][0]

game.run(True)
