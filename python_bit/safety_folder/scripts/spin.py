from enginelib import script
import glm


class CrateSpinner(script.Script):
    base_speed = 1
    savable_attributes = {'speed': 'speed'}

    def __init__(self, parent, game, *_args, speed=1, **_kwargs):
        super().__init__(parent, game, *_args, **_kwargs)
        self.speed = speed

    @script.on_frame()
    def spin_crate(self, delta_t):
        angle = self.base_speed * self.speed * delta_t * glm.radians(15 * (0 + 1))
        self.parent.orientation = glm.rotate(self.parent.orientation, angle, glm.vec3(0.5, 1, 0))
