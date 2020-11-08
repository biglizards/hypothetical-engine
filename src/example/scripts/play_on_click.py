from enginelib import script


class PlayOnClick(script.Script):
    @script.on_click_entity()
    def play_on_click(self, entity):
        if entity is self.parent:
            self.parent.play_audio()
