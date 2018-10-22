import glm
import itertools
import time
from collections import defaultdict
from functools import wraps

import engine

from camera import Camera


# TODO remove data, data_format once model loading is added
from util import multiply_vec3


class Entity(engine.Drawable):
    def __init__(self, data, indices, data_format, textures, vert_path, frag_path, geo_path=None, position=None,
                 orientation=None, scalar=None, velocity=None, has_gravity=False):
        super().__init__(data, indices, data_format, vert_path, frag_path, geo_path)

        for i, (texture, texture_name) in enumerate(textures):
            if isinstance(texture, str):
                texture = engine.Texture(texture)
            self.shader_program.add_texture(texture, texture_name, i)

        self.position = position if position is not None else glm.vec3(0, 0, 0)
        self.orientation = orientation if orientation is not None else glm.quat(1, 0, 0, 0)
        self.scalar = scalar or glm.vec3(1, 1, 1)
        self.velocity = velocity or glm.vec3(0, 0, 0)
        self.has_gravity = has_gravity
        self.model = None

    def set_model(self, model=None):
        self.model = model or self.generate_model()
        self.shader_program.set_value("model", self.model)

    def generate_model(self, ignore_orientation=False):
        # model = local->world
        model = glm.translate(glm.mat4(1), self.position)
        if not ignore_orientation:
            model = model * glm.mat4_cast(self.orientation)  # rotate by orientation
        if self.scalar is not None:
            model = glm.scale(model, self.scalar)
        return model

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
        self.projection = projection or glm.perspective(glm.radians(75), self.width / self.height, 0.1, 100)

    def add_entity(self, entity):
        self.entities.append(entity)

    @wraps(Entity)
    def create_entity(self, *args, **kwargs):
        new_entity = Entity(*args, **kwargs)
        self.add_entity(new_entity)
        return new_entity

    def draw_entities(self):
        view = self.camera.view_matrix()
        for entity in self.entities:
            entity.shader_program.set_value('view', view)
            entity.shader_program.set_value("projection", self.projection)
            entity.set_model()
            entity.draw()

    def dispatch(self, name, *args):
        funcs = self.dispatches.get(name, [])
        for func in funcs:
            func(*args)

    def add_callback(self, name, func):
        self.dispatches[name].append(func)

    def run(self, print_fps=False):
        frame_count = 0
        time_since_last_fps_print = time.time()
        last_frame_time = time.time()

        while not self.should_close():
            delta_t = time.time() - last_frame_time
            last_frame_time = time.time()

            # draw everything
            self.clear_colour(*self.background_colour)
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
                if frame_count > 2**12:
                    duration = time.time() - time_since_last_fps_print
                    print("current fps:", round(2**12/duration))
                    time_since_last_fps_print = time.time()
                    frame_count = 0
