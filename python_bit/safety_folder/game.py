import glm
import itertools
import time
from collections import defaultdict
from functools import wraps
from typing import Tuple

import engine

from camera import Camera


# TODO remove data, data_format once model loading is added
from util import multiply_vec3


class Entity(engine.Drawable):
    def __init__(self, data, indices, data_format, textures, vert_path, frag_path, geo_path=None, position=None,
                 orientation=None, scalar=None, velocity=None, do_gravity=False, do_collisions=False,
                 should_render=True):
        super().__init__(data, indices, data_format, vert_path, frag_path, geo_path)

        for i, (texture, texture_name) in enumerate(textures):  # todo raise error if too many textures (either 8 or 16)
            if isinstance(texture, str):
                texture = engine.Texture(texture)
            self.shader_program.add_texture(texture, texture_name, i)

        self.position = position if position is not None else glm.vec3(0, 0, 0)
        self.orientation = orientation if orientation is not None else glm.quat(1, 0, 0, 0)
        self.scalar = scalar or glm.vec3(1, 1, 1)
        self.velocity = velocity or glm.vec3(0, 0, 0)
        self.do_gravity = do_gravity
        self.do_collisions = do_collisions
        self.model = None
        self._ignore_this = 34
        self.should_render = should_render

        self._click_shader = engine.ShaderProgram(vert_path, 'shaders/clickHack.frag')

    def generate_model(self, ignore_orientation=False, store_model=True):
        """generates and returns the model matrix for this entity, and by default caches it (for the physics engine)"""
        model = glm.translate(glm.mat4(1), self.position)
        if not (self.orientation == glm.quat(1, 0, 0, 0) or ignore_orientation):
            model = model * glm.mat4_cast(self.orientation)  # rotate by orientation
        if self.scalar != glm.vec3(1, 1, 1):
            model = glm.scale(model, self.scalar)
        if store_model:
            self.model = model
        return model

    def set_transform_matrix(self, game):
        """this is especially the "prepare your shaders" function, so if the vertex shaders change,
        (eg the transformMat is renamed to mvp) then this function can be updated accordingly.
        A user would only need to care about this if they were modifying shaders"""
        projection_times_view = game.projection * game.camera.view_matrix()
        transformation_matrix = projection_times_view * self.generate_model()
        self.shader_program.set_value("transformMat", transformation_matrix)
        return transformation_matrix

    def get_corners(self):
        # todo have the corner not be hard-coded
        #  - it'd only need to be generated once, at load-time, when calculating the OABB
        # todo scale unit vectors by length of each side of the bounding box
        #  - this can also be pre-calculated

        # generate two opposite corners
        corner = multiply_vec3(glm.vec3(-.5, -.5, -.5), self.model)
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

        return [glm.vec3(self.model * unit_vector) for unit_vector in unit_vectors]


class Game(engine.Window):
    def __init__(self, *args, camera=None, background_colour=None, projection=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entities = []
        self.dispatches = defaultdict(list)

        self.camera = camera or Camera(self)
        self.background_colour = background_colour or (0.3, 0.5, 0.8, 1)
        self.projection = projection or glm.perspective(glm.radians(75), self.width / self.height, 0.1, 1000)

        self._set_default_callbacks({'on_cursor_pos_update': 'cursor_pos_callback',
                                     ('on_mouse_button_press', 'on_click'): 'mouse_button_callback',
                                     'on_key_press': 'key_callback',
                                     'on_char': 'char_callback',
                                     'on_file_drop': 'drop_file_callback',
                                     'on_scroll': 'scroll_callback',
                                     'on_resize': 'resize_callback'})

    def add_entity(self, entity):
        self.entities.append(entity)

    @wraps(Entity)
    def create_entity(self, *args, entity_class=Entity, **kwargs):
        new_entity = entity_class(*args, **kwargs)
        self.add_entity(new_entity)
        return new_entity

    def draw_entities(self):
        proj_times_view = self.projection * self.camera.view_matrix()
        # transformation_matrix = projection * view * model
        for entity in self.entities:
            if not entity.should_render:
                continue
            transformation_matrix = proj_times_view * entity.generate_model()
            entity.shader_program.set_value("transformMat", transformation_matrix)
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

    def _set_default_callbacks(self, events):
        """sets the default callbacks for events, given a dict in the format
            {'on_x': 'x_callback', ...}, where on_x is the dispatch name and x_callback is the attribute
        """
        for name, event in events.items():
            def dispatch_event(*args, _name=name):
                self.dispatch(_name, *args[1:])  # these callbacks have the first arg be `self`, so ignore that
            setattr(self, event, dispatch_event)

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
            self.draw_entities()
            # call user-defined functions
            self.dispatch('on_frame', delta_t)
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
