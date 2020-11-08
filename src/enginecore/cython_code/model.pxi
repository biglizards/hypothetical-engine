from cpython cimport array
cimport includes.assimp as assimp
import os
from itertools import zip_longest

IF FALSE:
    # this is a hack to get code inspection working
    include "util.pxi"

def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


# noinspection PyAttributeOutsideInit
cdef class Mesh:
    """
    a mesh has
     - vertex (and texture) co-ords
     - texture co-ords
     - texture data
     - a hitbox maybe?
    """
    cdef unsigned int VAO, VBO, EBO
    cdef public raw_data
    cdef public data_format
    cdef public corners
    cdef readonly bounding_radius
    cdef readonly centre
    cdef public dict textures
    cdef int no_of_indices
    cdef bint indexed

    def __cinit__(self, py_data, data_format, indices=None, textures=None, *args, **kwargs):
        self.VAO = 0
        self.VBO = 0
        self.EBO = 0
        self.textures = {}   # unit : texture

        self.raw_data = py_data
        self.data_format = data_format
        self.calculate_bounding_box()
        self.calculate_bounding_sphere()

        if textures is not None:
            for unit, texture in enumerate(textures):
                self.add_texture(texture, unit)

        self.buffer_packed_data(py_data, data_format, indices)

    def __init__(self, py_data, data_format, indices=None, *args, **kwargs):
        pass
    
    def get_vertices(self):
        for data in grouper(self.raw_data, sum(self.data_format)):
            yield data[:3]

    cpdef calculate_bounding_box(self):
        minimum = glm.vec3(float('inf'))
        maximum = glm.vec3(float('-inf'))
        for x, y, z in self.get_vertices():
            if x > maximum.x:
                maximum.x = x
            elif x < minimum.x:
                minimum.x = x
            if y > maximum.y:
                maximum.y = y
            elif y < minimum.y:
                minimum.y = y
            if z > maximum.z:
                maximum.z = z
            elif z < minimum.z:
                minimum.z = z

        corners = []
        x = (minimum, maximum)
        for a, b, c in itertools.product([0, 1], repeat=3):
            corners.append(glm.vec3(x[a][0], x[b][1], x[c][2]))

        self.corners = corners
        return corners

    cpdef calculate_bounding_sphere(self):
        # set centre to average of all vertices   todo (maybe it'd be better to use centre of aabb?)
        centre = glm.vec3(0)
        vertices = list(self.get_vertices())
        for vert in vertices:
            centre += vert
        centre /= len(vertices)

        # calculate radius -- greatest distance from centre
        cdef r = 0
        for vert in vertices:
            if glm.length(vert-centre) > r:
                r = glm.length(vert-centre)

        self.bounding_radius = r
        self.centre = centre
        return centre, r


    cdef buffer_packed_data(self, py_data, data_format, indices=None):
        """
        packed data is in the format specified in data_format
        where the meta-format is (width1, width2, ...)
        eg, for a data format of (3, 1, 2) the data would look like
        [a, a, a, b, c, c
         a, a, a, b, c, c,
         ...
         ]
        """
        # convert python list to array.array
        cdef array.array data = array.array('f', py_data)
        cdef array.array index_array
        cdef int length = len(data)
        cdef int total_width = sum(data_format)

        # create and bind array/buffer objects
        glGenVertexArrays(1, &self.VAO)
        glGenBuffers(1, &self.VBO)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        # buffer data
        glBufferData(target=GL_ARRAY_BUFFER, size=sizeof(float)*length,
                     data=data.data.as_floats, usage=GL_STATIC_DRAW)

        # add format info
        cdef int i, width, offset = 0
        for i, width in enumerate(data_format):
            glVertexAttribPointer(index=i, size=width, type=GL_FLOAT, normalized=0,
                                  stride=total_width*sizeof(float), pointer=<void*>(offset * sizeof(float)))
            glEnableVertexAttribArray(i)
            offset += width

        if indices:
            index_array = array.array('i', indices)
            glGenBuffers(1, &self.EBO)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices)*sizeof(int),
                         index_array.data.as_ints, GL_STATIC_DRAW)
            self.indexed = True
            self.no_of_indices = len(indices)
        else:
            self.indexed = False
            self.no_of_indices = len(data) / sum(data_format)

    cpdef void bind(self):
        glBindVertexArray(self.VAO)

    cpdef bind_textures(self, ShaderProgram shader=None):
        for unit, texture in self.textures.items():
            if shader is not None:
                shader.set_value("texture_" + str(unit), unit)
            texture.bind_to_unit(unit)

    cpdef add_texture(self, Texture texture, unit, overwrite=False):
        if not overwrite and unit in self.textures:
            raise ValueError("Unit {} already has associated texture".format(unit))
        self.textures[unit] = texture

    cpdef draw(self, ShaderProgram shader, unsigned int mode=GL_TRIANGLES):
        cdef Texture texture
        self.bind()
        self.bind_textures(shader)
        if self.indexed:
            glDrawElements(mode, self.no_of_indices, GL_UNSIGNED_INT, NULL)
        else:
            glDrawArrays(mode, 0, self.no_of_indices)

# noinspection PyAttributeOutsideInit
cdef class Model:
    """
    A model has
     - a shader program
     - a list of meshes
    """
    cdef public object meshes
    cdef public ShaderProgram shader_program

    cdef readonly bounding_radius

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, meshes, vert_path, frag_path, geo_path=None):
        self.meshes = meshes
        self.shader_program = ShaderProgram(vert_path, frag_path, geo_path)
        self.calculate_bounding_sphere()

    cpdef draw(self, unsigned int mode=GL_TRIANGLES):
        if not self.meshes:
            raise RuntimeError('Model was not properly init! Was super() called?')

        for mesh in self.meshes:
            mesh.draw(self.shader_program, mode=mode)

    cpdef draw_with_shader(self, ShaderProgram shader_program, unsigned int mode=GL_TRIANGLES):
        if not self.meshes:
            raise RuntimeError('Model was not properly init! Was super() called?')

        for mesh in self.meshes:
            print("drawing")
            mesh.draw(shader_program, mode=mode)


    cpdef recalculate_bounding_sphere(self):
        for mesh in self.meshes:
            mesh.calculate_bounding_sphere()
        self.calculate_bounding_sphere()

    cpdef calculate_bounding_sphere(self):
        # centre is implicitly the origin
        cdef r = 0
        for mesh in self.meshes:
            mesh_r = glm.length(mesh.centre) + mesh.bounding_radius
            if mesh_r > r:
                r = mesh_r

        self.bounding_radius = r
        return r


cpdef load_model(path_str, flip_on_load=True):
    cdef bytes path = to_bytes(path_str)
    cdef assimp.Importer importer
    cdef const assimp.aiScene* scene = importer.ReadFile(path, assimp.aiProcess_Triangulate | assimp.aiProcess_FlipUVs)
    if scene is NULL or (scene.mFlags & assimp.AI_SCENE_FLAGS_INCOMPLETE) or not scene.mRootNode:
        raise RuntimeError("ERROR [MODEL]: " + importer.GetErrorString().decode())
    return process_node(scene.mRootNode, scene, path, meshes=None, flip_on_load=flip_on_load)

cdef process_node(assimp.aiNode* node, const assimp.aiScene* scene, path, meshes=None, flip_on_load=True):
    cdef assimp.aiMesh* mesh
    cdef assimp.aiNode* child_node
    meshes = meshes if meshes is not None else []

    for mesh_index in node.mMeshes[:node.mNumMeshes]:
        mesh = scene.mMeshes[mesh_index]
        meshes.append(process_mesh(mesh, scene, path, flip_on_load))
    for child_node in node.mChildren[:node.mNumChildren]:
        process_node(child_node, scene, path, meshes=meshes, flip_on_load=flip_on_load)

    return meshes

cdef process_mesh(assimp.aiMesh* mesh, const assimp.aiScene* scene, path, flip_on_load=True):
    cdef assimp.aiVector3D* ai_vector
    cdef assimp.aiFace* face

    # vertices, normals and texture_coords
    vertices = []
    normals = []
    texture_coords = []
    for ai_vector in mesh.mVertices[:mesh.mNumVertices]:
        vertices.append((ai_vector.x, ai_vector.y, ai_vector.z))
    for ai_vector in mesh.mNormals[:mesh.mNumVertices]:
        normals.append((ai_vector.x, ai_vector.y, ai_vector.z))
    if mesh.mTextureCoords[0] is not NULL:
        for ai_vector in mesh.mTextureCoords[0][:mesh.mNumVertices]:
            texture_coords.append((ai_vector.x, ai_vector.y))

    # indices
    indices = []
    for face in mesh.mFaces[:mesh.mNumFaces]:
        if face.mNumIndices != 3:
            print("WARNING: Non triangle detected. May mess up rendering")
        for index in face.mIndices[:face.mNumIndices]:
            indices.append(index)

    data = []
    if texture_coords:
        data_zip = zip(vertices, normals, texture_coords)
        data_format = (3, 3, 2)
    else:
        data_zip = zip(vertices, normals)
        data_format = (3, 3)
    for coords in data_zip:
        data.extend(sum(coords, ()))  # flatten the tuple of tuples into a single tuple

    cdef assimp.aiMaterial* material = scene.mMaterials[mesh.mMaterialIndex]
    diff_textures = load_textures_from_material(material, assimp.aiTextureType_DIFFUSE, path, "diffuse", flip_on_load)
    # the following are being ignored until i sort out the shaders, since i dont have lighting yet
    # todo fix this once i've added lighting
    #spec_textures = load_textures_from_material(material, assimp.aiTextureType_SPECULAR, path)
    #ambient_textures =  load_textures_from_material(material, assimp.aiTextureType_AMBIENT, path)

    return Mesh(data, data_format, indices, textures=diff_textures)  # + spec_textures + ambient_textures

cdef load_textures_from_material(assimp.aiMaterial* material, assimp.aiTextureType texture_type, path, type_name_str,
                                 flip_on_load):
    cdef bytes directory = os.path.dirname(path)
    cdef unsigned int texture_count = material.GetTextureCount(texture_type)
    cdef assimp.aiString ai_string
    texture_paths = []
    for i in range(texture_count):
        material.GetTexture(texture_type, i, &ai_string)
        texture_paths.append(os.path.join(directory, ai_string.C_Str()))

    textures = [Texture(texture_path, flip_on_load=flip_on_load, name=texture_path) for texture_path in texture_paths]
    return textures
