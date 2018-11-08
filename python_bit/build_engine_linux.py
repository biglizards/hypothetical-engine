import os
from distutils.sysconfig import customize_compiler

from Cython.Build import cythonize
from setuptools import setup
# get distutils to work properly >:|
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension

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


with open('engine/config.pxi', 'w') as f:
    f.write('DEF DEBUG = 0\n'
            'DEF FALSE = 0\n'
            'DEF WINDOWS = 0\n'
            'DEF LINUX = 1\n')


ext_modules = [Extension(name="engine.engine",
                         language='c++',
                         sources=['engine/engine.pyx', #'../opengl_stuff/glad/src/glad.c',
                                  '../engine/engine.cpp'],
                         include_dirs=[#'../opengl_stuff/glad/include',
                                       #'../opengl_stuff/build2/',
                                       '.', '../ext/include', '../ext/include/nanovg/src'],
                         library_dirs=[#'../opengl_stuff/glfw/src/',
                                       '../ext/lib'],
                         libraries=['glfw3', 'nanogui',
                                    'GL',
                                    'X11', 'Xrandr', 'Xi', 'Xxf86vm', 'Xcursor', 'Xinerama',
                                    ],
                         extra_compile_args=["-std=c++11", '-fPIC', '-Wno-int-in-bool-context'],
                         extra_link_args=["-std=c++11", '-fPIC']
                         )]

setup(
    name='engine',
    packages=['engine'],
    cmdclass={'build_ext': my_build_ext},
    install_requires=['pyglm'],
    ext_modules=cythonize(
        ext_modules,
        build_dir="build",
        include_path=['engine'],
        compiler_directives={'embedsignature': True, 'language_level': 3},
        annotate=True,
        quiet=True,
      ),
    zip_safe=False,
)
