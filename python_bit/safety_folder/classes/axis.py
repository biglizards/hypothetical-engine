from game import ManualEntity
import glm
import util


class Axis(ManualEntity):
    clickable = False

    def __init__(self, *args, game, data, unit_vector, should_render, **kwargs):
        # awful hack to set the origin in the right place, todo remove when you add model loading
        # convert the unit vector into an index (ie x: 0, y:1, z:2)
        index = int(glm.length(glm.vec4(0, 1, 2, 1) * unit_vector))
        # mutate the data so the origin of the object is in the centre.
        data = [d + (0.5 if i % 5 == index else 0) for i, d in enumerate(data)]

        super().__init__(*args, game, data, **kwargs)
        self.game = game
        self.unit_vector = unit_vector
        self.scalar = glm.vec3(0.10, 0.10, 0.10) + (unit_vector.xyz * 0.9)
        self.parent = None
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False
        self.should_render = False
        # set callbacks
        self.game.add_callback('on_drag_update', self.move_axis)
        self.game.add_callback('on_click_entity', self.set_drag_start_pos)
        self.game.add_callback('on_drag', self.reset_variables)  # once the drag finishes, reset everything to none
        self.game.add_callback('before_frame', self.update_variables)

    def reset_variables(self, *_args):
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False

    def update_variables(self, *_args):
        if self.parent is not None:
            self.position = self.parent.position
            self.orientation = self.parent.orientation
            self.should_render = True

    def set_drag_start_pos(self, entity):
        if entity is self:
            self.is_dragging = True
            drag_start_pos = util.get_point_closest_to_cursor(self.game, self.position,
                                                              self.vector(), self.game.cursor_location)
            self.offset = self.parent.position - drag_start_pos
            self.parent_start_pos = self.parent.position
        elif util.is_clickable(entity):  # todo maybe replace with entity is game.selected_object
            self.parent = entity
        if entity is None:
            self.should_render = False

    def vector(self):
        return glm.normalize(glm.vec3(self.parent.model_mat * self.unit_vector))

    def move_axis(self, *mouse_pos):
        if not self.is_dragging:
            return None
        target = util.get_point_closest_to_cursor(self.game, self.parent_start_pos, self.vector(), mouse_pos)

        true_target = target + self.offset
        self.parent.position = true_target
