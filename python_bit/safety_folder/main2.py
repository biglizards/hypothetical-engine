import engine
import time
from timeit import timeit


def timeit(f):
    start = time.time()
    n = 10
    while True:
        f(n)
        if time.time()-start > 0.1:
            break
        n *= 10
    print('{0}: {1} loops took {2:.3g} s'
          .format(f.__name__, n, time.time()-start))


t = engine.A()
[timeit(getattr(t, test)) for test in dir(t) if test.startswith('test')]


class B(engine.A):
    pass


t =B()
[timeit(getattr(t, test)) for test in dir(t) if test.startswith('test')]
