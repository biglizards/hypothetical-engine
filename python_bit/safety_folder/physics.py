import glm
import itertools
from math import inf
from game import Entity
import cube

def generate_aabb(entity: Entity):
    model = entity.generate_model(ignore_orientation=True)
    aabb_min = model * glm.vec4(cube.aabb_min, 1)
    aabb_max = model * glm.vec4(cube.aabb_max, 1)
    return aabb_min, aabb_max


def aabb_intersect(min1, max1, min2, max2):
    return min1.x <= max2.x and max1.x >= min2.x and \
           min1.y <= max2.y and max1.y >= min2.y and \
           min1.z <= max2.z and max1.z >= min2.z


def two_cubes_intersect(cube1, cube2):
    # if glm.length(cube1.position - cube2.position) > 6:  # obtained by pythag, todo use bounding spheres
    #    return False
    corners1 = cube1.get_corners()
    corners2 = cube2.get_corners()
    return unaligned_intersect(corners1, cube1.model, corners2, cube2.model)


def unaligned_intersect(corners1, model1, corners2, model2):
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


def intersects_on_projection(corners1, corners2, axis):
    min1, max1 = get_min_and_max(corners1, axis)
    min2, max2 = get_min_and_max(corners2, axis)

    # if they overlap, the sum of the two lengths will be less than the length between the biggest and the smallest
    total_length = max(max1, max2) - min(min1, min2)
    sum_of_both = (max1 - min1) + (max2 - min2)
    return total_length <= sum_of_both   # can change to <= if you want touching to count as overlapping


def get_min_and_max(corners, axis):
    # declare min and max as the wrong infinities so any the first data overwrites it
    min_val = inf
    max_val = -inf
    for corner in corners:
        dist = glm.dot(corner, axis)
        if dist < min_val:
            min_val = dist
        elif dist > max_val:
            max_val = dist
    return min_val, max_val
