import glm

import engine
import script
from physics import two_cubes_intersect


class Physics(script.Script):
    gravity = glm.vec3(0, -1, 0)

    def __init__(self, *args, **kwargs):
        super(Physics, self).__init__(*args, **kwargs)

    @script.every_n_ms(16)
    def do_gravity(self, delta_t):
        # only run every 1/60th of a second or so

        self.parent.velocity += self.gravity * delta_t
        self.parent.position += self.parent.velocity * delta_t
        self.parent.set_transform_matrix()

        for other_entity in self.game.entities:
            if other_entity is self.parent:
                continue
            if two_cubes_intersect(self.parent, other_entity):
                # don't
                self.parent.position -= self.parent.velocity * delta_t
                self.parent.velocity = glm.vec3(0, 0, 0)
                break
