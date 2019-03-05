import glm
import itertools
import time
from collections import defaultdict
from typing import Tuple

import engine

from camera import Camera


# TODO remove data, data_format once model loading is added
from util import multiply_vec3


def savable_args(*args):
    return {arg: arg for arg in args}


class Entity(engine.Model):
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

    def remove(self):
        """this function is called when the entity is removed, and can be overridden to perform cleanup"""
        pass

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

    def set_transform_matrix(self):
        """this is essentially the "prepare your shaders" function, so if the vertex shaders change,
        (eg the transformMat is renamed to mvp, etc) then this function can be updated accordingly.
        A user would only need to care about this if they were modifying shaders"""
        projection_times_view = self.game.projection * self.game.camera.view_matrix()
        transformation_matrix = projection_times_view * self.generate_model_mat()
        self.shader_program.set_trans_mat(transformation_matrix)
        return transformation_matrix

    def get_corners(self):
        # todo have the corner not be hard-coded
        #  - it'd only need to be generated once, at load-time, when calculating the OABB
        # todo scale unit vectors by length of each side of the bounding box
        #  - this can also be pre-calculated

        # generate two opposite corners
        corner = multiply_vec3(glm.vec3(-.5, -.5, -.5), self.model_mat)
        # generate the local unit vectors (note: these vectors may not be normalised, but that's fine)
        unit_vectors = self.local_unit_vectors()
        corners = []
        for i in (0, 1, 2, 3):
            for path in itertools.combinations(unit_vectors, i):
                corners.append(corner + sum(path))
        return corners

    def local_unit_vectors(self):
        i_vector = glm.vec4(1, 0, 0, 0)
        j_vector = glm.vec4(0, 1, 0, 0)
        k_vector = glm.vec4(0, 0, 1, 0)
        unit_vectors = (i_vector, j_vector, k_vector)

        return [glm.vec3(self.model_mat * unit_vector) for unit_vector in unit_vectors]


class ManualEntity(Entity):
    def __init__(self, game, data, indices, data_format, textures, *args, **kwargs):
        mesh = engine.Mesh(data, data_format, indices)

        for i, (texture, texture_name) in enumerate(textures):  # todo raise error if too many textures (either 8 or 16)
            if isinstance(texture, str):
                texture = engine.Texture(texture)
            mesh.add_texture(texture, i)

        super().__init__(game, meshes=[mesh], *args, **kwargs)


class Game(engine.Window):
    def __init__(self, *args, camera=None, background_colour=None, projection=None, fov=75, near=0.1, far=100,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.entities = []
        self.entities_by_id = {}
        self.overlay_entities = []
        self.entity_lists = [self.entities, self.overlay_entities]
        self.dispatches = defaultdict(list)

        self.camera = camera or Camera(self)
        self.background_colour = background_colour or (0.3, 0.5, 0.8, 1)
        self.projection = projection or glm.perspective(glm.radians(fov), self.width / self.height, near, far)
        self.near, self.far, self.fov = near, far, fov  # todo set these to properties that update self.projection

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

    # @wraps(Entity) todo why was this here, i dont think it needs to be
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

    def draw_entities(self, entity_list):
        proj_times_view = self.projection * self.camera.view_matrix()
        # transformation_matrix = projection * view * model
        for entity in entity_list:
            if not entity.should_render:
                continue
            transformation_matrix = proj_times_view * entity.generate_model_mat()
            entity.shader_program.set_trans_mat(transformation_matrix)
            entity.draw()

    def dispatch(self, names: str or Tuple[str], *args):
        # if the input isn't a tuple, make it one so we can iterate over it
        if isinstance(names, str):
            names = (names,)

        for name in names:
            funcs = self.dispatches.get(name, [])
            for func in funcs:
                func(*args)

    def add_callback(self, name, func):
        self.dispatches[name].append(func)

    def remove_callback(self, name, func):
        self.dispatches[name].remove(func)

    def _set_default_callbacks(self, events):
        """sets the default callbacks for events, given a dict in the format
            {'on_x': 'x_callback', ...}, where on_x is the dispatch name and x_callback is the attribute
        """
        for name, event in events.items():
            def dispatch_event(*args, _name=name):
                self.dispatch(_name, *args[1:])  # these callbacks have the first arg be `self`, so ignore that
            setattr(self, event, dispatch_event)

    def _resize_callback(self, *args):
        self.projection = glm.perspective(glm.radians(self.fov), self.width / self.height, self.near, self.far)
        self.dispatch('on_resize', *args[1:])

    def run(self, print_fps=False):
        frame_count = 0
        time_since_last_fps_print = time.time()
        last_frame_time = time.time()

        while not self.should_close():
            time_time = time.time()
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
            engine.poll_events()
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

