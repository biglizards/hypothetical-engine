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


# variables altered by the gui
box_speed = 0
gravity_enabled = False

# create the gui
helper = engine.FormHelper(game.gui)
gui_window = helper.add_window(240, 10, 'GUI WINDOW (example)')

helper.add_group('gravity')
helper.add_variable('enable gravity', bool, linked_var='gravity_enabled')
helper.add_button('reset', reset_camera)
helper.add_button('save', lambda: save.save_level('save.json', game))


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

game.add_global_script(scripts.keys.CustomKeyPresses)
game.add_global_script(scripts.editor_scripts.EditorScripts)

load.load_level('save.json', game)

# crates = []
# dot = [x for x in game.entities if x.id == 'dot'][0]

make_entity_list()
# make_resource_list()

# todo make axis appear when you select an object

game.run(True)
