import glob
import os
import platform
import shutil
from distutils.sysconfig import customize_compiler

from Cython.Build import cythonize
from setuptools import setup
# get distutils to work properly >:|
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension

linux = platform.system() == 'Linux'
windows = platform.system() == 'Windows'
if not linux or windows:
    raise OSError('Could not detect system as linux or windows, and only these platforms are supported!')

if linux:
    # force system to use g++, even for c code
    os.environ["CC"] = "g++"
    os.environ["CXX"] = "g++"

    class my_build_ext(build_ext):
        def build_extensions(self):
            customize_compiler(self.compiler)
            try:
                self.compiler.compiler_so.remove("-Wstrict-prototypes")
            except (AttributeError, ValueError):
                pass
            build_ext.build_extensions(self)


with open('config.pxi', 'w') as f:
    f.write(f'DEF DEBUG = 0\n'
            f'DEF FALSE = 0\n'
            f'DEF WINDOWS = {windows}\n'
            f'DEF LINUX = {linux}\n')


ext_modules = [Extension(name="engine",
                         language='c++',
                         sources=['engine.pyx', '../c/engine.cpp'],
                         include_dirs=['.', '../ext/include', '../ext/include/nanovg/src'],
                         library_dirs=['../ext/lib'],
                         libraries=['glfw3', 'nanogui', 'assimp',
                                    'GL',
                                    'X11', 'Xrandr', 'Xi', 'Xxf86vm', 'Xcursor', 'Xinerama',
                                    ] if linux else [
                                    'opengl32', 'nanogui', 'glfw3', 'gdi32', 'user32', 'shell32',
                                    'Comdlg32', 'Dbghelp'
                                    ],
                         extra_compile_args=["-std=c++11", '-fPIC', '-Wno-int-in-bool-context', '-O0'] if linux else ['-Zi'],
                         extra_link_args=["-std=c++11", '-fPIC', '-O0'] if linux else ['/DEBUG']
                         ),
               ]

setup(
    name='engine',
    #packages=['.'],
    cmdclass={'build_ext': my_build_ext} if linux else {},
    install_requires=['pyglm'],
    ext_modules=cythonize(
        ext_modules,
        #build_dir="build",
        #include_path=['engine'],
        compiler_directives={'embedsignature': True, 'binding': True, 'language_level': 3, 'linetrace': False},
        annotate=False,
        quiet=False,
        force=False,
      ),
    zip_safe=False,
)

# print('copying file to ../../enginelib')
# files = glob.glob('engine.cpython*')
# if len(files) > 1:
#     raise RuntimeError(f'Too many compiled files detected, please delete the extra ones:\n{files}')
# elif len(files) == 0:
#     raise RuntimeError('No compiled file detected! Please open an issue about this.')
#
# shutil.copy(files[0], f'../tests/{files[0]}')
# shutil.move(files[0], f'../../enginelib/{files[0]}')
