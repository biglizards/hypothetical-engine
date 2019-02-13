import glm

import engine

import util
from game import Game, Entity


class Click(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_callback('on_click', self.dispatch_click_entity)

    def dispatch_click_entity(self, button, action, *_args, **_kwargs):
        if not (button == engine.MOUSE_LEFT and action == engine.MOUSE_PRESS):
            return

        entity = util.get_entity_at_pos(self, *self.cursor_location)
        self.dispatch('on_click_entity', entity)


class Editor(Click, Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_object = None
        self.selected_gui = None
        self.property_window_helper = None
        self.add_callback('on_click_entity', self.on_entity_click)

    def on_entity_click(self, entity):
        if util.is_clickable(entity):
            self.select_entity(entity)
        # todo have separate logic for axes etc. Maybe entity.on_click_in_editor()

    def select_entity(self, entity: Entity or None):
        target_entity = entity
        self.change_highlighted_object(target_entity)
        self.create_object_gui(target_entity)

    def change_highlighted_object(self, entity: Entity):
        if self.selected_object is not None:
            self.selected_object.shader_program.set_value('highlightAmount', 0.0)
        if entity is not None:
            entity.shader_program.set_value('highlightAmount', 0.3)
        self.selected_object = entity

    @staticmethod
    def xyz_section(gui_window, vector, entity, key, helper):
        xyz_section = engine.Widget(gui_window, layout=engine.BoxLayout(orientation=0, spacing=6))
        gui_window.layout.append_row(0)
        gui_window.layout.set_anchor(xyz_section, engine.Anchor(1, gui_window.layout.row_count - 1, 3, 1))

        for i in range(3):
            def setter(new_val, i=i, vector=vector):  # the keyword args save the value (otherwise all
                vector[i] = new_val                   # functions would use the last value in the loop)

            def getter(i=i, key=key, entity=entity):
                return entity.__dict__[key][i]

            letter = ['x', 'y', 'z'][i]
            engine.Label(xyz_section, letter)
            box = engine.FloatBox(parent=xyz_section, value=vector[i], spinnable=True, callback=setter)
            helper.add_manual_getter(box, getter)  # todo refactor this mess out
            box.fixed_width = 60
            box.alignment = 0  # todo replace with named constant (and/or thing in init)

    def create_object_gui(self, entity: Entity):
        # todo wrap and use advanced grid layout to get the x, y, z things all on one line
        # https://nanogui.readthedocs.io/en/latest/api/class_nanogui__AdvancedGridLayout.html#class-nanogui-advancedgridlayout
        if self.selected_gui is not None:
            self.selected_gui.dispose()
            self.selected_gui = None
        if entity is None:
            return

        helper = engine.FormHelper(self.gui)
        new_gui = helper.add_window(640, 10, 'entity properties')

        for key, item in entity.__dict__.items():  # key is name of attr, item is attr itself
            if key.startswith('_'):
                continue
            if isinstance(item, glm.vec3):
                helper.add_group(key)
                self.xyz_section(new_gui, item, entity, key, helper)
            elif isinstance(item, (int, float, bool, str)):
                helper.add_group(key)

                def setter(new_val, _old_val, key=key, entity=entity):
                    entity.__dict__[key] = new_val

                def getter(key=key, entity=entity):
                    return entity.__dict__[key]

                helper.add_variable(key, type(item), setter=setter, getter=getter)

            elif isinstance(item, (glm.mat4, glm.quat)):  # ignore matrices and quaternions
                pass
            else:
                print('warning: unknown variable type {}'.format(type(item)))

        self.selected_gui = new_gui
        self.gui.update_layout()
        new_gui.set_position(self.width - new_gui.width - 10, 10)
        new_gui.fixed_width = new_gui.width

        self.property_window_helper = helper


class Drag(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dragging = False
        self.holding_mouse_button = False
        self.drag_start = None
        self.add_callback('on_click', self.dragger_on_click)
        self.add_callback('on_cursor_pos_update', self.on_cursor_location_update)

    def dragger_on_click(self, button, action, _mods, *_args):
        if button != engine.MOUSE_LEFT:
            return
        if action == engine.MOUSE_CLICK:
            assert self.is_dragging is False, "somehow user clicked while already dragging"
            self.holding_mouse_button = True
            self.drag_start = self.cursor_location
        elif action == engine.MOUSE_RELEASE:
            if self.is_dragging:
                self.dispatch('on_drag', self.drag_start, self.cursor_location)
            # reset values to defaults, since the drag is over
            self.is_dragging = False
            self.holding_mouse_button = False
            self.drag_start = None

    def on_cursor_location_update(self, *mouse_pos):
        should_start_drag = self.holding_mouse_button and not self.is_dragging
        if should_start_drag and mouse_pos != self.drag_start:
            self.is_dragging = True
        if self.is_dragging:
            self.dispatch('on_drag_update', *mouse_pos)
