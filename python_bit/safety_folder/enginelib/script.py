import inspect
from collections import defaultdict
from functools import wraps


class Script:
    """The base class for script objects. Stores the references to the parent (the entity that owns the script) and the
    game object, for convenience."""
    def __init__(self, parent, game, *_args, **_kwargs):
        self.parent = parent
        self.game = game
        self.savable_attributes = {}
        # note: args and kwargs are set in editor.add_script, not here, since we dont get args from subclasses etc.
        self._args = []
        self._kwargs = {}

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('_'):
                continue

            if hasattr(method, 'hook_name') and hasattr(method, 'hook_args'):  # if it's wrapped (eg with `basic_hook`)
                # todo either find a use for hook_args or get rid of it
                game.add_callback(method.hook_name, method)
            else:
                game.add_callback(name, method)   # if it isn't decorated, add it as a callback anyway, there's no cost

    def remove(self):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('_'):
                continue

            if hasattr(method, 'hook_name') and hasattr(method, 'hook_args'):  # if it's wrapped (eg with `basic_hook`)
                # todo either find a use for hook_args or get rid of it
                self.game.remove_callback(method.hook_name, method)
            else:
                self.game.remove_callback(name, method)   # if it isn't decorated, add it as a callback anyway, there's no cost

        self.parent.scripts.remove(self)
        # for thing in gc.get_referrers(self):
        #     print(thing, gc.get_referrers(thing))


def basic_hook(name, **args):
    """A keyword taking decorator. Returns a decorator that adds hook data to a method or function.
    called like `@basic_hook('on_key_press')` or by using the convenience functions below"""
    def inner_decorator(method):
        method.hook_name = name
        method.hook_args = args
        return method
    return inner_decorator


def every_n_ms(n, **args):
    n /= 1000  # convert from ms to seconds

    def decorator(method):
        time_elapsed = defaultdict(float)  # format {self: time}

        @wraps(method)
        def wrapper(self, delta_t, *args, **kwargs):
            time_elapsed[self] += delta_t
            if time_elapsed[self] > n:
                method(self, time_elapsed[self], *args, **kwargs)
                time_elapsed[self] = 0
        wrapper.hook_name = 'on_frame'
        wrapper.hook_args = args
        return wrapper
    return decorator


########
# below this point is just a bunch of boring, repeated functions for the sake of autocomplete. Nothing interesting.

def on_mouse_button(**kwargs):
    return basic_hook('on_mouse_button', **kwargs)


def on_cursor_pos_update(**kwargs):
    return basic_hook('on_cursor_pos_update', **kwargs)


def on_key_press(**kwargs):
    return basic_hook('on_key_press', **kwargs)


def on_char(**kwargs):
    return basic_hook('on_char', **kwargs)


def on_file_drop(**kwargs):
    return basic_hook('on_file_drop', **kwargs)


def on_scroll(**kwargs):
    return basic_hook('on_scroll', **kwargs)


def on_resize(**kwargs):
    return basic_hook('on_resize', **kwargs)


def on_frame(**kwargs):
    return basic_hook('on_frame', **kwargs)
