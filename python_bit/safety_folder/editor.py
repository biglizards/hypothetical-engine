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
    def xyz_section(gui_window, vector, entity, key, helper, n=3):
        xyz_section = engine.Widget(gui_window, layout=engine.BoxLayout(orientation=0, spacing=6))
        gui_window.layout.append_row(0)
        gui_window.layout.set_anchor(xyz_section, engine.Anchor(1, gui_window.layout.row_count - 1, 3, 1))

        for i in range(n):
            def setter(new_val, i=i, key=key, entity=entity):  # the keyword args save the value (otherwise all
                entity.__dict__[key][i] = new_val              # functions would use the last value in the loop)

            def getter(i=i, key=key, entity=entity):
                return entity.__dict__[key][i]

            if n == 3:
                letter = ['x', 'y', 'z'][i]
                engine.Label(xyz_section, letter)
                width = 60
            else:
                width = 55
            box = engine.FloatBox(parent=xyz_section, value=vector[i], spinnable=(n == 3), callback=setter)
            box.font_size = 17.5
            helper.add_manual_getter(box, getter)  # todo refactor this mess out
            box.fixed_width = width
            box.alignment = 0  # todo replace with named constant (and/or thing in init)

    def populate_properties_window(self, entity: Entity, helper, widget):
        for key, item in entity.__dict__.items():  # key is name of attr, item is attr itself
            if key.startswith('_') or key in getattr(entity, 'property_blacklist', []):
                continue
            elif isinstance(item, glm.vec3):
                helper.add_group(key)
                self.xyz_section(widget, item, entity, key, helper)
            elif isinstance(item, glm.quat):
                helper.add_group(key)
                self.xyz_section(widget, item, entity, key, helper, n=4)
            elif isinstance(item, (int, float, bool, str)):
                # helper.add_group(key)

                def setter(new_val, _old_val, key=key, entity=entity):
                    entity.__dict__[key] = new_val

                def getter(key=key, entity=entity):
                    return entity.__dict__[key]

                helper.add_variable(key, type(item), setter=setter, getter=getter)

            elif isinstance(item, (glm.mat4, glm.quat)):  # ignore matrices and quaternions
                pass
            else:
                print(f'warning: unknown variable type {type(item)}: {key}')

    def create_object_gui(self, entity: Entity):
        """
        An entity in the editor has been clicked, so we need to make the property window for it
        1. if a property window already exists, delete it
        2. if the background was clicked, dont try to make a window for it
        3. iterate over the __dict__ of the object:
          a. if it starts with _ or is on the blacklist, ignore it
          b. if the type matches something we have a handler for, use that handler
            i. this uses the 'helper's advanced grid layout
          c. raise a warning if no handler is found
        4. iterate over the scripts of the object:
          a. create a popup button
          b. iterate over the __dict__ of the script:
            i. if it starts with _ or is on the blacklist, ignore it
            ii. if the type matches something we have a handler for, use that handler
                (this uses the layout of the popup, usually a GridLayout)
            iii. raise a warning if no handler is found
        """
        if self.selected_gui is not None:
            self.selected_gui.dispose()
            self.selected_gui = None
            self.property_window_helper = None
        if entity is None:
            return

        # create the helper
        helper = engine.FormHelper(self.gui)
        new_gui = helper.add_window(0, 0, 'entity properties')

        # swap the layout to a GroupLayout
        layout = new_gui.layout
        new_gui.layout = engine.GroupLayout(margin=0, spacing=0)
        # wrap the window in a scroll panel
        scroll_panel_holder = engine.ScrollPanel(new_gui)
        scroll_panel_holder.fixed_height = (self.height-30) * 0.9
        scroll_panel = engine.Widget(scroll_panel_holder, layout=engine.GroupLayout(margin=0, spacing=0))
        # create the two main segments for the window: the helper bit with all the attributes in,
        # and the scripts section with all the scripts in
        helper_section = engine.Widget(scroll_panel, layout=layout)  # uses AdvancedLayout from earlier
        # the helper_section layout also has a margin of 10, so we set that here so they match
        script_section = engine.Widget(scroll_panel, layout=engine.GroupLayout(margin=10))
        # set the helpers "window" to the correct widget
        helper.set_window_unsafe(helper_section)

        self.populate_properties_window(entity, helper, widget=helper_section)

        engine.Label(caption="Scripts", parent=script_section, font_size=20)
        for script in entity.scripts:
            # create popup button
            popup_button = engine.PopupButton(parent=script_section, caption="popup", side=0)
            advanced_layout = engine.AdvancedGridLayout([10, 0, 10, 0])
            popup_button.popup.layout = advanced_layout
            # populate popup with properties
            helper.set_window_unsafe(popup_button.popup)
            self.populate_properties_window(script, helper, popup_button.popup)
            # add "remove" button
            advanced_layout.append_row()
            spacer = engine.Widget(parent=popup_button.popup)
            spacer.fixed_height = 10
            advanced_layout.set_anchor(spacer, engine.Anchor(1, advanced_layout.row_count - 1, 3, 1))
            advanced_layout.append_row()
            delete_button = engine.Button(name="delet this", parent=popup_button.popup, callback=script.remove)
            advanced_layout.set_anchor(delete_button, engine.Anchor(1, advanced_layout.row_count - 1, 1, 1))


        # end bit
        self.selected_gui = new_gui
        self.gui.update_layout()
        new_gui.set_position(self.width - new_gui.width - 10, 10)
        new_gui.fixed_width = new_gui.width

        self.property_window_helper = helper

    def create_entity(self, *args, entity_class=Entity, **kwargs):
        entity = super().create_entity(*args, entity_class=entity_class, **kwargs)
        entity._args = args
        entity._kwargs = kwargs
        return entity

    def create_script(self, entity, script_class, *args, **kwargs):
        script = super(Editor, self).create_script(entity=entity, script_class=script_class, *args, **kwargs)
        script._args = args
        script._kwargs = kwargs
        return script


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
