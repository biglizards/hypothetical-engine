import engine
import glm
import time
import math
from util import rotate_vec3


class BaseCamera:
    def __init__(self, game):
        """
        all camera must implement and keep up to date:
          position (self explanatory)
          front, up, and right: vectors defining the orientation of the camera. since they are all perpendicular, right
                                is entirely dependent on the other two, but is included for convenience and performance
        :param game:
        """
        self.game = game

        self.position = glm.vec3(0, 0, 3)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.normalize(glm.cross(self.front, self.up))

    def view_matrix(self):
        target = self.position + self.front  # target is just in front of the camera
        return glm.lookAt(self.position, target, self.up)


class BasicCamera(BaseCamera):
    def __init__(self, game):
        super().__init__(game)

        self.last_cursor_x = 0
        self.last_cursor_y = 0
        self.first_frame = True
        self.sensitivity = 0.01  # change to taste

        self.game.add_callback('on_cursor_pos_update', self.handle_cursor_pos)

    def handle_cursor_pos(self, x, y):
        if self.first_frame:  # prevent jump in camera position when initialising the last positions
            self.first_frame = False
            self.last_cursor_x = x
            self.last_cursor_y = y

        if self.game.cursor_mode == 'normal':
            return

        delta_x = (self.last_cursor_x - x) * self.sensitivity
        delta_y = (self.last_cursor_y - y) * self.sensitivity

        self.rotate_camera_with_clamping(delta_x, delta_y)
        self.right = glm.normalize(glm.cross(self.front, self.up))

        self.last_cursor_x = x
        self.last_cursor_y = y

    def rotate_camera_with_clamping(self, delta_x, delta_y):
        """Since the camera glitches out if you look too far up or down (ie bending over backwards)
           it is restricted to not be able to do that
           TODO allow that to happen
         """
        angle = math.acos(glm.dot(self.front, self.up))
        if not (angle <= delta_y or angle - delta_y >= math.pi):
            self.front = rotate_vec3(self.front, axis=self.right, angle=delta_y)

        # also rotate it horizontally, but with no restrictions
        self.front = rotate_vec3(self.front, axis=self.up, angle=delta_x)


class InputCamera(BasicCamera):
    """An example showing how a camera can be controlled using user input. This is the camera used in the editor."""
    key_mapping = {'forwards': engine.KEY_W,
                   'backwards': engine.KEY_S,
                   'left': engine.KEY_A,
                   'right': engine.KEY_D,
                   'up': engine.KEY_SPACE,
                   'down': engine.KEY_LEFT_CONTROL,
                   'slow': engine.KEY_LEFT_SHIFT,
                   'rotate_anti_clockwise': engine.KEY_Q,
                   'rotate_clockwise': engine.KEY_E}

    def __init__(self, game):
        super().__init__(game)
        self.last_frame_time = time.time()
        # add editor specific callback in case this is used in editor mode
        self.game.add_callback('on_cursor_pos_update', self.handle_cursor_pos, editor=True)
    
    def key_is_pressed(self, key):
        return self.game.is_pressed(self.key_mapping[key])

    def handle_input(self):
        if self.game.gui.focused():
            # don't handle input if the gui is focused
            return

        delta_t = time.time() - self.last_frame_time
        self.last_frame_time = time.time()
        speed = 5 * delta_t

        if self.key_is_pressed('slow'):
            speed /= 10

        if self.key_is_pressed('forwards'):
            self.position += self.front * speed  # move forward slightly
        if self.key_is_pressed('backwards'):
            self.position -= self.front * speed  # move backwards slightly
        if self.key_is_pressed('left'):
            self.position -= self.right * speed
        if self.key_is_pressed('right'):
            self.position += self.right * speed

        if self.key_is_pressed('up'):
            self.position += self.up * speed
        if self.key_is_pressed('down'):
            self.position -= self.up * speed

        if self.key_is_pressed('rotate_clockwise'):
            self.up = glm.vec3(glm.vec4(self.up, 1) * glm.rotate(glm.mat4(1), speed/4, self.front))
            self.right = glm.normalize(glm.cross(self.front, self.up))
        if self.key_is_pressed('rotate_anti_clockwise'):
            self.up = glm.vec3(glm.vec4(self.up, 1) * glm.rotate(glm.mat4(1), -speed/4, self.front))
            self.right = glm.normalize(glm.cross(self.front, self.up))


Camera = InputCamera
