import engine
import glm
import time
import math
from util import rotate_vec3

class Camera:
    def __init__(self, window: engine.Window):
        self.window = window

        self.position = glm.vec3(0, 0, 3)
        self.velocity = glm.vec3(0, 0, 0)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.normalize(glm.cross(self.front, self.up))

        self.last_cursor_x = 0
        self.last_cursor_y = 0
        self.first_frame = True
        self.sensitivity = 0.01

        self.last_frame_time = time.time()
        self.window.cursor_pos_callback = self.handle_cursor_pos

    def handle_input(self):
        if self.window.gui.focused():
            # don't handle input if the gui is focused
            return

        delta_t = time.time() - self.last_frame_time
        self.last_frame_time = time.time()
        speed = 5 * delta_t

        if self.window.is_pressed(engine.KEY_W):
            self.position += self.front * speed  # move forward slightly
        if self.window.is_pressed(engine.KEY_S):
            self.position -= self.front * speed  # move backwards slightly
        if self.window.is_pressed(engine.KEY_A):
            self.position -= self.right * speed
        if self.window.is_pressed(engine.KEY_D):
            self.position += self.right * speed

        if self.window.is_pressed(engine.KEY_SPACE):
            self.position += self.up * speed
        if self.window.is_pressed(engine.KEY_LEFT_CONTROL):
            self.position -= self.up * speed

        if self.window.is_pressed(engine.KEY_E):
            self.up = glm.vec3(glm.vec4(self.up, 1) * glm.rotate(glm.mat4(1), speed/4, self.front))
            self.right = glm.normalize(glm.cross(self.front, self.up))
        if self.window.is_pressed(engine.KEY_Q):
            self.up = glm.vec3(glm.vec4(self.up, 1) * glm.rotate(glm.mat4(1), -speed/4, self.front))
            self.right = glm.normalize(glm.cross(self.front, self.up))

    def handle_cursor_pos(self, x, y):
        if self.first_frame:  # prevent jump in camera position when initialising the last positions
            self.first_frame = False
            self.last_cursor_x = x
            self.last_cursor_y = y

        self.window.gui.handle_cursor_pos(x, y)

        if self.window.cursor_mode == 'normal':
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
        dot = glm.dot(self.front, self.up)
        angle = math.acos(dot)
        if not (angle <= delta_y or angle - delta_y >= math.pi):
            self.front = rotate_vec3(self.front, axis=self.right, angle=delta_y)

        # also rotate it horizontally, but with no restrictions
        self.front = rotate_vec3(self.front, axis=self.up, angle=delta_x)

    def view_matrix(self):
        target = self.position + self.front  # target is just in front of the camera
        return glm.lookAt(self.position, target, self.up)


