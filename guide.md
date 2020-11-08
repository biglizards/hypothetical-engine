Like everything else this guide is a work in progress -- 
I'll do my best to keep it up to date and detailed enough, but no promises

## Error handling
In an ideal world, my code has no bugs in, so the only exceptions come from user code.
If you want to handle an error, change the `Game.on_error` function. By default it just re-raises the error.
```python
def my_error_handler(e):
    # log but don't crash
    print("oh no an error:", e)    

game = Game(...)
game.on_error = my_error_handler
```

## Hot Reloading

Hot reloading allows you to change your code without closing and re-opening the game.
You can trigger a reload by calling `load.loader.reload()` (or pressing the button in the editor).

To enable hot reloading, there are 3 options of increasing overhead and convinience:

##### 1. Decorate the function with `@reload.reloadable`
```python
import enginelib.level.reload as reload

@reload.reloadable
def my_function():
    pass
```
This adds a layer of indirection wherever the function is called, adding a tiny bit of overhead.

##### 2. Decorate the class with `@reload.reloadable_class`
```python
import enginelib.level.reload as reload

@reload.reloadable_class
class MyClass:
    def my_function(self):
        pass
```
This decorates every method in the class (unless it starts with `__` like `__init__`) with `reload.reloadable`.

##### 3. Pass `everything_is_reloadable=True` to `Game` or `Editor`
This decorates every class with `@reload.reloadable_class`.

#### Caveats
When you reload a class, it doesn't automatically update existing instances of that class. However, creating new 
instances of everything would defeat the point. If all we stored were instances, we could just update the old class to
use the new functions, but we also store references to bound methods. To solve this (in the general case), we replace
every method on every class with a layer of indirection that checks what the latest method is, then calls that.

As you would expect, this adds some overhead to every function call, which isn't great. Turns out it's not actually a 
huge amount compared to the cost of running large amounts of Python code generally, so there's that.

Also it's probably full of bugs and workarounds, and I'll try to document them all here:
 - You can't use `super()` after reloading, but directly referring to the parent class (if you're only doing single 
   inheritance) works fine.
   - Or if you really want to use a function called super, you can use `Script.super()`. I wouldn't recommend it, but
     you've got the option.
 - If for some godforsaken reason you use attributes of type `wrapper_descriptor`, they won't be reloaded. That's not 
   even a type you can refer to directly, so it'd probably only come up if you're writing C extensions.
 - If you manage to have an attribute that doesn't start with `__`, isn't in `__dict__`, and doesn't belong to a parent 
 class, then you are clearly hacking and the reloading module reserves the right to trigger undefined behaviour.
    - As of writing I'm pretty sure it won't, but there's always the risk it'll use that opportunity to become sentient
      and take over the world. Not worth the risk IMO.
 - If you use anything with descriptors (eg properties), it probably won't work. Maybe it will, and if it does, good.
   If it doesn't, feel free to submit a bug report because that technically is a bug. If I solve enough specific cases
   it'll become the general case in the limit.
 - Cython functions cannot be reloaded (although if you're happy to recompile I imagine 
   you're probably happy to restart the program)