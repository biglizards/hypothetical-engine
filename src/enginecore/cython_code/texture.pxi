IF FALSE:
    # this is a hack to get code inspection working
    include "util.pxi"

cdef extern from "stb_image.h":
    # i dont have to #define STB_IMAGE_IMPLEMENTATION because nanogui contains a copy of it already
    unsigned char* stbi_load(char* filename, int* x, int* y, int* channels_in_file, int desired_channels)
    # note that if desired_channels = 0, it chooses for you (probably for the best)
    void stbi_image_free(void* data)
    void stbi_set_flip_vertically_on_load(bint flag)

cpdef unsigned int load_texture_from_file(filename_str, data_format=None, flip_on_load=True) except 0:
    """loads a texture from a file, returns 0 on failure"""

    cdef bytes filename = to_bytes(filename_str)

    cdef int width, height, no_of_channels
    stbi_set_flip_vertically_on_load(flip_on_load)
    cdef unsigned char* data = stbi_load(filename, &width, &height, &no_of_channels, 0)

    if not data:
        raise FileNotFoundError("failed to load texture: " + filename.decode())

    if data_format is None:  # figure out format based on number of channels
        data_format = {3:GL_RGB, 4:GL_RGBA}[no_of_channels]

    cdef unsigned int texture
    glGenTextures(1, &texture)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, mipmap_level=0, internal_format=data_format, width=width, height=height,
                 must_be_zero=0, data_format=data_format, data_type=GL_UNSIGNED_BYTE, data=data)
    glGenerateMipmap(GL_TEXTURE_2D)

    stbi_image_free(data)

    if texture == 0:
        raise RuntimeError("failed to create texture; reason unknown")

    return texture

texture_cache = {}

cdef class Texture:
    """
    a super thin wrapper around texture objects
    """
    cdef unsigned int texture
    cdef public object name
    cdef public object texture_type

    def __init__(self, texture_path, data_format=None, flip_on_load=True, name="", texture_type=None):
        if texture_path in texture_cache:
            self.texture = texture_cache[texture_path]
        else:
            self.texture = load_texture_from_file(texture_path, data_format, flip_on_load)
            texture_cache[texture_path] = self.texture
        self.name = name
        self.texture_type = texture_type

    cpdef bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

    cpdef bind_to_unit(self, int unit):
        target_unit = GL_TEXTURE0 + unit  # this works because, for example, GL_TEXTURE3 = GL_TEXTURE0 + 3
        glActiveTexture(unit=target_unit)
        self.bind()