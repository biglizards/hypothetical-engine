from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

# get distutils to work properly >:|
from distutils.command.build_ext import build_ext
from distutils.sysconfig import customize_compiler
import os
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


ext_modules = [Extension(name="engine.engine",
                         language='c++',
                         sources=['engine/engine.pyx', '../opengl_stuff/glad/src/glad.c', '../engine/engine.cpp'],
                         include_dirs=['../opengl_stuff/glad/include',
                                       '../opengl_stuff/glfw/include', '.'],
                         library_dirs=['../opengl_stuff/glfw/src/'],
                         libraries=['glfw3',
                                    'GL',
                                    'X11', 'Xrandr', 'Xi', 'Xxf86vm', 'Xcursor', 'Xinerama',
                                    ],
                         extra_compile_args=["-std=c++11"],
                         extra_link_args=["-std=c++11"]
                         )]

setup(
    name='engine',
    packages=['engine'],
    cmdclass={'build_ext': my_build_ext},
    ext_modules=cythonize(
        ext_modules,
        build_dir="build",
        include_path=['engine'],
        compiler_directives={'embedsignature': True, 'language_level': 3}
      ),
)