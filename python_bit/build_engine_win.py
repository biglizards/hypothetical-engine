from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

print("starting compile...")

debug = 0
# in future, have this be set from command line or whatever

#with open('engine/config.pxi', 'w') as f:
#    f.write('DEF DEBUG = {}'.format(debug))


ext_modules = [Extension(name="engine.*",
                         language='c++',
                         sources=['engine/*.pyx',
                                  '../engine/engine.cpp'],
                         include_dirs=['../ext/include',
                                       '../ext/include/nanovg/src'  # grr
                                       '.'],
                         library_dirs=['../ext/lib'],
                         libraries=['opengl32', 'nanogui', 'glfw3',
                                    # the rest are windows libs that need to be included
                                    'gdi32',
                                    'user32',
                                    'shell32',
                                    'Comdlg32'],
                         ),
               ]

setup(
    name='engine',
    packages=['engine'],
    ext_modules=cythonize(
        ext_modules,
        build_dir="build",
        compiler_directives={'embedsignature': True, 'language_level': 3},
        annotate=True,
        quiet=True,
        force=True,
    ),
)

print("done")
