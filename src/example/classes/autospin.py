from enginelib.entity import Entity
from scripts.spin import CrateSpinner


class AutoSpin(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.scripts:
            self.game.create_script(self, CrateSpinner)
