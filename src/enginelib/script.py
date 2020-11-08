import inspect
from collections import defaultdict
from functools import wraps

from enginelib.level import load


class Script:
    """The base class for script objects. Stores the references to the parent (the entity that owns the script) and the
    game object, for convenience."""
    def __init__(self, parent, game, *_args, **_kwargs):
        self.parent = parent
        self.game = game
        self.savable_attributes = {}
        self.property_blacklist = ['parent', 'game', 'savable_attributes', 'property_blacklist']
        # note: args and kwargs are set in editor.add_script, not here, since we dont get args from subclasses etc.
        self._args = []
        self._kwargs = {}
        add_hook_callbacks(self, self.game, add_everything=True)

    def __new__(cls, *args, **kwargs):
        """Called when creating a new script instance. If the class has been reloaded, use the newer version instead"""
        # note: without this, calling super with a reloaded class always raises an error
        new_cls = load.loader.get_newer_class(cls)
        obj = object.__new__(new_cls)
        if cls is not new_cls:
            # __init__ is not automatically called if we return the "wrong" class, so call it manually
            obj.__init__(*args, **kwargs)

        return obj

    def remove(self):
        remove_hook_callbacks(self, self.game, remove_everything=True)
        self.parent.scripts.remove(self)


def iterate_over_methods_and_call_function_if_they_are_a_hook(self, function, do_everything=False):
    for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
        if name.startswith('_'):
            continue

        if hasattr(method, 'hook_name') and hasattr(method, 'hook_args'):  # if it's wrapped (eg with `basic_hook`)
            function(method.hook_name, method)
        elif do_everything:
            function(name, method)  # if it isn't decorated, add it as a callback anyway, there's no cost


def add_hook_callbacks(self, game, add_everything=False):
    iterate_over_methods_and_call_function_if_they_are_a_hook(self, game.add_callback, add_everything)


def remove_hook_callbacks(self, game, remove_everything=False):
    iterate_over_methods_and_call_function_if_they_are_a_hook(self, game.remove_callback, remove_everything)


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
        wrapper.func = method
        # testing out a new thing
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


def on_click_entity(**kwargs):
    return basic_hook('on_click_entity', **kwargs)
