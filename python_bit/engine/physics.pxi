from math import inf
import itertools

cdef struct min_and_max:
    double min_val
    double max_val

corner_min = glm.vec3(-.5, -.5, -.5)
corner_max = glm.vec3(.5, .5, .5)


cpdef gen_corners_from_min_max(a, b):
    """returns the corners given the maximum and minimum values of a cuboid"""
    return ((a[0], a[1], a[2]), (b[0], a[1], a[2]), (a[0], b[1], a[2]),
            (b[0], b[1], a[2]), (a[0], a[1], b[2]), (b[0], a[1], b[2]),
            (a[0], b[1], b[2]), (b[0], b[1], b[2]))


cpdef gen_corners(model):
    return gen_corners_from_min_max(multiply_vec3(corner_min, model), multiply_vec3(corner_max, model))


cpdef multiply_vec3(vec, mat):
    return glm.vec3(mat * glm.vec4(vec, 1))


cpdef bint two_cubes_intersect(cube1, cube2):
    if glm.length(cube1.position - cube2.position) > 6:  # obtained by pythag, todo use bounding spheres
        return False
    corners1 = gen_corners(cube1.model)
    corners2 = gen_corners(cube2.model)
    return unaligned_intersect(corners1, cube1.model, corners2, cube2.model)


cpdef bint unaligned_intersect(corners1, model1, corners2, model2):
    """ adapted from explanation at
    https://gamedev.stackexchange.com/questions/44500/how-many-and-which-axes-to-use-for-3d-obb-collision-with-sat
    According to that, this is sufficient to show they do (or don't) intersect
    """
    i_vector = glm.vec4(1, 0, 0, 0)
    j_vector = glm.vec4(0, 1, 0, 0)
    k_vector = glm.vec4(0, 0, 1, 0)
    unit_vectors = (i_vector, j_vector, k_vector)

    local_vectors_1 = [glm.vec3(model1 * unit_vector) for unit_vector in unit_vectors]
    local_vectors_2 = [glm.vec3(model2 * unit_vector) for unit_vector in unit_vectors]

    # generate all local unit vectors
    for axis in itertools.chain(local_vectors_1, local_vectors_2):
        if intersects_on_projection(corners1, corners2, axis) is False:
            return False

    # generate all cross products of local unit vectors
    for unit_vector_1, unit_vector_2 in itertools.product(local_vectors_1, local_vectors_2):
        axis = glm.cross(unit_vector_1, unit_vector_2)
        if axis == glm.vec3(0, 0, 0):
            continue
        if intersects_on_projection(corners1, corners2, axis) is False:
            return False
    return True


cdef bint intersects_on_projection(corners1, corners2, axis):
    cdef min_and_max v1 = get_min_and_max(corners1, axis)
    cdef min_and_max v2 = get_min_and_max(corners2, axis)

    # if they overlap, the sum of the two lengths will be less than the length between the biggest and the smallest
    cdef double total_length = max(v1.max_val, v2.max_val) - min(v1.min_val, v2.min_val)
    cdef double sum_of_both = (v1.max_val - v1.min_val) + (v2.max_val - v2.min_val)
    return total_length < sum_of_both   # can change to =< if you want touching to count as overlapping


cdef min_and_max get_min_and_max(corners, axis):
    # declare min and max as the wrong infinities so any the first data overwrites it
    cdef double min_val = inf
    cdef double max_val = -inf
    cdef double dist
    for corner in corners:
        dist = glm.dot(corner, axis)
        if dist < min_val:
            min_val = dist
        elif dist > max_val:
            max_val = dist
        #min_val = min(min_val, dist)
        #max_val = max(max_val, dist)
    cdef min_and_max rv
    rv.min_val = min_val
    rv.max_val = max_val
    return rv
