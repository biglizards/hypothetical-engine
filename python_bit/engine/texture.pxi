IF FALSE:
    # this is a hack to get code inspection working
    include "util.pxi"

cdef extern from "stb_image.h":
    # i dont have to #define STB_IMAGE_IMPLEMENTATION because nanogui contains a copy of it already
    unsigned char* stbi_load(char* filename, int* x, int* y, int* channels_in_file, int desired_channels)
    # note that if desired_channels = 0, it chooses for you (probably for the best)
    void stbi_image_free(void* data)
    void stbi_set_flip_vertically_on_load(bint flag)

cdef extern from *:
    void glGenTextures(int n, unsigned int* textures)
    void glBindTexture(unsigned int target, unsigned int texture)  # eg glBindTexture(GL_TEXTURE_2D, texture)
    void glTexImage2D(unsigned int target, int mipmap_level, int internal_format, int width, int height,
                      int must_be_zero, unsigned int data_format, unsigned int data_type, const void* data)
    # data_format: the format you pass in. internal_format: how the data is stored. they should probably be the same
    # (https://stackoverflow.com/questions/34497195/difference-between-format-and-internalformat)
    void glGenerateMipmap(unsigned int target)

    void glActiveTexture(unsigned int unit)
    void glUniform1i(int location, int value)
    int glGetUniformLocation(unsigned int program, const char* name)
    void glUseProgram(unsigned int program)


    unsigned int GL_TEXTURE0
    unsigned int GL_TEXTURE_2D
    unsigned int GL_RGB
    unsigned int GL_RGBA
    unsigned int GL_UNSIGNED_BYTE
    unsigned int glGetError()

cpdef unsigned int load_texture_from_file(filename_str, data_format=GL_RGB, flip_on_load=True) except 0:
    """loads a texture from a file, returns 0 on failure"""

    cdef bytes filename = to_bytes(filename_str)

    cdef int width, height, no_of_channels
    stbi_set_flip_vertically_on_load(flip_on_load)
    cdef unsigned char* data = stbi_load(filename, &width, &height, &no_of_channels, 0)

    if not data:
        raise FileNotFoundError("failed to load texture")

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

cdef class Texture:
    """
    a super thin wrapper around texture objects
    maybe i'll add to it more later
    maybe i wont
    """
    cdef unsigned int texture

    def __init__(self, texture_path, data_format=GL_RGB):
        self.texture = load_texture_from_file(texture_path, data_format)

    cpdef bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

    cpdef bind_to_unit(self, int unit):
        target_unit = GL_TEXTURE0 + unit  # this works because, for example, GL_TEXTURE3 = GL_TEXTURE0 + 3
        glActiveTexture(unit=target_unit)
        self.bind()