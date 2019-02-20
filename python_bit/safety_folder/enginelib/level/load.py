import functools
import importlib

import json
import glm
from warnings import warn


def handle(data, game):
    output_data = {}
    for name, value in data.items():
        output_data[name] = handle_item(value, game)
    return output_data


# noinspection PyCallingNonCallable
def handle_item(item, game):
    return handlers[type(item)](item, game)


# noinspection PyCallingNonCallable
def handle_dict(value, game):
    # if it's a dict, it might be a serialised object. Check if it is.
    object_type = value.get('@type')
    if object_type is not None:
        # it was a serialised object, so select the right handler for it
        return handlers[object_type](value, game)
    # it wasn't, so actually is just a dict. Handle as normal.
    return handle(value, game)


def handle_entity(data, game):
    args, kwargs, entity_class = extract_entity_data(data, game)
    game.create_entity(*args, entity_class=entity_class, **kwargs)


def handle_script(data, game):
    args, kwargs, script_class = extract_entity_data(data, game)
    return functools.partial(game.create_script, *args, script_class=script_class, **kwargs)


def extract_entity_data(data, game):
    kwargs = {name: handle_item(item, game)
              for name, item in data.items()
              if not name.startswith('@')}
    args = handle_item(data.get('@args', []), game)  # @args is deprecated and should no longer exist
    if args:
        warn("@args is deprecated", DeprecationWarning)

    entity_class = load_entity_class(module_name=data['@class_module'],
                                     class_name=data['@class_name'])

    return args, kwargs, entity_class


def load_entity_class(module_name, class_name):
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def handle_entity_ref(data, game):
    return game.entities_by_id[data['id']]


# handlers in the form {@type: handler(data, game), ...}
handlers = {
    int: lambda x, _: x,
    str: lambda x, _: x,
    float: lambda x, _: x,
    bool: lambda x, _: x,
    type(None): lambda x, _: x,
    dict: handle_dict,
    list: lambda x, game: [handle_item(z, game) for z in x],
    'vec2': lambda x, _: glm.vec2(x['values']),
    'vec3': lambda x, _: glm.vec3(x['values']),
    'vec4': lambda x, _: glm.vec4(x['values']),
    'quat': lambda x, _: glm.quat(x['values']),
    'entity': handle_entity,
    'entity_ref': handle_entity_ref,
    'script': handle_script,
}


def load_level(location, game):
    with open(location, 'r') as f:
        save_obj = json.load(f)
    entity_dict = save_obj['entities']

    # since the dict is full of (hopefully) entities, we call handle_item to call the relevant handler
    for entity in entity_dict.values():
        handle_item(entity, game)
