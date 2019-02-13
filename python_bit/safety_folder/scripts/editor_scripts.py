import engine
import script


class EditorScripts(script.Script):
    @script.every_n_ms(100)
    def refresh_gui(self, delta_t):
        try:
            self.game.property_window_helper.refresh()
            self.game.gui.update_layout()
        except AttributeError:
            pass

