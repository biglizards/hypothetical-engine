import script


class EditorScripts(script.Script):
    @script.every_n_ms(50)
    def refresh_gui(self, _delta_t):
        try:
            self.game.update_entity_list()
            self.game.property_window_helper.refresh()
            self.game.gui.update_layout()
        except AttributeError:
            pass

