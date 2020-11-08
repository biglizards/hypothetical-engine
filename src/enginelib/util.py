import glm
import engine
import importlib.util


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


# noinspection PyProtectedMember
def draw_entity_click_hack(i, entity):
    # ensure both shader programs use the same vertex shader
    if entity.shader_program.paths[0] != entity._click_shader.paths[0]:
        entity._click_shader = engine.ShaderProgram(entity.shader_program.paths[0], 'shaders/clickHack.frag')
    # render
    entity._click_shader.set_value('entityColour', id_to_rgb(i))
    entity.set_transform_matrix(entity._click_shader)
    entity.draw_with_shader(entity._click_shader)


def get_entity_at_pos(game, x, y):
    """
    returns the entity at a given position. Draws to the screen, so dont use this while rendering

    Assigns an id in the form (0-255, 0-255, 0-255) to each object, draw it in that colour, then check what the colour
    the pixel at that point is. Kinda slow, bit of a hack, but it works for now
    """

    # set background to white
    game.clear_colour(1, 1, 1, 1)
    # draw everything in a unique colour
    for i, entity in enumerate(game.entities):
        if entity.should_render:
            draw_entity_click_hack(i, entity)

    # if there are any, draw overlay entities like axes over the top of the rest of the entities
    if hasattr(game, "overlay_entities"):
        # draw overlay entities on top
        game.clear(engine.DEPTH_BUFFER_BIT)
        for i, entity in enumerate(game.overlay_entities, start=len(game.entities)):
            if entity.should_render:
                draw_entity_click_hack(i, entity)

    # create list of target entities.
    entity_list = list(game.all_entities)  # wow this is horrible for memory usage

    # apparently the next bit is super slow - rip
    engine.wait_until_finished()

    # read pixel value and covert it back to id
    r, g, b, a = game.read_pixel(x, game.height - y)  # glReadPixels and glfwGetCursorPos have different origins
    index = rbg_to_id(r, g, b)
    # if the index isn't valid, they must have clicked the background
    if index >= len(entity_list):
        return None
    return entity_list[index]


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
    """
    k = (glm.length(glm.cross(vec2, (point2 - point1)))) / (glm.length(glm.cross(vec2, vec1))) * vec1
    if glm.dot(glm.cross(vec2, (point2 - point1)), glm.cross(vec2, vec1)) > 0:
        return point1 + k
    return point1 - k


def to_ndc(game, x, y):
    return ((x / game.width) - 0.5) * 2, ((y / game.height) - 0.5) * -2


def get_point_closest_to_cursor(game, position, vector, cursor_pos=None):
    """projects a line from the cursor into the world and returns the point of intersection
       with another line in world space.
       created for the draggable local axes in the editor
       """
    if cursor_pos is None:
        cursor_pos = game.cursor_location_ndc
    else:
        cursor_pos = to_ndc(game, *cursor_pos)

    screen_vector, pos_in_world_space = get_world_space_vector(game, cursor_pos)
    point_of_intersection = solve_simultaneous(position, vector,
                                               game.camera.position, screen_vector.xyz)
    return point_of_intersection


def is_clickable(entity):
    return not (hasattr(entity, 'clickable') and entity.clickable is False)


def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    foo = importlib.util.module_from_spec(spec)
    return spec.loader.exec_module(foo)
