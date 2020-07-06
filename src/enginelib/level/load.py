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


# oh no, globals. But dont worry, they're only used in load_entity_class, and also at the end of load_level.
# i could pass these through the call stack, or make this into a class, but this way is neater imo.
is_reloading = False
reloaded_modules = set()


def load_entity_class(module_name, class_name):
    module = importlib.import_module(module_name)
    if module not in reloaded_modules:
        module = importlib.reload(module)
        reloaded_modules.add(module)
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
    # glm.quat does not accept lists as arguments in the latest version
    'quat': lambda x, _: glm.quat(*x['values']),
    # 'quat': lambda x, _: glm.quat(x['values'][-1], *x['values'][:-1]),
    'entity': handle_entity,
    'entity_ref': handle_entity_ref,
    'script': handle_script,
    'script_cls': lambda data, _: (load_entity_class(module_name=data['@class_module'],
                                                     class_name=data['@class_name']), data['@name']),
    'entity_cls': lambda data, _: (load_entity_class(module_name=data['@class_module'],  # todo remove duplication
                                                     class_name=data['@class_name']), data['@name']),

}


def load_level(location, game):
    with open(location, 'r') as f:
        save_obj = json.load(f)

    # load models and scripts (ie everything that's not entities)
    game.models = handle_item(save_obj['models'], game)
    game.scripts = {cls: name for cls, name in handle_item(save_obj['scripts'], game)}
    game.entity_classes = {cls: name for cls, name in handle_item(save_obj['entity_classes'], game)}

    # load entities
    entity_dict = save_obj['entities']
    # since the dict is full of (hopefully) entities, we call handle_item to call the relevant handler
    for entity in entity_dict.values():
        handle_item(entity, game)

    global is_reloading, reloaded_modules
    is_reloading = True
    reloaded_modules.clear()
