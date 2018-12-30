import inspect

from game import Game


class Script:
    """The base class for script objects. Stores the references to the parent (the entity that owns the script) and the
    game object, for convenience."""
    def __init__(self, parent, game, *_args, **_kwargs):
        self.parent = parent
        self.game = game

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('_'):
                continue

            if hasattr(method, 'hook_name') and hasattr(method, 'hook_args'):  # if it's wrapped (eg with `basic_hook`)
                game.add_callback(method.hook_name, method)
            else:
                game.add_callback(name, method)   # if it isn't decorated, add it as a callback anyway, there's no cost


class ScriptGame(Game):
    """An add-on for the Game object that adds support for global scripts. Stores them in a list and does nothing
    with them, just so they dont get garbage collected. TODO do they get gc'd even if they're not stored in a list?"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.global_scripts = []

    def add_global_script(self, script):
        self.global_scripts.append(script(parent=None, game=self))


def basic_hook(name, **args):
    """A keyword taking decorator. Returns a decorator that adds hook data to a method or function.
    called like `@basic_hook('on_key_press')` or by using the convenience functions below"""
    def inner_decorator(method):
        method.hook_name = name
        method.hook_args = args
        return method
    return inner_decorator


########
# below this point is just a bunch of boring, repeated functions. Nothing interesting.

def on_mouse_button():
    return basic_hook('on_mouse_button')


def on_cursor_pos_update():
    return basic_hook('on_cursor_pos_update')


def on_key_press():
    return basic_hook('on_key_press')


def on_char():
    return basic_hook('on_char')


def on_file_drop():
    return basic_hook('on_file_drop')


def on_scroll():
    return basic_hook('on_scroll')


def on_resize():
    return basic_hook('on_resize')
