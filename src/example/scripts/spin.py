from enginelib import script
import glm

from enginelib.level.reload import reloadable


class CrateSpinner(script.Script):
    # allow changes to speed to persist across restarts
    savable_attributes = {'speed': 'speed'}

    # all scripts are given a reference to the entity they're attached to and the game god object
    def __init__(self, parent, game, speed=1):
        # super().__init__(parent, game)
        super(self.__class__, self).__init__(parent, game)
        self.speed = speed

    # any methods with script.on_* decorators will be called when the relevant event occurs
    # this one is called at the start of each frame
    @script.on_frame()
    def spin_crate(self, delta_t):
        angle = self.speed * delta_t
        # rotate parent around some arbitrarily chosen axis
        self.parent.orientation = glm.rotate(self.parent.orientation, angle, glm.vec3(0.5, 1, 0))
