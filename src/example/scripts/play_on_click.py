from enginelib import script


class PlayOnClick(script.Script):
    @script.on_click_entity()
    def spin_crate(self, entity):
        if entity is self.parent:
            print("yay2")
            self.parent.play_audio()
