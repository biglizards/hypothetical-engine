import glm
import itertools
from math import inf
from enginelib.game import Entity


# def generate_aabb(entity: Entity):
#     model_mat = entity.generate_model_mat(ignore_orientation=True)
#     aabb_min = model_mat * glm.vec4(cube.aabb_min, 1)
#     aabb_max = model_mat * glm.vec4(cube.aabb_max, 1)
#     return aabb_min, aabb_max


def aabb_intersect(min1, max1, min2, max2):
    return min1.x <= max2.x and max1.x >= min2.x and \
           min1.y <= max2.y and max1.y >= min2.y and \
           min1.z <= max2.z and max1.z >= min2.z


def two_entities_intersect(entity1, entity2):
    if not all(entity.do_collisions for entity in (entity1, entity2)):
        return False

    if glm.length(entity1.position - entity2.position) \
            > (entity1.bounding_radius * max(entity1.scalar)) + (entity2.bounding_radius * max(entity2.scalar)):
        return False  # bounding spheres dont intersect

    for mesh1 in entity1.meshes:
        if glm.length(entity1.position + mesh1.centre - entity2.position) \
                > (mesh1.bounding_radius * max(entity1.scalar)) + (entity2.bounding_radius * max(entity2.scalar)):
            continue  # the meshes sphere doesnt intersect with entity2's

        for mesh2 in entity2.meshes:
            if glm.length(entity1.position + mesh1.centre - entity2.position - mesh2.centre) \
                    > (mesh1.bounding_radius * max(entity1.scalar)) + (mesh2.bounding_radius * max(entity2.scalar)):
                continue
            # both bounding spheres intersect -- the two meshes need to be checked to each other
            if two_meshes_intersect(mesh1, mesh2, entity1, entity2):
                return True


def two_meshes_intersect(mesh1, mesh2, entity1, entity2):
    corners1 = [glm.vec3(entity1.model_mat * glm.vec4(corner, 1)) for corner in mesh1.corners]
    corners2 = [glm.vec3(entity2.model_mat * glm.vec4(corner, 1)) for corner in mesh2.corners]
    return unaligned_intersect(corners1, entity1.model_mat, corners2, entity2.model_mat)


def unaligned_intersect(corners1, model_mat1, corners2, model_mat2):
    """
    adapted from explanation at
    https://gamedev.stackexchange.com/questions/44500/how-many-and-which-axes-to-use-for-3d-obb-collision-with-sat
    According to that, this is sufficient to show two OBB do (or don't) intersect
    """
    i_vector = glm.vec4(1, 0, 0, 0)
    j_vector = glm.vec4(0, 1, 0, 0)
    k_vector = glm.vec4(0, 0, 1, 0)
    unit_vectors = (i_vector, j_vector, k_vector)

    local_vectors_1 = [glm.vec3(model_mat1 * unit_vector) for unit_vector in unit_vectors]
    local_vectors_2 = [glm.vec3(model_mat2 * unit_vector) for unit_vector in unit_vectors]

    # generate all local unit vectors
    for axis in itertools.chain(local_vectors_1, local_vectors_2):
        if intersects_on_projection(corners1, corners2, axis) is False:
            return False

    # generate all cross products of local unit vectors
    for unit_vector_1, unit_vector_2 in itertools.product(local_vectors_1, local_vectors_2):
        axis = glm.cross(unit_vector_1, unit_vector_2)
        if axis == glm.vec3(0, 0, 0):  # vectors were the same, so skip it
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
    # declare min and max as the wrong infinities so any (ie the first) data overwrites it
    min_val = inf
    max_val = -inf
    for corner in corners:
        dist = glm.dot(corner, axis)
        if dist < min_val:
            min_val = dist
        elif dist > max_val:
            max_val = dist
    return min_val, max_val
