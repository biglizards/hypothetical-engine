So, saving is a bit of an odd one. By default, when in editor mode the arguments you pass to engine.create_entity
will be stored, and written to disk when you save. This, however, does not work for attributes that change after
being loaded (which are, after all, the main reason to use an editor), so when saving the engine looks for
`entity.savable_attributes`, An example is shown below:

```python
class MyEntity(Entity):
    def __init__(self, game, arg1, arg2, arg3=None):
        super().__init__(...)
        self.arg1 = arg1
        self.arg2_but_with_a_different_name = arg2
        self.thing_obtained_from_arg3 = SomeOtherClass(arg3)

        # mapping of arg_name -> property_name
        self.savable_attributes = {'arg1': 'arg1', 'arg2': 'arg2_but_with_a_different_name'}
```

Note that since `SomeOtherClass(arg3)` is not of the same type as `arg3`, we (probably) can't save
`thing_obtained_from_arg3` and pass it as an argument to `SomeOtherClass`. Instead, if the value of
your property can change while being edited, you have 2 options

option 1:
```python
class MyEntity(Entity):
    def __init__(self, game, arg1, arg2, arg3=None):
        super().__init__(...)
        self.thing_obtained_from_arg3 = SomeOtherClass(arg3)

        self.save_overrides = {}
        game.add_callback('on_save', self.on_save)

    def on_save(self):
        self.save_overrides = {'arg3': extract_arg3_from_thing(self.thing_obtained_from_arg3)}
```

option 2:
```python
import enginelib.save as save  # or whatever it is, the module name will probably change
save.handlers[SomeOtherClass] = extract_arg3_from_thing
MyEntity.savable_attributes['arg3'] = 'thing_obtained_from_arg3'
```
