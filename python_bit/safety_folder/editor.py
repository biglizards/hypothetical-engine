import glm
import importlib
import os
from warnings import warn

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
        self.models = {}
        self.scripts = {}
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
    def xyz_section(gui_window, vector, entity, key, helper, width=60):
        xyz_section = engine.Widget(gui_window, layout=engine.BoxLayout(orientation=0, spacing=6))
        gui_window.layout.append_row(0)
        gui_window.layout.set_anchor(xyz_section, engine.Anchor(1, gui_window.layout.row_count - 1, 3, 1))

        for i, value in enumerate(vector):
            def setter(new_val, i=i, key=key, entity=entity):  # the keyword args save the value (otherwise all
                entity.__dict__[key][i] = new_val              # functions would use the last value in the loop)

            def getter(i=i, key=key, entity=entity):
                return entity.__dict__[key][i]

            if len(vector) <= 3:  # sometimes, eg quats, it's more, but there's not enough space for labels then
                letter = ['x', 'y', 'z'][i]
                engine.Label(xyz_section, letter)
            box = engine.FloatBox(parent=xyz_section, value=value, spinnable=(len(vector) <= 3), callback=setter)
            box.font_size = 17.5
            helper.add_manual_getter(box, getter)  # todo refactor this mess out
            box.fixed_width = width
            box.alignment = 0  # todo replace with named constant (and/or thing in init)

    def populate_properties_window(self, entity: Entity, helper, widget):
        if isinstance(entity, Entity):  # scripts also use this, so we need to check it's an entity
            # add 'id' at the top (it's a property so i need to do this manually)
            helper.add_variable('id', str, setter=lambda x, _: setattr(entity, 'id', x),
                                getter=lambda: entity.id)

        for key, item in entity.__dict__.items():  # key is name of attr, item is attr itself
            if key.startswith('_') or key in getattr(entity, 'property_blacklist', []):
                continue
            elif isinstance(item, glm.vec3):
                helper.add_group(key)
                self.xyz_section(widget, item, entity, key, helper)
            elif isinstance(item, glm.quat):
                helper.add_group(key)
                self.xyz_section(widget, item, entity, key, helper, width=54)
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
                warn(f'warning: unknown variable type {type(item)}: {key}', RuntimeWarning)

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
          b. iterate over the __dict__ of the script, same as 3.
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

        if entity.model_path is not None:
            engine.Label(caption="Model", parent=script_section, font_size=20)
            engine.Label(caption=entity.model_path, parent=script_section)
            model_changer = engine.PopupButton(caption="Change Model", parent=script_section, side=0)
            self.make_model_editor(entity, model_changer.popup)

        engine.Button(parent=script_section, name="delet this", callback=lambda: self.remove_entity(entity))

        engine.Label(caption="Scripts", parent=script_section, font_size=20)
        script_adder = engine.PopupButton(caption="Add script", parent=script_section, side=0)
        self.make_script_adder(entity, script_adder.popup)
        for script in entity.scripts:
            # create popup button
            popup_button = engine.PopupButton(parent=script_section, caption=script.__class__.__name__, side=0)
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
            delete_button = engine.Button(name="delet this", parent=popup_button.popup,
                                          callback=lambda: (script.remove(), self.create_object_gui(entity)))
            advanced_layout.set_anchor(delete_button, engine.Anchor(1, advanced_layout.row_count - 1, 1, 1))

        # end bit
        self.selected_gui = new_gui
        self.gui.update_layout()
        new_gui.set_position(self.width - new_gui.width - 10, 10)
        new_gui.fixed_width = new_gui.width

        self.property_window_helper = helper

    @staticmethod
    def make_resource_list(window, width=255, height=100):
        def update_resource_list(text):
            if text == '':
                for button in scroll_panel.children:
                    button.visible = True
                return
            for button in scroll_panel.children:
                button.visible = text.lower() in button.text.lower()

        window.layout = engine.GroupLayout()
        if width > 0:
            window.fixed_width = width
        if height > 0:
            window.fixed_height = height
        _search_box = engine.TextBox(parent=window, placeholder="search box",
                                     callback=update_resource_list)

        scroll_panel_holder = engine.ScrollPanel(window)
        scroll_panel = engine.Widget(scroll_panel_holder, layout=engine.GroupLayout())
        return scroll_panel

    def make_script_adder(self, entity, window):
        def import_script(path=None, name=None):
            module = importlib.import_module(path)
            self.create_script(entity, getattr(module, name))
            self.create_object_gui(entity)

        engine.Button(name="Import new script", parent=window,
                      callback=lambda: self.make_file_import(callback=import_script,
                                                             path_placeholder='scripts.module',
                                                             name_placeholder='ScriptClassName', use_button=False))

        scroll_panel = self.make_resource_list(window, height=200)
        for cls, name in self.scripts.items():
            # engine.Label(caption=f"{x}th button", parent=scroll_panel)
            name = name if name is not None else cls.__name__
            button = engine.Button(name, parent=scroll_panel,
                                   callback=lambda: (self.create_script(entity, cls),
                                                     self.create_object_gui(entity))
                                   )
            button.fixed_height = 20

        return window

    def make_model_editor(self, entity, window):
        def set_entity_model(path=None, name=None):
            if path == '':
                return None
            entity.meshes = engine.load_model(path)
            entity.model_path = path
            if path not in self.models:
                self.models[path] = name
            self.create_object_gui(entity)  # reload properties menu

        engine.Button(name="import new model", parent=window,
                      callback=lambda: self.make_file_import(callback=set_entity_model,
                                                             path_placeholder='path/to/file',
                                                             name_placeholder='model name'))

        scroll_panel = self.make_resource_list(window, width=-1, height=-1)
        for path, name in self.models.items():
            # engine.Label(caption=f"{x}th button", parent=scroll_panel)
            name = name if name is not None else path
            button = engine.Button(name, parent=scroll_panel, callback=lambda path_=path: set_entity_model(path_))
            button.fixed_height = 20

        return window

    def make_file_import(self, callback=None, name="file loader", path_placeholder='', name_placeholder='',
                         use_button=True):
        def set_file_path(path):
            if path == '':
                return None
            path_box.value = os.path.relpath(path)
            if name_box.value == '':
                name_box.value = os.path.basename(path)

        window = engine.GuiWindow(self.width//2-125, self.height//2-80,
                                  name, gui=self.gui, layout=engine.GroupLayout())
        window.fixed_width = 250
        if use_button:
            engine.Button(parent=window, name="open file", callback=lambda: set_file_path(engine.file_dialog(True)))
        path_box = engine.TextBox(parent=window, value="", placeholder=path_placeholder)
        name_box = engine.TextBox(parent=window, value="", placeholder=name_placeholder)

        button_section = engine.Widget(parent=window, layout=engine.BoxLayout(orientation=0, spacing=90))
        engine.Button(parent=button_section, name="cancel", callback=window.dispose)
        engine.Button(parent=button_section, name="apply",
                      callback=lambda: (callback(path=path_box.value, name=name_box.value),
                                        window.dispose()))

    def create_entity(self, *args, entity_class=Entity, **kwargs):
        if kwargs.get('model_path') and kwargs.get('model_path') not in self.models:
            self.models[kwargs.get('model_path')] = None

        entity = super().create_entity(*args, entity_class=entity_class, **kwargs)
        entity._args = args
        entity._kwargs = kwargs
        return entity

    def remove_entity(self, entity):
        super().remove_entity(entity)
        if self.selected_object is entity:
            self.select_entity(None)

    def create_script(self, entity, script_class, *args, **kwargs):
        if script_class not in self.scripts:
            self.scripts[script_class] = None
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
