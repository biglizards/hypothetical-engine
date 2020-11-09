The code is split into 3 main sections:

enginecore, which is compiled and contains C and Cython code. It's mostly a collection of wrappers around libraries like
GLFW, NanoGUI, GLAD, and Assimp. If the engine were to be optimised, this is where the fast code would go.

enginelib is a pure python library that extends enginecore into a more user friendly interface, and adds most of the
interesting features, like
- a camera (technically, 4 cameras)
- saving and loading (including hot reloading)
- the entire editor
- entities
- scripts and the dispatch system

The example shows how a project could be structured, and contains a variety of example classes showing the flexibility
of the engine (such as the speaker and axis classes, and the scripts).

A quick rundown of the logical structure of this project:
 - `Model` contains a `Shader` and a collection of `Mesh`es and can be rendered with `Model.draw()`
 - `Entitiy`s are `Models` but with more features, and represent all objects in a scene.
 - The `Game` holds the `Entitiy`s and the main loop, and dispatches events.
   - The `Game` has a `Camera` which handles perspective, movement, etc.
 - The `Editor` is a `Game` but with a GUI for editing the attributes of `Entitiy`s
 - Any method can be registered as a callback for events like `on_frame`, `on_key_press`, `every_n_ms`, etc.
 - `Script` instances are attached to `Entity` instances, where they use hooks to affect the entities in some way 
 (eg giving it physics)
 - The `enginelib.level.save` and `enginelib.level.load` serialise and deserialise levels, which contain:
   - entities
   - models
   - textures
   - audio
   - shaders
 - The `Loader` object keeps track of all loaded classes (both entity classes and scripts), and can hot reload them
   from disk (updating all instances of them with the new code).
 - Every frame, the scene is rendered, and then the `on_frame` event is dispatched, allowing for periodically updating.
   Then, events are polled and the relevant events are dispatched (`on_key_press`, `on_cursor_move`, etc). 