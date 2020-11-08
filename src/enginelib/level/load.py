import functools
import importlib

import json
import glm
from warnings import warn

from enginelib.level.reload import Loader

loader = Loader()


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

    entity_class = loader.load_class(module_name=data['@class_module'],
                                     class_name=data['@class_name'])

    return args, kwargs, entity_class


def handle_entity_ref(data, game):
    return game.entities_by_id[data['id']]


def handle_cls(data, _):
    return loader.load_class(module_name=data['@class_module'], class_name=data['@class_name']), data['@name']


def identity(x, _game):
    """return the first argument. used for types that are directly serialisable"""
    return x


# handlers in the form {@type: handler(data, game), ...}
# the reason some are strings and some aren't is because basic types are deserialized and then handled,
# but non-json types are represented as dictionaries (see handle_dict for more)
handlers = {
    int: identity, str: identity, float: identity, bool: identity, type(None): identity,
    dict: handle_dict,
    list: lambda x, game: [handle_item(z, game) for z in x],
    'vec2': lambda x, _: glm.vec2(x['values']),
    'vec3': lambda x, _: glm.vec3(x['values']),
    'vec4': lambda x, _: glm.vec4(x['values']),
    'quat': lambda x, _: glm.quat(*x['values']),
    'entity': handle_entity,
    'entity_ref': handle_entity_ref,
    'script': handle_script,
    'script_cls': handle_cls,
    'entity_cls': handle_cls,
}


def load_level(location, game):
    with open(location, 'r') as f:
        save_obj = json.load(f)

    # load models and scripts (ie everything that's not entities)
    game.scripts = {cls: name for cls, name in handle_item(save_obj['scripts'], game)}
    game.entity_classes = {cls: name for cls, name in handle_item(save_obj['entity_classes'], game)}

    # load entities
    entity_dict = save_obj['entities']
    # since the dict is full of (hopefully) entities, we call handle_item to call the relevant handler
    for entity in entity_dict.values():
        handle_item(entity, game)

    from enginelib.level.save import assets
    for asset in assets:
        # assert not (hasattr(game, asset) and getattr(game, asset)), \
        #     f"asset {asset} attempted to overwrite existing attribute in game -- save file is incompatible"
        if asset not in save_obj:
            print(f"warning: expected asset {asset} in save file")
            continue
        setattr(game, asset, handle_item(save_obj[asset], game))
