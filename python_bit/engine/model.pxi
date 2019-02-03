from cpython cimport array
cimport assimp
import os

IF FALSE:
    # this is a hack to get code inspection working
    include "util.pxi"

cdef class Mesh:
    """
    a mesh has
     - vertex (and texture) co-ords
     - texture co-ords
     - texture data
     - a hitbox maybe?
    """
    cdef unsigned int VAO, VBO, EBO
    cdef public dict textures
    cdef int no_of_indices
    cdef bint indexed

    def __cinit__(self, py_data, data_format, indices=None, textures=None, *args, **kwargs):
        self.VAO = 0
        self.VBO = 0
        self.EBO = 0
        self.textures = {}   # unit : texture

        if textures is not None:
            for unit, texture in enumerate(textures):
                self.add_texture(texture, unit)

        self.buffer_packed_data(py_data, data_format, indices)

    def __init__(self, py_data, data_format, indices=None, *args, **kwargs):
        pass

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


cdef class Model:
    """
    A model has
     - a shader program
     - a list of meshes
    """
    cdef public object meshes
    cdef public ShaderProgram shader_program

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, meshes, vert_path, frag_path, geo_path=None):
        self.meshes = meshes
        self.shader_program = ShaderProgram(vert_path, frag_path, geo_path)

    cpdef draw(self, unsigned int mode=GL_TRIANGLES):
        if not self.meshes:  # todo consider removing
            raise RuntimeError('Model was not properly init! Was super() called?')

        for mesh in self.meshes:
            mesh.draw(self.shader_program, mode=mode)


cpdef load_model(path_str):
    cdef bytes path = to_bytes(path_str)
    cdef assimp.Importer importer
    cdef const assimp.aiScene* scene = importer.ReadFile(path, assimp.aiProcess_Triangulate | assimp.aiProcess_FlipUVs)
    if scene is NULL or (scene.mFlags & assimp.AI_SCENE_FLAGS_INCOMPLETE) or not scene.mRootNode:
        raise RuntimeError("ERROR [MODEL]: " + importer.GetErrorString().decode())
    return process_node(scene.mRootNode, scene, path)

cdef process_node(assimp.aiNode* node, const assimp.aiScene* scene, path, meshes=None):
    cdef assimp.aiMesh* mesh
    cdef assimp.aiNode* child_node
    meshes = meshes if meshes is not None else []

    for mesh_index in node.mMeshes[:node.mNumMeshes]:
        mesh = scene.mMeshes[mesh_index]
        meshes.append(process_mesh(mesh, scene, path))
    for child_node in node.mChildren[:node.mNumChildren]:
        process_node(child_node, scene, path, meshes=meshes)

    return meshes

cdef process_mesh(assimp.aiMesh* mesh, const assimp.aiScene* scene, path):
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
            print("WARNING: Non triangle detected. May fuck up rendering")
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
        data.extend(sum(coords, ()))

    cdef assimp.aiMaterial* material = scene.mMaterials[mesh.mMaterialIndex]
    diff_textures = load_textures_from_material(material, assimp.aiTextureType_DIFFUSE, path, "diffuse")
    # the following are being ignored until i sort out the shaders, since i dont have lighting yet
    # todo fix this once i've added lighting
    #spec_textures = load_textures_from_material(material, assimp.aiTextureType_SPECULAR, path)
    #ambient_textures =  load_textures_from_material(material, assimp.aiTextureType_AMBIENT, path)

    return Mesh(data, data_format, indices, textures=diff_textures)  # + spec_textures + ambient_textures

cdef load_textures_from_material(assimp.aiMaterial* material, assimp.aiTextureType texture_type, path, type_name_str):
    cdef bytes directory = os.path.dirname(path)
    cdef unsigned int texture_count = material.GetTextureCount(texture_type)
    cdef assimp.aiString ai_string
    texture_paths = []
    for i in range(texture_count):
        material.GetTexture(texture_type, i, &ai_string)
        texture_paths.append(os.path.join(directory, ai_string.C_Str()))

    textures = [Texture(texture_path, flip_on_load=False, name=texture_path) for texture_path in texture_paths]
    return textures
