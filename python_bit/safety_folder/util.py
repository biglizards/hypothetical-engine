import glm
import engine


def rotate_vec3(vec, angle, axis):
    return glm.vec3(glm.rotate(glm.mat4(1), angle, axis) * glm.vec4(vec, 1))


def multiply_vec3(vec, mat):
    return glm.vec3(mat * glm.vec4(vec, 1))


def id_to_rgb(i):
    return glm.vec4(((i & 0x000000FF) >> 0) / 255,
                    ((i & 0x0000FF00) >> 8) / 255,
                    ((i & 0x00FF0000) >> 16) / 255,
                    1.0)


def rbg_to_id(r, g, b):
    return r + g*256 + b*256**2


def get_entity_at_pos(game, x, y):
    """
    returns the entity at a given position. Draws to the screen, so dont use this while rendering
    todo check if swap_buffers can be used to swap back to the old thing, so this can be used mid-render

    Assigns an id in the form (0-255, 0-255, 0-255) to each object, draw it in that colour, then check what the colour
    the pixel at that point is. Kinda slow, bit of a hack, but it works for now
    """

    # draw everything in a unique colour
    game.clear_colour(1, 1, 1, 1)
    for i, entity in enumerate(game.entities):
        if not entity.should_render:
            continue
        # ensure both shader programs use the same vertex shader
        if entity.shader_program.paths[0] != entity._click_shader.paths[0]:
            entity.__click_shader = engine.ShaderProgram(entity.shader_program.paths[0], 'shaders/clickHack.frag')
        # swap shader programs
        entity.shader_program, entity._click_shader = entity._click_shader, entity.shader_program
        # render
        entity.shader_program.set_value('entityColour', id_to_rgb(i))
        entity.set_transform_matrix(game)
        entity.draw()
    # apparently the next bit is super slow - rip
    engine.wait_until_finished()

    # swap shaders back to normal
    for entity in game.entities:
        if not entity.should_render:
            continue
        entity.shader_program, entity._click_shader = entity._click_shader, entity.shader_program

    # read pixel value and covert it back to id
    r, g, b, a = game.read_pixel(x, game.height - y)  # todo stop having like 3 different co-ord systems
    index = rbg_to_id(r, g, b)
    # if the index isn't valid, they must have clicked the background
    if index >= len(game.entities):
        return None
    return game.entities[index]


def get_world_space_vector(game, pos_on_screen):
    old_pos = game.camera.position
    game.camera.position = glm.vec3(0, 0, 0)
    vector = glm.inverse(game.projection * game.camera.view_matrix()) * glm.vec4(pos_on_screen, 1, 1)
    vector = glm.normalize(vector)
    game.camera.position = old_pos

    pos_in_world_space = game.camera.position + vector.xyz
    return vector, pos_in_world_space


def solve_simultaneous(point1, vec1, point2, vec2):
    """solves simultaneous equations in the form:
       a: point1 + {lambda} * vec1
       b: point2 + {mu} * vec2
       where {lambda} and {mu} are variables
       returns the point where they intersect, assuming they do.
       Currently unsure what happens if they dont intersect - from the looks of it it gives you the point where they're closest to each other
         (if there's more than one of those points, they must have the same direction vector, and it raises a division by zero error)
       formula taken from stack overflow, adapted to use python: [https://math.stackexchange.com/questions/270767/find-intersection-of-two-3d-lines]
       todo maybe add comments that explain what the heck is going on
    """
    k = (glm.length(glm.cross(vec2, (point2 - point1)))) / (glm.length(glm.cross(vec2, vec1))) * vec1
    if glm.dot(glm.cross(vec2, (point2 - point1)), glm.cross(vec2, vec1)) > 0:
        return point1 + k
    return point1 - k
