import glm
import importlib
import os
from warnings import warn

import engine
import openal

from enginelib import util
from enginelib.level import save, load
from enginelib.entity import Entity
from enginelib.game import Game


class Click(Game):
    """a mixin that detects when a given entity is clicked on, and dispatches an event"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_callback('on_click', self.dispatch_click_entity, always_fire=True)

    def dispatch_click_entity(self, button, action, *_args, **_kwargs):
        if not (button == engine.MOUSE_LEFT and action == engine.MOUSE_PRESS):
            return

        entity = util.get_entity_at_pos(self, *self.cursor_location)
        self.dispatch('on_click_entity', entity)


class Drag(Game):
    """a mixin that adds a callback for clicking and dragging the mouse"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dragging = False
        self.holding_mouse_button = False
        self.drag_start = None
        self.add_callback('on_click', self.dragger_on_click, always_fire=True)
        self.add_callback('on_cursor_pos_update', self.on_cursor_location_update, always_fire=True)

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


# noinspection PyShadowingNames
class Editor(Click, Drag):
    """The main editor class. Contains A LOT of GUI code"""
    def __init__(self, *args, **kwargs):
        self.mode = 'editor'
        self.selected_object = None
        self.selected_gui = None
        self.property_window_helper = None
        self.entity_list_scroll_panel = None
        self.entity_list_buttons_by_id = {}

        self.models = {}
        self.scripts = {}
        self.entity_classes = {}
        self.audio = {}
        self.frag_shaders = {}
        self.vert_shaders = {}

        super().__init__(*args, **kwargs)

        self.add_callback('on_click_entity', self.on_entity_click, editor=True)

        self.add_global_script(load.loader.load_class('enginelib.editor_scripts', 'EditorScripts'))
        self.make_entity_list()
        self.create_tool_window()

        self.gui.update_layout()

    def dispatch(self, name: str, *args):
        """calls all functions registered as listening to a given hook"""
        # call the functions which should fire even in editor mode
        funcs = self.dispatches.get(name, [])
        for func in funcs:
            if self.should_run_function(func):
                try:
                    func(*args)
                except Exception as e:
                    self.on_error(e)

    def should_run_function(self, func):
        if self.mode == 'game':
            return not (hasattr(func, 'hook_args') and func.hook_args.get('editor'))
        elif self.mode == 'editor':
            return hasattr(func, 'hook_args') and (func.hook_args.get('editor') or func.hook_args.get('always_fire'))

    def hard_reload_level(self):
        while self.entities:
            self.remove_entity(self.entities[0])
        while self.overlay_entities:
            self.remove_entity(self.overlay_entities[0])
        # reload all the modules
        self.scripts = {}
        self.entity_classes = {}

        load.load_level(self.save_name, game=self)

    def soft_reload_level(self):
        load.loader.reload()
        self.entity_classes = {load.loader.get_newer_class(cls): val for cls, val in self.entity_classes.items()}

    def toggle_mode(self):
        self.mode = 'game' if self.mode == 'editor' else 'editor'
        self.dispatch('on_mode_change', self.mode)
        self.dispatch('on_game_start')

    def create_entity(self, *args, entity_class=Entity, **kwargs):
        if kwargs.get('model_path') and kwargs.get('model_path') not in self.models:
            self.models[kwargs.get('model_path')] = None  # none means "no custom name set"
        if entity_class not in self.entity_classes:
            self.entity_classes[entity_class] = None  # none means "no custom name set"

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
            self.scripts[script_class] = None  # none means "no custom name set"
        # script = super(Editor, self).create_script(entity=entity, script_class=script_class, *args, **kwargs)
        script = Entity.super(self, Editor).create_script(self, entity=entity, script_class=script_class, *args, **kwargs)
        script._args = args
        script._kwargs = kwargs
        return script

    def on_entity_click(self, entity):
        if util.is_clickable(entity):
            self.select_entity(entity)

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

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # all code below this point is GUI creation code
    # it's not very good, but that's because it is impossible to write nice looking GIU creation code
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    @staticmethod
    def xyz_section(gui_window, vector, entity, key, helper, width=60):
        """creates a section for editing the individual components of a vector"""
        xyz_section = engine.Widget(parent=gui_window, layout=engine.BoxLayout(orientation=0, spacing=6))
        with xyz_section:
            gui_window.layout.append_row(0)
            gui_window.layout.set_anchor(xyz_section, engine.Anchor(1, gui_window.layout.row_count - 1, 3, 1))

            for i, value in enumerate(vector):
                def setter(new_val, i=i, key=key, entity=entity):  # the keyword args save the value (otherwise all
                    entity.__dict__[key][i] = new_val              # functions would use the last value in the loop)

                def getter(i=i, key=key, entity=entity):
                    return entity.__dict__[key][i]

                if len(vector) <= 3:  # sometimes, eg quats, it's more, but there's not enough space for labels then
                    letter = ['x', 'y', 'z'][i]
                    engine.Label(letter)
                box = engine.FloatBox(value=value, callback=setter, spinnable=(len(vector) <= 3),
                                      font_size=17.5, fixed_width=width, alignment=0)
                helper.add_manual_getter(box, getter)

    def populate_properties_window(self, entity: Entity, helper, widget):
        """iterates over all attributes of an entity, and creates GUI widgets for displaying/editing them"""
        ignore_types = (openal.ctypes.c_uint, openal.Buffer, glm.mat4, glm.quat)

        if isinstance(entity, Entity):  # scripts also use this, so we need to check it's an entity
            helper.add_group(f'Entity class: {entity.__class__.__name__}')
            # add 'id' at the top (it's a property so i need to do this manually)
            helper.add_variable('id', str, setter=lambda x, _: setattr(entity, 'id', x),
                                getter=lambda: entity.id)

        for key, item in entity.__dict__.items():  # key is name of attr, item is attr itself
            if key.startswith('_') or key in getattr(entity, 'property_blacklist', []):
                continue
            elif isinstance(item, glm.vec3) or (isinstance(item, tuple) and len(item) == 3):
                helper.add_group(key)
                self.xyz_section(widget, item, entity, key, helper, width=60)
            elif isinstance(item, glm.quat):
                helper.add_group(key)
                self.xyz_section(widget, item, entity, key, helper, width=54)
            elif isinstance(item, (int, float, bool, str)):
                # helper.add_group(key)

                def setter(new_val, _old_val, key=key, entity=entity):
                    # entity.__dict__[key] = new_val
                    # i remember there was some kind of bug where the above didnt work,
                    # but i cant figure out what it was
                    # i guess it bypasses __setattr__ but i dont want that
                    setattr(entity, key, new_val)

                def getter(key=key, entity=entity):
                    return entity.__dict__[key]

                helper.add_variable(key, type(item), setter=setter, getter=getter)

            elif isinstance(item, ignore_types):  # ignore matrices and quaternions
                pass
            else:
                warn(f"warning: unknown variable type {type(item)} found in attribute '{key}' of {entity}", RuntimeWarning)

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
        5. Special cases for audio and shaders
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
        old_layout = new_gui.layout
        new_gui.layout = engine.GroupLayout(margin=0, spacing=0)
        # wrap the window in a scroll panel
        scroll_panel_holder = engine.ScrollPanel(new_gui, fixed_height=(self.height-30) * 0.9)
        scroll_panel = engine.Widget(scroll_panel_holder, layout=engine.GroupLayout(margin=0, spacing=0))
        # create the two main segments for the window: the helper bit with all the attributes in,
        # and the scripts section with all the scripts in
        helper_section = engine.Widget(scroll_panel, layout=old_layout)  # uses AdvancedLayout from earlier
        # the helper_section layout also has a margin of 10, so we set that here so they match
        script_section = engine.Widget(scroll_panel, layout=engine.GroupLayout(margin=10))
        # set the helpers "window" to the correct widget
        helper.set_window_unsafe(helper_section)

        self.populate_properties_window(entity, helper, widget=helper_section)

        with script_section:
            if entity.model_path is not None:
                engine.Label("Model", font_size=20)
                # get the model name
                model_name = self.models.get(entity.model_path)
                model_name = model_name if model_name is not None else entity.model_path
                engine.Label(f'selected: {model_name}')
                model_changer = engine.PopupButton("Change Model", side=0)
                self.make_model_editor(entity, model_changer.popup)

            engine.Button("delete this", callback=lambda: self.remove_entity(entity))

            engine.Label("Scripts", font_size=20)
            script_adder = engine.PopupButton("Add script", side=0)
            self.make_script_adder(entity, script_adder.popup)
            for script in entity.scripts:
                self.make_property_edit_button(caption=script.__class__.__name__, helper=helper,
                                               entity=entity, thing=script, remove_callback=script.remove)

            if hasattr(entity, 'audio_sources'):
                engine.Label("Audio", font_size=20)
                audio_adder = engine.PopupButton("Add audio", side=0)
                self.make_audio_adder(entity, window=audio_adder.popup)
                for name, source in entity.audio_sources.items():
                    self.make_property_edit_button(caption=name, helper=helper, entity=entity, thing=source,
                                                   remove_callback=lambda name_=name: entity.remove_audio(name_))

            # keep shaders at the bottom
            shader_adder = engine.PopupButton("Configure Shaders", side=0)
            with shader_adder.popup:
                shader_adder.popup.layout = engine.GroupLayout()
                a = engine.PopupButton("Vertex", side=0)
                self.make_shader_adder(entity, window=a.popup, shader_type='vert_path', asset_dict=self.vert_shaders)
                b = engine.PopupButton("Fragment", side=0)
                self.make_shader_adder(entity, window=b.popup, shader_type='frag_path', asset_dict=self.frag_shaders)
                # self.make_shader_adder(entity, window=engine.PopupButton("Geometry", side=0).popup, shader_type='geo_path')
            # self.make_shader_adder(entity, window=shader_adder.popup, shader_type='vert_path')
            # self.make_audio_adder(entity, window=audio_adder.popup)
            # for name, source in entity.audio_sources.items():
            #     self.make_property_edit_button(caption=name, helper=helper, entity=entity, thing=source,
            #                                    remove_callback=lambda name_=name: entity.remove_audio(name_))

        # end bit
        self.selected_gui = new_gui
        self.gui.update_layout()
        # put the window on the right hand side, with a bit of breathing room
        new_gui.set_position(self.width - new_gui.width - 10, 10)
        new_gui.fixed_width = new_gui.width

        self.property_window_helper = helper

    def make_resource_list(self, window, width=255, height=100):
        def update_resource_list(text):
            if text == '':
                for button in scroll_panel.children:
                    button.visible = True
                return
            for button in scroll_panel.children:
                button.visible = text.lower() in button.text.lower()
            self.gui.update_layout()

        window.layout = engine.GroupLayout()
        if width > 0:
            window.fixed_width = width
        if height > 0:
            window.fixed_height = height
        search_box = engine.TextBox(parent=window, placeholder="search box",
                                    # callback=update_resource_list,
                                    on_key_callback=update_resource_list
                                    )

        scroll_panel_holder = engine.ScrollPanel(window)
        scroll_panel = engine.Widget(scroll_panel_holder, layout=engine.GroupLayout())
        if height > 0:
            scroll_panel_holder.fixed_height = height - 100
        return scroll_panel, search_box

    def make_delete_button(self, entity, remove_callback, layout, parent, reload_gui=True):
        def on_press():
            remove_callback()
            if reload_gui:
                self.create_object_gui(entity)

        layout.append_row()
        spacer = engine.Widget(parent=parent)
        spacer.fixed_height = 10
        layout.set_anchor(spacer, engine.Anchor(1, layout.row_count - 1, 3, 1))
        layout.append_row()
        delete_button = engine.Button(name="delete this", parent=parent, callback=on_press)
        layout.set_anchor(delete_button, engine.Anchor(1, layout.row_count - 1, 1, 1))

    def make_property_edit_button(self, caption, helper, entity, thing, remove_callback):
        # parent: script_section
        # caption: script.__class__.__name__
        # create popup button
        popup_button = engine.PopupButton(caption=caption, side=0)
        advanced_layout = engine.AdvancedGridLayout([10, 0, 10, 0])
        popup_button.popup.layout = advanced_layout
        # populate popup with properties
        helper.set_window_unsafe(popup_button.popup)
        self.populate_properties_window(thing, helper, popup_button.popup)
        # add "remove" button
        self.make_delete_button(entity, remove_callback=remove_callback, layout=advanced_layout,
                                parent=popup_button.popup)

    def make_script_adder(self, entity, window):
        def import_script(path=None, name=None):
            class_object = load.loader.load_class(path, name)
            self.create_script(entity, class_object)
            self.create_object_gui(entity)

        engine.Button(name="Import new script", parent=window,
                      callback=lambda: self.make_file_import(callback=import_script,
                                                             path_placeholder='scripts.module',
                                                             name_placeholder='ScriptClassName', use_button=False))

        scroll_panel, _ = self.make_resource_list(window, height=200)
        for cls, name in self.scripts.items():
            name = name if name is not None else cls.__name__
            button = engine.Button(name, parent=scroll_panel,
                                   callback=lambda cls=cls: (self.create_script(entity, cls),
                                                             self.create_object_gui(entity))
                                   )
            button.fixed_height = 20

        return window

    def make_audio_adder(self, entity, window):
        def load_audio(path=None, name=None):
            if path == '':
                return None
            entity.add_audio(path, name)
            if path not in self.audio:
                self.audio[path] = name
            self.create_object_gui(entity)

        engine.Button(name="Import new audio", parent=window,
                      callback=lambda: self.make_file_import(callback=load_audio,
                                                             path_placeholder='path/to/audio.wav',
                                                             name_placeholder='audio name', use_button=True))

        scroll_panel, _ = self.make_resource_list(window, height=200)
        for path, name in self.audio.items():
            name = name if name is not None else path
            button = engine.Button(name, parent=scroll_panel,
                                   callback=lambda path_=path: (entity.add_audio(path_, name),
                                                                self.create_object_gui(entity))
                                   )
            button.fixed_height = 20

        return window

    def make_shader_adder(self, entity, window, shader_type, asset_dict):
        def load_shader(path=None):
            if path == '':
                return None
            entity.set_shader(path, shader_type)
            if path not in asset_dict:
                asset_dict[path] = path.split('/')[-1]
            self.create_object_gui(entity)

        engine.Button(name="Import new " + shader_type, parent=window,
                      callback=lambda: load_shader(engine.file_dialog(True))
                      )

        scroll_panel, _ = self.make_resource_list(window, height=200)
        for path, name in asset_dict.items():
            name = name if name is not None else path
            button = engine.Button(name, parent=scroll_panel,
                                   callback=lambda path_=path: (entity.set_shader(path_, shader_type),
                                                                self.create_object_gui(entity))
                                   )
            button.fixed_height = 20

        return window

    def make_model_editor(self, entity, window):
        def set_entity_model(path=None, name=None):
            if path == '':
                return None
            path = os.path.relpath(path)  # get relative path
            entity.meshes = engine.load_model(path)
            entity.model_path = path
            if path not in self.models:
                self.models[path] = name
            self.create_object_gui(entity)  # reload properties menu

        engine.Button(name="import new model", parent=window,
                      callback=lambda: self.make_file_import(callback=set_entity_model,
                                                             path_placeholder='path/to/file',
                                                             name_placeholder='model name'))

        scroll_panel, _ = self.make_resource_list(window, width=-1, height=-1)
        for path, name in self.models.items():
            name = name if name is not None else path
            button = engine.Button(name, parent=scroll_panel, callback=lambda path_=path: set_entity_model(path_))
            button.fixed_height = 20

        return window

    def make_entity_class_editor(self, window, create_new_entity):
        def import_entity_class(path=None, name=None):
            module = importlib.import_module(path)
            entity_class = getattr(module, name)
            create_new_entity(entity_class)

        engine.Button(name="Import new class", parent=window,
                      callback=lambda: self.make_file_import(callback=import_entity_class,
                                                             path_placeholder='classes.module',
                                                             name_placeholder='EntityClassName', use_button=False))

        scroll_panel, search_box = self.make_resource_list(window, height=200)
        for cls, name in self.entity_classes.items():
            name = name if name is not None else cls.__name__
            button = engine.Button(name, parent=scroll_panel,
                                   callback=lambda entity_class=cls: create_new_entity(entity_class))
            button.fixed_height = 20

        return search_box

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

    def make_entity_list(self):
        entity_list_window = engine.GuiWindow(10, 10, "entity list", gui=self.gui, layout=engine.GroupLayout())
        entity_list_window.fixed_width = 225

        def create_new_entity(cls):
            # select a unique id, keep guessing until you find one
            id = 'new_entity'
            i = len(self.entities)
            while True:
                if id not in self.entities_by_id:
                    break
                i += 1
                id = f'new_entity{i}'

            new_entity = self.create_entity(model_path='resources/cube/cube.obj', id=id, entity_class=cls,
                                            vert_path='shaders/basic.vert', frag_path='shaders/basichighlight.frag')
            self.select_entity(new_entity)

        add_entity_button = engine.PopupButton(callback=lambda *args: search_box.request_focus(),
                                               parent=entity_list_window, caption="create entity", side=0)
        add_entity_button.side = 1  # the chevron is the wrong way round if i dont do this
        search_box = self.make_entity_class_editor(add_entity_button.popup, create_new_entity)

        scroll_panel_holder = engine.ScrollPanel(entity_list_window)
        scroll_panel_holder.fixed_height = 150
        scroll_panel = engine.Widget(parent=scroll_panel_holder, layout=engine.GroupLayout())
        self.entity_list_scroll_panel = scroll_panel
        self.update_entity_list()

    def update_entity_list(self):
        # if an entity is not in the list, add it
        for id, entity in self.entities_by_id.items():
            if id in self.entity_list_buttons_by_id or id.startswith('_'):
                continue

            # engine.Label(caption=f"{x}th button", parent=scroll_panel)
            button = engine.Button(id, lambda target=entity: self.select_entity(target),
                                   parent=self.entity_list_scroll_panel)
            button.fixed_height = 20
            self.entity_list_buttons_by_id[id] = button

        # if a deleted entity is still in the list, remove it
        ids_to_delete = []
        for id, button in self.entity_list_buttons_by_id.items():
            if id not in self.entities_by_id:
                button.visible = False  # todo actually remove it
                ids_to_delete.append(id)
        for id in ids_to_delete:
            del self.entity_list_buttons_by_id[id]

        self.gui.update_layout()

    def create_tool_window(self):
        tool_window = engine.GuiWindow(240, 10, 'tools', gui=self.gui, layout=engine.GroupLayout())
        with tool_window:
            engine.Button('save', callback=lambda: save.save_level(self.save_name, editor=self))
            engine.Button('reload', callback=self.soft_reload_level)
            mode_box = engine.TextBox(value=f'mode: {self.mode}', editable=False)
            engine.Button('toggle mode',
                          callback=lambda: (self.toggle_mode(),
                                            setattr(mode_box, 'value', f'mode: {self.mode}')))
            engine.Button('throw error', callback=lambda: 1/0)