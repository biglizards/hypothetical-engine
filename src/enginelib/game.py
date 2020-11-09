import itertools
import sys
import time
import traceback
from collections import defaultdict
from typing import Iterable

import engine
import glm
import openal

from enginelib.camera import Camera
from enginelib.entity import Entity
from enginelib.level import load, reload


class Game(engine.Window):
    def __init__(self, *args, camera=None, save_name=None, background_colour=None, projection=None, fov=75, near=0.1, far=100,
                 everything_is_reloadable=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.entities = []
        self.entities_by_id = {}
        self.overlay_entities = []
        self.entity_lists = [self.entities, self.overlay_entities]
        self.dispatches = defaultdict(list)
        self.global_scripts = []
        self.make_everything_reloadable = everything_is_reloadable
        if self.make_everything_reloadable:
            # make self re-loadable
            load.loader.make_everything_reloadable = True
            load.loader.add_to_reload_cache(type(self), force_reload=False)
            reload.reloadable_class(type(self))
            reload.reloadable_class(type(camera) if camera else Camera)
            # load.loader.add_to_reload_cache(type(camera) if camera else Camera)
            load.loader.make_everything_reloadable = True

        self.camera = camera(self) if camera else Camera(self)
        self.save_name = save_name if save_name else self.save_name
        self.background_colour = background_colour or (0.3, 0.5, 0.8, 1)
        self.projection = projection or glm.perspective(glm.radians(fov), self.width / self.height, near, far)
        self.near, self.far, self.fov = near, far, fov

        self.resize_callback = self._resize_callback  # for some reason, this is needed. Dont ask.

        # engine.Window provides the callbacks
        self._set_default_callbacks({'on_cursor_pos_update': 'cursor_pos_callback',
                                     ('on_mouse_button_press', 'on_click'): 'mouse_button_callback',
                                     'on_key_press': 'key_callback',
                                     'on_char': 'char_callback',
                                     'on_file_drop': 'drop_file_callback',
                                     'on_scroll': 'scroll_callback',
                                     # 'on_resize': 'resize_callback',  # replaced manually
                                     })

        load.load_level(self.save_name, game=self)

    @property
    def all_entities(self):
        return itertools.chain(*self.entity_lists)

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        del self.entities_by_id[entity.id]
        try:
            self.entities.remove(entity)
        except ValueError:  # entity not in list
            self.overlay_entities.remove(entity)
        while entity.scripts:
            entity.scripts[0].remove()
        entity.remove()  # call custom handler to do custom cleanup

    def create_entity(self, *args, entity_class=Entity, overlay=False, id, **kwargs):
        assert id not in self.entities_by_id, 'entities must be unique'
        new_entity = entity_class(game=self, id=id, *args, **kwargs)
        self.entities_by_id[id] = new_entity
        if overlay:
            self.overlay_entities.append(new_entity)
        else:
            self.entities.append(new_entity)
        return new_entity

    def create_script(self, entity, script_class, *args, **kwargs):
        new_script = script_class(parent=entity, game=self, *args, **kwargs)
        entity.scripts.append(new_script)
        return new_script

    def add_global_script(self, script):
        self.global_scripts.append(script(parent=None, game=self))

    def draw_entities(self, entity_list):
        proj_times_view = self.projection * self.camera.view_matrix()
        # transformation_matrix = projection * view * model
        for entity in entity_list:
            if not entity.should_render:
                continue
            transformation_matrix = proj_times_view * entity.generate_model_mat()
            entity.shader_program.set_trans_mat(transformation_matrix)
            entity.draw()

    def dispatch(self, name: str, *args):
        funcs = self.dispatches.get(name, [])
        for func in funcs:
            func(*args)

    def dispatch_many(self, names: Iterable[str], *args):
        for name in names:
            self.dispatch(name, *args)

    def add_callback(self, name, func, **args):
        if args:
            try:
                if hasattr(func, 'hook_args') and func.hook_args != args:
                    raise RuntimeError(f"{func} was registered to two hooks with different arguments")
                func.hook_args = args
            except AttributeError:
                # this can happen if func is a method
                func = MethodWrapper(func, args)

        self.dispatches[name].append(func)

    def remove_callback(self, name, func):
        try:
            self.dispatches[name].remove(func)
        except ValueError:
            self.dispatches[name] = list(filter(lambda x: not (x.__self__ is func.__self__
                                                               and x.__name__ == func.__name__),
                                                self.dispatches[name]))

    def _set_default_callbacks(self, events):
        """sets the default callbacks for events, given a dict in the format
            {'on_x': 'x_callback', ...}, where on_x is the dispatch name and x_callback is the attribute
        """
        for name, event in events.items():
            def dispatch_event(*args, _name=name):
                if isinstance(_name, str):
                    self.dispatch(_name, *args[1:])  # these callbacks have the first arg be `self`, so ignore that
                else:  # the only other valid thing should be a tuple, but any iterable is fine really
                    self.dispatch_many(_name, *args[1:])
            setattr(self, event, dispatch_event)

    def _resize_callback(self, *args):
        self.projection = glm.perspective(glm.radians(self.fov), self.width / self.height, self.near, self.far)
        self.dispatch('on_resize', *args[1:])

    def on_error(self, e):
        tb = ''.join(x for x in traceback.format_exception(etype=type(e),
                                                           value=e,
                                                           tb=e.__traceback__) if 'return inner.f(self' not in x)
        print(tb, file=sys.stderr)

    def run(self, *args, **kwargs):
        """A wrapper around self._run, but calls it with a try-finally,
        so the indentation doesn't get too out of hand"""

        try:
            self._run(*args, **kwargs)
        except TypeError as e:
            if e.args == ('super(type, obj): obj must be an instance or subtype of type',):
                raise TypeError("You reloaded a class which uses super() outside of __init__ - "
                                "try self.super(CLASS_NAME) instead")
        finally:
            openal.oalQuit()

    def _run(self, print_fps=False):
        frame_count = 0
        time_since_last_fps_print = time.perf_counter()
        last_frame_time = time.perf_counter()

        self.dispatch('on_game_start')

        while not self.should_close():
            time_time = time.perf_counter()
            delta_t = (time_time - last_frame_time) % 0.1  # if the game freezes, just ignore it
            last_frame_time = time_time

            # draw everything
            self.clear_colour(*self.background_colour)
            self.dispatch('before_frame', delta_t)
            self.draw_entities(self.entities)
            # call user-defined functions
            self.dispatch('on_frame', delta_t)
            # draw any entities that are meant to be overlaid on top of the rest, like axes or a custom gui
            self.clear(engine.DEPTH_BUFFER_BIT)
            self.draw_entities(self.overlay_entities)

            self.gui.draw()
            self.swap_buffers()

            # handle input
            try:
                engine.poll_events()
            except Exception as e:
                self.on_error(e)

            self.camera.handle_input()

            # fps printer
            if print_fps:
                frame_count += 1
                if time_time > time_since_last_fps_print + 5:
                    duration = time_time - time_since_last_fps_print
                    print("current fps:", round(frame_count/duration))
                    time_since_last_fps_print = time_time
                    frame_count = 0

        # the loop is over, so self.should_close() == True


class MethodWrapper:
    def __init__(self, method, args):
        self.hook_args = args
        self.method = method

    def __call__(self, *args, **kwargs):
        self.method(*args, **kwargs)

    def __eq__(self, other):
        return other == self.method