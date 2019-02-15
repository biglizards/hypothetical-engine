import importlib

import json
import glm


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
    kwargs = {name: handle_item(item, game)
              for name, item in data.items()
              if not name.startswith('@')}
    args = handle_item(data['@args'], game)

    entity_class = load_entity_class(module_name=data['@class_module'],
                                     class_name=data['@class_name'])

    game.create_entity(*args, entity_class=entity_class, **kwargs)


def load_entity_class(module_name, class_name):
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


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
    'entity': handle_entity,
}


def load_level(location, game):
    with open(location, 'r') as f:
        entity_list = json.load(f)

    # since the file is a list of (probably) entities, we call handle_item to call the relevant handler
    for entity in entity_list:
        handle_item(entity, game)