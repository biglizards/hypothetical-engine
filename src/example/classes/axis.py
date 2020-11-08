from enginelib.editor import Editor
from enginelib.game import ManualEntity
import glm
from enginelib import util


class Axis(ManualEntity):
    clickable = False

    def __init__(self, *args, game, data, unit_vector, should_render, **kwargs):
        # awful hack to set the origin in the right place
        # convert the unit vector into an index (ie x: 0, y:1, z:2)
        index = int(glm.length(glm.vec4(0, 1, 2, 1) * unit_vector))
        # mutate the data so the origin of the object is in the centre.
        data = [d + (0.5 if i % 5 == index else 0) for i, d in enumerate(data)]

        super().__init__(*args, game, data, **kwargs)
        self.game = game
        self.unit_vector = unit_vector
        self.scalar = glm.vec3(0.10, 0.10, 0.10) + (unit_vector.xyz * 0.9)
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False
        self.should_render = False

        # dont bother using hooks if not in editor mode
        if not isinstance(game, Editor):
            return

        # set callbacks
        self.game.add_callback('on_drag_update', self.move_axis, editor=True)
        self.game.add_callback('on_click_entity', self.on_click_entity, editor=True)
        self.game.add_callback('on_drag', self.reset_variables, editor=True)  # once the drag finishes, reset everything to none
        self.game.add_callback('before_frame', self.update_variables, editor=True)

    def remove(self):
        self.game.remove_callback('on_drag_update', self.move_axis)
        self.game.remove_callback('on_click_entity', self.on_click_entity)
        self.game.remove_callback('on_drag', self.reset_variables)
        self.game.remove_callback('before_frame', self.update_variables)

    def reset_variables(self, *_args):
        self.offset = None
        self.parent_start_pos = None
        self.is_dragging = False

    def update_variables(self, *_args):
        if self.game.selected_object is not None:
            self.position = self.game.selected_object.position
            self.orientation = self.game.selected_object.orientation
            self.should_render = True
        else:
            self.should_render = False

    def set_drag_start_pos(self):
        self.is_dragging = True
        drag_start_pos = util.get_point_closest_to_cursor(self.game, self.position,
                                                          self.vector(), self.game.cursor_location)
        self.offset = self.game.selected_object.position - drag_start_pos
        self.parent_start_pos = self.game.selected_object.position

    def on_click_entity(self, entity):
        if entity is self:
            self.set_drag_start_pos()

    def vector(self):
        return glm.normalize(glm.vec3(self.game.selected_object.model_mat * self.unit_vector))

    def move_axis(self, *mouse_pos):
        if not self.is_dragging or self.game.selected_object is None:
            return
        target = util.get_point_closest_to_cursor(self.game, self.parent_start_pos, self.vector(), mouse_pos)

        true_target = target + self.offset
        self.game.selected_object.position = true_target
