import glm
import inspect
import itertools
import json
import warnings
from warnings import warn

from game import Entity
from script import Script


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


def convert_args_to_kwargs(entity, args):
    raise NotImplementedError(f"entity {entity} has positional args, but these are not supported yet!")


# noinspection PyProtectedMember
def handle_entity(entity):
    # ensure entity is valid and serialisable
    if not hasattr(entity, '_args') or not hasattr(entity, '_kwargs'):
        raise AttributeError(f"Unable to serialise {entity} (did not have attributes '_args and _kwargs')")
    if entity.__class__.__module__ is None:
        raise AttributeError(f"Could not get module name for {entity.__class__}")
    if entity.__class__.__module__ == "__main__":
        warn(f"WARNING: {entity.__class__} declared in __main__, please do not do that", RuntimeWarning)

    # there seems to be some controversy over how to get the module and class name from a class
    # after reading https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
    # i'm using the top answer but using __qualname__ instead
    entity_obj = {'@type': 'entity', '@class_module': entity.__class__.__module__,
                  '@class_name': entity.__class__.__qualname__}
    if entity._args:
        entity_obj.update(handle_item(convert_args_to_kwargs(entity, entity._args)))

    # set the base arguments to the original arguments
    for arg_name, value in entity._kwargs.items():
        if arg_name not in entity.savable_attributes:
            entity_obj[arg_name] = handle_item(value)

    # replace any arguments that might have been updated after instantiation
    for arg_name, attr_name in entity.savable_attributes.items():
        entity_obj[arg_name] = handle_item(getattr(entity, attr_name))

    # handle any overrides, if they exist
    overrides = getattr(entity, 'save_overrides', {})
    for arg_name, value in overrides.items():
        entity_obj[arg_name] = handle_item(value)

    # todo 1. raise error if arg names change
    # todo 2. add way to change signature of entity without breaking saves
    # todo 3. try to re-import the name to make sure it worked and refers to the correct thing (cont)
    # and/or only accept classes that can be guaranteed to be available in PYTHONPATH like the library,
    # or files within the bit of the level that gets zipped (like example_app/classes/my_custom_class.py)
    return entity_obj


def handle_entity_ref(entity):
    if hasattr(entity, 'game'):  # todo refactor to allow this to access `game`
        assert entity in entity.game.all_entities
    return {'@type': 'entity_ref', 'id': entity.id}


def handle_script(script):
    script_obj = handle_entity(script)  # yeah i know this looks strange but stick with me
    script_obj['@type'] = 'script'
    # script_obj['parent'] = handle_item(script.parent)
    return script_obj


def handle_script_cls(cls, name):
    return {'@type': 'script_cls', '@name': name, '@class_module': cls.__module__, '@class_name': cls.__qualname__}


handlers = {int: lambda x: x,
            str: lambda x: x,
            float: lambda x: x,
            bool: lambda x: x,
            type(None): lambda x: x,
            dict: lambda data: {name: handle_item(value) for name, value in data.items()},
            list: lambda x: [handle_item(z) for z in x],
            tuple: lambda x: [handle_item(z) for z in x],  # todo have this not be a list because that's wrong
            Entity: handle_entity_ref,
            Script: handle_script,
            glm.vec2: lambda x: {'@type': 'vec2', 'values': list(x)},
            glm.vec3: lambda x: {'@type': 'vec3', 'values': list(x)},
            glm.vec4: lambda x: {'@type': 'vec4', 'values': list(x)},
            # in quaternions, args are given in (w, x, y, z), but list(x) = (x, y, z, w)
            # oddly, however, if you pass a list, it reads in in (x, y, z, w) order, so quat(list(quat)) = quat
            glm.quat: lambda x: {'@type': 'quat', 'values': list(x)},  # list(x)[-1:] + list(x)[:3]
            }


def save_level(location, editor):
    editor.dispatch('on_save')
    save_file = {}

    processed_entities = {}  # id: {entity...}
    for entity in itertools.chain(editor.entities, editor.overlay_entities):
        entity_obj = handle_entity(entity)
        assert entity.id not in processed_entities, 'duplicate id not allowed'
        processed_entities[entity_obj['id']] = entity_obj
    save_file['entities'] = processed_entities

    save_file['models'] = handle_item(editor.models)
    save_file['scripts'] = [handle_script_cls(cls, name) for cls, name in editor.scripts.items()]

    with open(location, 'w') as f:
        json.dump(save_file, f, indent=4)

    editor.dispatch('after_save')
