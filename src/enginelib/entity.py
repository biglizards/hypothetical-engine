import glm
import itertools

import engine

from enginelib import script
from enginelib.level import load


def savable_args(*args):
    return {arg: arg for arg in args}


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


class ManualEntity(Entity):
    def __init__(self, game, data, indices, data_format, textures, *args, **kwargs):
        mesh = engine.Mesh(data, data_format, indices)

        for i, (texture, texture_name) in enumerate(textures):
            if isinstance(texture, str):
                texture = engine.Texture(texture)
            mesh.add_texture(texture, i)

        super(ManualEntity, self).__init__(game, meshes=[mesh], *args, **kwargs)


