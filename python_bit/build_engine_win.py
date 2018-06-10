from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

debug = 0
# in future, have this be set from command line or whatever
with open('engine/config.pxi', 'w') as f:
    f.write('DEF DEBUG = {}'.format(debug))

ext_modules = [Extension(name="engine.*",
                         language='c++',
                         sources=['engine/*.pyx', '../opengl_stuff/GLAD/src/glad.c', '../engine/engine.cpp'],
                         include_dirs=['C:/Users/pc/Documents/Code/opengl_stuff/GLAD/include',
                                       'C:/Users/pc/Documents/Code/opengl_stuff/glfw/include', '.'],
                         library_dirs=['C:/Users/pc/Documents/Code/opengl_stuff/glfw/lib-vc2015/'],
                         libraries=['glfw3',
                                    'opengl32',
                                    'gdi32',
                                    'user32',
                                    'shell32'],
                         ),
               ]

setup(
    name='engine',
    packages=['engine'],
    ext_modules=cythonize(
        ext_modules,
        build_dir="build",
        compiler_directives={'embedsignature': True, 'language_level': 3},
        annotate=True
      ),
)
