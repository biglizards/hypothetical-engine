import glm

def rotate_vec3(vec, angle, axis):
    return glm.vec3(glm.rotate(glm.mat4(1), angle, axis) * glm.vec4(vec, 1))
