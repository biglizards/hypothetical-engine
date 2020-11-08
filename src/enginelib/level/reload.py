import importlib
import inspect
from functools import wraps


class Foo(object):
    pass


wrapper_descriptor = type(object.__eq__)
assert wrapper_descriptor.__name__ == 'wrapper_descriptor'


def should_ignore(attr_name, attr):
    # attempt to ignore all the wrapper_descriptors, which are basically the default special methods
    # eg __eq__ on a class that doesnt override __eq__
    # we can ignore these safely, so as not to clutter __dict__
    return attr_name in ['__class__', '__dict__'] or \
           (attr_name.startswith('__') and isinstance(attr, wrapper_descriptor))


class Loader:
    def __init__(self):
        self.loaded_modules = {}  # name: module object
        self.loaded_classes = set()
        self.make_everything_reloadable = False

    def get_newer_class(self, old_class, error=False):
        mod = self.loaded_modules.get(old_class.__module__)
        if not mod:
            text = 'class was not in module cache -- did you load it manually?'
            if error:
                raise RuntimeError(text)
            print("warning:", text)
            return old_class
        return getattr(mod, old_class.__name__)

    def reload(self):
        # load all modules first in case of syntax errors, then swap out old classes with new ones
        for module in self.loaded_modules.values():
            new_module = importlib.reload(module)
            assert module is new_module

        for cls in self.loaded_classes:
            # get new version of class and try to merge them
            new_cls = self.get_newer_class(cls)
            # if the old class was reloadable, wrap the new one as well
            if hasattr(cls, '_is_reloadable_class') and cls._is_reloadable_class:
                reloadable_class(new_cls)

            # not_ignored = []
            # ignored = []

            if hasattr(new_cls, '__pyx_vtable__'):
                # it's a cython object and god i dont even want to get into reloading them
                continue

            for attr_name, attr in inspect.getmembers(new_cls):
                if should_ignore(attr_name, attr):
                    continue
                # not_ignored.append((attr_name, attr))

                if attr_name not in new_cls.__dict__:
                    # it's probably just from a class lower down so ignore it
                    # man we sure are pointlessly parsing the entire mro here by using inspect.getmembers
                    # ignored.append((attr_name, attr))
                    continue

                # ok so static methods are dumb and i hate them because you can't assign them properly
                if attr is not (sm := new_cls.__dict__[attr_name]):
                    if isinstance(sm, staticmethod):
                        setattr(cls, attr_name, sm)
                    else:
                        raise ValueError("you used descriptors and I dont really know what to do there. sorry :(")
                else:
                    # it is a nice sane reasonable attribute that's in __dict__ and means it
                    setattr(cls, attr_name, getattr(new_cls, attr_name))

            # print("done", [(x,y) for (x,y) in ignored if x not in ['__dir__', '__format__', '__init_subclass__', '__new__', '__reduce__', '__reduce_ex__', '__sizeof__', '__subclasshook__', '__weakref__']])

    def handle_module(self, module_name, module, force_reload):
        if module_name not in self.loaded_modules:
            # even if this is the first time seeing a module, it might already have been loaded
            # so make sure to reload it just in case
            if force_reload:
                importlib.reload(module)
            self.loaded_modules[module_name] = module

    def load_class(self, module_name, class_name, force_reload=True):
        module = importlib.import_module(module_name)
        self.handle_module(module_name, module, force_reload)

        class_object = getattr(module, class_name)
        self.loaded_classes.add(class_object)  # since it's a set, we dont need to handle duplicates

        if self.make_everything_reloadable:
            reloadable_class(class_object)

        return class_object

    def add_to_reload_cache(self, class_obj: type, force_reload=True):
        if not type(class_obj) is type:
            # ie they passed an instance by mistake
            raise ValueError("Expected class -- did you pass an instance by mistake?")

        self.load_class(class_obj.__module__, class_obj.__name__, force_reload)


def reloadable(f, original_class=None):
    """
    Makes a function always point to the latest version,
    even if references to it were taken

    without this, bar is not updated when foo is:
    >>> bar = foo.bar
    >>> loader.reload()  # reload foo, changing foo.bar (but not the local reference bar)
    >>> assert bar() == foo.bar()
    AssertionError
    """
    # if it's already wrapped, dont wrap it twice
    if hasattr(f, 'f'):
        return f

    @wraps(f)
    def inner(self, *args, **kwargs):
        if not inner.original_class:
            inner.original_class = self.__class__
        new_f = getattr(inner.original_class, inner.f.__name__).f
        if new_f.__qualname__ != inner.f.__qualname__:
            # uh oh we've got the wrong function
            print("yikes that's not right", self, inner.f)
            raise ValueError("TODO: have inheritance play nicely with reloading")
        else:
            inner.f = new_f
        return inner.f(self, *args, **kwargs)

    inner.f = f
    inner.original_class = original_class
    return inner


def reloadable_class(c):
    for func_name, func in inspect.getmembers(c, predicate=inspect.isfunction):
        if isinstance(inspect.getattr_static(c, func_name), staticmethod):
            continue
        setattr(c, func_name, reloadable(func, original_class=c))
    c._is_reloadable_class = True
    return c
