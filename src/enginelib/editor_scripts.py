import engine

from enginelib import script


class EditorScripts(script.Script):
    @script.every_n_ms(1000, editor=True)
    def refresh_gui(self, _delta_t):
        try:
            self.game.update_entity_list()
            # self.game.property_window_helper.refresh()
            # self.game.gui.update_layout()
        except AttributeError:
            pass

    @script.on_key_press(always_fire=True)
    def do_stuff(self, key, _scancode, action, _mods):
        if action != engine.KEY_PRESS:
            return

        if key == engine.KEY_Z:
            self.game.close()
        if key == engine.KEY_X:
            self.game.set_cursor_capture('disabled')
            # prevent the camera from jumping when switching between normal and disabled without moving the mouse
            self.game.camera.first_frame = True
        if key == engine.KEY_C:
            self.game.set_cursor_capture('normal')
        if key == engine.KEY_ESCAPE:
            self.game.select_entity(None)


