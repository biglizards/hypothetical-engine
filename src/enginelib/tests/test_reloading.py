from hypothesis import given
from hypothesis.strategies import integers

from enginelib.level.reload import Loader, reloadable_class

import sys
import os

# sometimes the path doesnt contain the current directory, so importing the locally created files breaks
sys.path.append(os.getcwd())

TEXT = '''import enginelib.level.reload as reload

{2}
class Foo:
    class_attr = {1}
    def __init__(self, i):
        self.i = i

    @reload.reloadable
    def bar(self):
        return self.i + {0}
    
    def non_reloadable(self):
        return {3}    
'''

EXTRA_FUNCTION = '''
    @reload.reloadable
    def baz(self):
        return {}
'''

SUBCLASS = '''
import foo
@reload.reloadable_class
class Bar(foo.Foo):
    def bar(self):
        return 2*self.i + {}
'''


def create_foo(i=1, attr=1, deco='', non=1, text=TEXT, extra_text='', filename='foo.py'):
    with open(filename, 'w') as f:
        f.write(text.format(i, attr, deco, non) + extra_text)


def setup(*blanks, **kwblanks):
    def deco(f):
        def inner(*args, **kwargs):
            create_foo(*blanks, **kwblanks)
            loader = Loader()
            Foo = loader.load_class('foo', 'Foo')
            return f(Foo, loader, *args, **kwargs)
        return inner
    return deco


@setup()
def test_loader_loads_thing(foo_class, _loader):
    assert hasattr(foo_class, 'bar')


@setup(1)
@given(integers())
def test_loader_foo_bar_is_1_plus_i(foo_class, _loader, i):
    assert foo_class(i).bar() == 1+i


@setup()
@given(integers(), integers())
def test_loader_reloads_foo(foo_class, loader, i, j):
    foo = foo_class(i)
    create_foo(j)
    loader.reload()
    assert foo.bar() == j+i


@setup(1)
@given(integers(), integers())
def test_reloadable_affects_function_references(foo_class, loader, i, j):
    foo = foo_class(i)
    bar = foo.bar
    create_foo(j)
    loader.reload()
    assert bar() == foo.bar() == i+j


@setup()
@given(integers())
def test_reload_affects_class_attributes(foo_class, loader, i):
    create_foo(attr=i)
    loader.reload()
    assert foo_class.class_attr == i


@given(integers())
def test_reload_adds_new_functions(i):
    # manually create fresh foo
    create_foo()
    loader = Loader()
    foo_class = loader.load_class('foo', 'Foo')
    foo = foo_class(1)
    assert not hasattr(foo, 'baz')
    create_foo(extra_text=EXTRA_FUNCTION.format(i))
    loader.reload()
    assert foo.baz() == i


def test_funky_setup():
    """
    issue here:
    - load and cache class (A)
    - reload, getting different class (B)
    - the second load_entity_class returns (B), even though (A) is in cache
    - reload only affects (A) and ignores (B)

    solution: just keep a set of all classes instead of a dict
    """
    for _ in range(3):
        create_foo()
        loader = Loader()
        loader.load_class('foo', 'Foo')
        loader.reload()
        foo_class = loader.load_class('foo', 'Foo')
        foo = foo_class(1)
        assert not hasattr(foo, 'baz')
        create_foo(extra_text=EXTRA_FUNCTION.format(0))
        loader.reload()
        assert hasattr(foo, 'baz')


@setup(deco='@reload.reloadable_class', non=1)
def test_reloadable_class_works(foo_class, loader):
    foo = foo_class(1)
    assert foo.non_reloadable() == 1
    create_foo(non=2)
    loader.reload()
    assert foo.non_reloadable() == 2


@setup()
def test_loader_can_load_multiple_classes(_foo_class, loader: Loader):
    create_foo(attr=3)
    create_foo(attr=5, filename='bar.py')
    loader.reload()
    foo_class = loader.load_class('foo', 'Foo')
    bar_class = loader.load_class('bar', 'Foo')
    assert foo_class.class_attr == 3
    assert bar_class.class_attr == 5


@setup(i=1)
def test_make_class_reloadable_after_instantiation(foo_class, loader: Loader):
    foo = foo_class(1)
    reloadable_class(foo_class)
    bar = foo.bar
    create_foo(i=2)
    loader.reload()
    assert bar() == 3


def test_reloadable_subclasses():
    loader = Loader()
    create_foo(extra_text=SUBCLASS.format(5), filename='bar.py')
    create_foo(non=3, filename='foo.py')
    bar = loader.load_class('bar', 'Bar')(1)
    non = bar.non_reloadable
    assert non() == 3
    create_foo(non=5)
    loader.reload()
    assert non() == 5


def test_reloadable_subclasses2():
    loader = Loader()
    create_foo(extra_text=SUBCLASS.format("super().f"), filename='bar.py')
    create_foo(non=3, filename='foo.py')
    bar = loader.load_class('bar', 'Bar')(1)
    non = bar.non_reloadable
    assert non() == 3
    create_foo(non=5)
    loader.reload()
    assert non() == 5


def test_super_works():
    loader = Loader()
    B = loader.load_class('baz', 'C')
    b = B()
    loader.reload()
    B = loader.get_newer_class(B)
    b2 = B()


def test_dumb_super_works_with_old_class():
    loader = Loader()
    B = loader.load_class('baz', 'B2')
    b = B(loader)
    loader.reload()
    b2 = B(loader)

if __name__ == '__main__':
    test_dumb_super_works_with_old_class()