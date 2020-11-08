# hypothetical-engine

This is (and likely will forever be) a work in progress. Since the bulk of the engine is written in python, you can (and are encouraged to) subclass `Game`, `Entity`, etc to modify behaviours (including changing almost anything about the editor itself).

## Examples

### Scripting

Scripts are written in Python. Example:

```py
from enginelib import script
import glm


class CrateSpinner(script.Script):
    # allow changes to speed to persist across restarts
    savable_attributes = {'speed': 'speed'}

    # all scripts are given a reference to the entity they're attached to and the game god object
    def __init__(self, parent, game, speed=1):
        super().__init__(parent, game)
        self.speed = speed

    # any methods with script.on_* decorators will be called when the relevant event occurs
    # this one is called at the start of each frame
    @script.on_frame()
    def spin_crate(self, delta_t):
        angle = self.speed * delta_t
        # rotate parent around some arbitrarily chosen axis
        self.parent.orientation = glm.rotate(self.parent.orientation, angle, glm.vec3(0.5, 1, 0))
```

![scripts.gif](https://github.com/biglizards/hypothetical-engine/raw/master/resources/script.gif)

### Models
Any model type supported by [assimp](https://github.com/assimp/assimp) can be loaded, in theory. Changing an object's model is easy, and you can import more using a file dialogue.

![models.gif](https://github.com/biglizards/hypothetical-engine/raw/master/resources/models.gif)

### Physics
We support a simple physics and collision engine by default (provided via a script)

![physics.gif](https://github.com/biglizards/hypothetical-engine/raw/master/resources/physics.gif)

### Audio
Audio importing and playing (including positional audio) is possible. I will convey this to you using a static image:

![audio.png](https://github.com/biglizards/hypothetical-engine/raw/master/resources/audio.png)

## Attributions
Who Likes to Party by Kevin MacLeod
Link: https://incompetech.filmmusic.io/song/4627-who-likes-to-party
License: http://creativecommons.org/licenses/by/4.0/

Blender-chan model by SearKitchen
https://sketchfab.com/3d-models/blender-chan-6835f0d60e0c4813812c0247e3b73da7