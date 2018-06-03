from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


ext_modules = [Extension(name="engine.engine",
                         sources=['engine/engine.pyx', '../opengl_stuff/GLAD/src/glad.c', '../engine/engine.cpp'],
                         include_dirs=['C:/Users/pc/Documents/Code/opengl_stuff/GLAD/include',
                                       'C:/Users/pc/Documents/Code/opengl_stuff/glfw/include'],
                         library_dirs=['C:/Users/pc/Documents/Code/opengl_stuff/glfw/lib-vc2015/'],
                         libraries=['glfw3',
                                    'opengl32',
                                    'gdi32',
                                    'user32',
                                    'shell32'],
                         )]

setup(
    name='engine',
    packages=['engine'],
    ext_modules=cythonize(
        ext_modules,
        build_dir="build",
        compiler_directives={'embedsignature': True, 'language_level': 3}
      ),
)

# horrible debug thing
from shutil import copyfile

copyfile('build/lib.win32-3.6/engine/engine.cp36-win32.pyd', 'engine/engine.cp36-win32.pyd')
with open('engine/__init__.py', 'w') as f:
    # by now, __init__.py is blank, so we can import it freely
    import engine.engine
    exports = ', '.join(name for name in dir(engine.engine) if not name.startswith('__'))

    f.write('from .engine import {}\n'.format(exports))
    f.write('from .engine import *\n')

copyfile('engine/__init__.py',
         'D:/Users/***REMOVED***/AppData/Local/Programs/Python/Python36-32/Lib/site-packages/engine/__init__.py')
