import sys
import traceback

import glm
import itertools
import time
from collections import defaultdict
from typing import Iterable

import engine
import openal

from enginelib import script
from enginelib.camera import Camera
from enginelib.level import load, reload
from enginelib.util import multiply_vec3


class MethodWrapper:
    def __init__(self, method, args):
        self.hook_args = args
        self.method = method

    def __call__(self, *args, **kwargs):
        self.method(*args, **kwargs)

    def __eq__(self, other):
        return other == self.method


def savable_args(*args):
    return {arg: arg for arg in args}


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


class Entity(engine.Model):
    def __new__(cls, *args, **kwargs):
        """Called when creating a new entity instance. If the class has been reloaded, use the newer version instead"""
        # note: without this, calling super with a reloaded class always raises an error
        new_cls = load.loader.get_newer_class(cls)
        obj = engine.Model.__new__(new_cls)
        if cls is not new_cls:
            # __init__ is not automatically called if we return the "wrong" class, so call it manually
            obj.__init__(*args, **kwargs)

        return obj

    def __init__(self, game, vert_path, frag_path, geo_path=None, meshes=None, model_path=None, position=None,
                 orientation=None, scalar=None, velocity=None, do_gravity=False, do_collisions=False,
                 should_render=True, scripts=None, id='', flip_textures=True, **kwargs):

        if not (meshes is None) ^ (model_path is None):
            raise RuntimeError("exactly one of 'meshes' and 'model_path' must be passed to Entity")
        if meshes is None:
            meshes = engine.load_model(model_path, flip_on_load=flip_textures)

        super().__init__(meshes, vert_path, frag_path, geo_path)

        self.game = game
        self._id = id
        self.position = position if position is not None else glm.vec3(0, 0, 0)
        self.orientation = orientation if orientation is not None else glm.quat(1, 0, 0, 0)
        self.scalar = scalar or glm.vec3(1, 1, 1)
        self.velocity = velocity or glm.vec3(0, 0, 0)
        self.do_gravity = do_gravity
        self.do_collisions = do_collisions
        self.model_path = model_path
        self.model_mat = None
        self.bounding_sphere_radius = float('inf')
        self.should_render = should_render

        # add savable attributes (that is, attributes that i expect to change while editing is being done)
        self.savable_attributes = savable_args('position', 'orientation', 'scalar', 'velocity', 'do_gravity',
                                               'do_collisions', 'should_render', 'id', 'scripts', 'model_path')
        # arguments not on this list: shader paths, meshes, model_path, scripts

        # set the property blacklist, which lists the things that dont show up in the property window
        self.property_blacklist = ['game', 'savable_attributes', 'property_blacklist', 'scripts', 'model_path']

        self.scripts = []
        if scripts is not None:
            for add_script in scripts:  # scripts is a list of partials of game.add_script
                add_script(entity=self)

        self._click_shader = engine.ShaderProgram(vert_path, 'shaders/clickHack.frag')
        self.save_overrides = {}

        # if anything was added as a hook, set the callback for it automatically
        script.add_hook_callbacks(self, self.game, add_everything=False)

    def on_save(self):
        self.save_overrides.update(self.get_shaders())

    def get_shaders(self):
        vert_path, frag_path, geo_path = self.shader_program.paths
        return {
                'vert_path': vert_path,
                'frag_path': frag_path,
                'geo_path': geo_path,
            }

    def super(self, cls):
        # ok this is a bit of a long story
        # when you reload an object, and that object calls super(CLS, self), the definition of CLS changes
        # but the self stays as being the old object, so super complains the instance is unrelated to the class
        # obviously this is dumb and doesnt work so todo fix this
        import inspect
        ret_next = False
        for mro_cls in inspect.getmro(cls):
            if ret_next:
                return mro_cls
            if mro_cls == cls:
                ret_next = True
        raise ValueError("no classes lower than passed class in MRO!")

    def remove(self):
        """this function is called when the entity is removed, and can be overridden to perform cleanup"""
        pass

    def set_shader(self, shader_path, shader_type):
        """changes the shader of a given type"""
        paths = self.get_shaders()
        paths[shader_type] = shader_path
        self.shader_program = engine.ShaderProgram(**paths)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        del self.game.entities_by_id[self._id]
        self._id = value
        self.game.entities_by_id[value] = self

    def generate_model_mat(self, ignore_orientation=False, store_model_mat=True):
        """generates and returns the model matrix for this entity, and by default caches it (for the physics engine)"""
        model_mat = glm.translate(glm.mat4(1), self.position)
        if not (self.orientation == glm.quat(1, 0, 0, 0) or ignore_orientation):
            model_mat = model_mat * glm.mat4_cast(self.orientation)  # rotate by orientation
        if self.scalar != glm.vec3(1, 1, 1):
            model_mat = glm.scale(model_mat, self.scalar)
        if store_model_mat:
            self.model_mat = model_mat
        return model_mat

    def set_transform_matrix(self, shader_program=None):
        """this is essentially the "prepare your shaders" function, so if the vertex shaders change,
        (eg the transformMat is renamed to mvp, etc) then this function can be updated accordingly.
        A user would only need to care about this if they were modifying shaders"""
        if shader_program is None:
            shader_program = self.shader_program

        projection_times_view = self.game.projection * self.game.camera.view_matrix()
        transformation_matrix = projection_times_view * self.generate_model_mat()
        shader_program.set_trans_mat(transformation_matrix)
        return transformation_matrix

    def get_vertices(self):
        for mesh in self.meshes:
            yield from mesh.get_vertices()

    def local_unit_vectors(self):
        i_vector = glm.vec4(1, 0, 0, 0)
        j_vector = glm.vec4(0, 1, 0, 0)
        k_vector = glm.vec4(0, 0, 1, 0)
        unit_vectors = (i_vector, j_vector, k_vector)

        return [glm.vec3(self.model_mat * unit_vector) for unit_vector in unit_vectors]


class ManualEntity(Entity):
    def __init__(self, game, data, indices, data_format, textures, *args, **kwargs):
        mesh = engine.Mesh(data, data_format, indices)

        for i, (texture, texture_name) in enumerate(textures):
            if isinstance(texture, str):
                texture = engine.Texture(texture)
            mesh.add_texture(texture, i)

        super(ManualEntity, self).__init__(game, meshes=[mesh], *args, **kwargs)


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

