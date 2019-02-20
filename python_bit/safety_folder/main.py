import glm

import engine

import script
import scripts.editor_scripts
import scripts.keys
from editor import Editor, Drag
from enginelib.level import save
from enginelib.level import load
from physics import two_cubes_intersect


class CustomEditor(Editor, Drag, script.ScriptGame):
    pass


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
    dot = game.entities_by_id['dot']
    # i'm unpacking it for performance reasons
    proj_times_view = game.projection * game.camera.view_matrix()
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

path_box = engine.TextBox(parent=model_loader_window, value="resources/capsule/capsule.obj")
model_loader_window.fixed_width = 225

engine.Button("load model", parent=model_loader_window,
              callback=lambda: game.create_entity(model_path=path_box.value, id='new_model',
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
        name = entity.id if entity.id is not '' else f'{i}th entity'
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
                                    callback=print)
    game.gui.update_layout()


resource_images = engine.ImagePanel.load_images(game.gui, "resources")

game.gui.update_layout()


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


game.add_callback('on_frame', do_gravity)
game.add_callback('on_frame', draw_dots_on_corners)

game.add_global_script(scripts.keys.CustomKeyPresses)
game.add_global_script(scripts.editor_scripts.EditorScripts)

load.load_level('save.json', game)

# crates = []
# dot = [x for x in game.entities if x.id == 'dot'][0]

make_entity_list()
# make_resource_list()

# todo make axis appear when you select an object

game.run(True)
