NOTE: the actual test code is in cython_code/tests, because it needs to access internals

to get coverage for these tests, you need to be in cython_code (the actual tests run fine either way)
you'd want to run something like
[cython_code]$ py.test ../tests/ --cov .

In pycharm, you may need to disable the bundled coverage, as CTracer must be used.

note: there aren't very many tests, since most code in the core is just a wrapper around other libraries