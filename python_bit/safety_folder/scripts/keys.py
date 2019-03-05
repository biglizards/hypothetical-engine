import script
import engine


class CustomKeyPresses(script.Script):
    @script.on_key_press(editor=True)
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
