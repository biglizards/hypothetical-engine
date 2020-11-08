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
    # packages=['enginelib', 'enginelib.level'],
    # package_dir={'enginelib': '../../enginelib'},
    cmdclass={'build_ext': my_build_ext} if linux else {},
    install_requires=['pyglm', 'pyopenal'],
    zip_safe=False,
    ext_modules=cythonize(
        ext_modules,
        #build_dir="build",
        #include_path=['engine'],
        # for reasons i'm not entirely sure about, having linetrace on breaks the debugger
        compiler_directives={'embedsignature': True, 'binding': True, 'language_level': 3, 'linetrace': False},
        annotate=False,
        quiet=False,
        force=True,
      ),
    script_args=['install'],
    # options={'build': {'build_lib': '../..'}},
)
