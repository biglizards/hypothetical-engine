from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


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

# i'm trying out a new thing where i don't RUIN EVERYTHING
exit(0)
# much better

# horrible debug thing
from shutil import copyfile
import sys

with open('engine/__init__.py', 'w') as f:
    # by now, __init__.py is blank, so we can import it freely
    sys.path.append('build/lib.win32-3.6/engine')
    import engine.engine

    exports = ', '.join(name for name in dir(engine.engine) if not name.startswith('__'))

    f.write('from .engine import {}\n'.format(exports))
    f.write('from .engine import *\n')

copyfile('engine/__init__.py',
         'D:/Users/***REMOVED***/AppData/Local/Programs/Python/Python36-32/Lib/site-packages/engine/__init__.py')
