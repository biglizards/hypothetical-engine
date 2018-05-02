from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'cool_maths',
    ext_modules = cythonize('cy_stuff/*.pyx')
)