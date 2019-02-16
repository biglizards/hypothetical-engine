import glm
import inspect
import itertools
import json
import warnings
from warnings import warn

from game import Entity


def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return str(msg) + '\n'


warnings.formatwarning = custom_formatwarning


# noinspection PyCallingNonCallable
def handle_item(item):
    for base_class in inspect.getmro(item.__class__):
        handler = handlers.get(base_class)
        if handler is None:
            continue
        object_data = handler(item)
        # if the handler was for a parent class, make sure it includes the name of the subclass in the data
        if type(item) != base_class and ('@class_module' not in object_data or '@class_name' not in object_data):
            warn(f"WARNING: Save handler for class '{base_class}' does not set '@class_module' and '@class_name' "
                 f"but has subclass '{type(item)}', so this handler is being skipped. "
                 f"Consider modifying it or writing your own.", RuntimeWarning)
            continue
        return object_data
    raise KeyError(f"No save handler could be found for class '{item.__class__}'")


def handle_entity(entity):
    # ensure entity is valid and serialisable
    if not hasattr(entity, '_args') or not hasattr(entity, '_kwargs'):
        raise AttributeError(f"Unable to serialise entity {entity} (did not have attributes '_args and _kwargs')")
    if entity.__class__.__module__ is None:
        raise AttributeError(f"Could not get module name for entity class {entity.__class__}")
    if entity.__class__.__module__ == "__main__":
        warn(f"WARNING: entity class '{entity.__class__}' declared in __main__, please do not do that", RuntimeWarning)

    # there seems to be some controversy over how to get the module and class name from a class
    # after reading https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
    # i'm using the top answer but using __qualname__ instead
    entity_obj = {'@type': 'entity', '@class_module': entity.__class__.__module__,
                  '@class_name': entity.__class__.__qualname__,
                  '@args': handle_entity_args(entity, entity._args)}
    entity_obj.update(handle_entity_kwargs(entity, entity._kwargs))
    # todo 1. raise error if arg names change
    # todo 2. add way to change signature of entity without breaking saves
    # todo 3. try to re-import the name to make sure it worked and refers to the correct thing (cont)
    # and/or only accept classes that can be guaranteed to be available in PYTHONPATH like the library,
    # or files within the bit of the level that gets zipped (like example_app/classes/my_custom_class.py)
    return entity_obj


def handle_entity_args(entity, args):
    handled_args = []
    for i, name, initial_value in enumerate(zip(args, inspect.getfullargspec(entity.__init__).args)):
        try:
            handled_args.append(handle_entity_arg(entity, name, initial_value))
        except AttributeError:
            handled_args.append(handle_item(initial_value))
    return args


def handle_entity_kwargs(entity, kwargs):
    handled_kwargs = {}
    for name, initial_value in kwargs.items():
        try:
            handled_kwargs[name] = handle_entity_kwarg(entity, name, initial_value)
        except AttributeError:
            handled_kwargs[name] = handle_item(initial_value)
    return handled_kwargs


def handle_entity_arg(entity, name, initial_value):
    """
    if the entity has an attribute with the same name as an argument, try to take that as our value
    instead of the initial value passed to __init__ (to account for stuff like entity.position changing)
    raises AttributeError, which is caught by `handle_entity_args`
    """

    new_value = getattr(entity, name)
    if not isinstance(new_value, type(initial_value)) and initial_value is not None:
        warn(f"WARNING: value {name} of entity {entity} changed type from __init__ argument. "
             f"Consider renaming it.")
        return
    return handle_item(initial_value)


def handle_entity_kwarg(entity, name, initial_value):
    """
    if the entity has an attribute with the same name as an argument, try to take that as our value
    instead of the initial value passed to __init__ (to account for stuff like entity.position changing)
    raises AttributeError, which is caught by `handle_entity_kwargs`
    """

    new_value = getattr(entity, name)
    if not isinstance(new_value, type(initial_value)) and initial_value is not None :
        warn(f"WARNING: value {name} of entity {entity} changed type from __init__ argument. "
             f"Consider renaming it.")
        return
    return handle_item(initial_value)


handlers = {int: lambda x: x,
            str: lambda x: x,
            float: lambda x: x,
            bool: lambda x: x,
            type(None): lambda x: x,
            dict: lambda data: {name: handle_item(value) for name, value in data.items()},
            list: lambda x: [handle_item(z) for z in x],
            tuple: lambda x: [handle_item(z) for z in x],  # todo have this not be a list because that's wrong
            Entity: handle_entity,
            glm.vec2: lambda x: {'@type': 'vec2', 'values': list(x)},
            glm.vec3: lambda x: {'@type': 'vec3', 'values': list(x)},
            glm.vec4: lambda x: {'@type': 'vec4', 'values': list(x)},
            }


def save_level(location, editor):
    processed_entities = []
    for entity in itertools.chain(editor.entities, editor.overlay_entities):
        entity_obj = handle_item(entity)
        processed_entities.append(entity_obj)

    with open(location, 'w') as f:
        json.dump(processed_entities, f, indent=4)
