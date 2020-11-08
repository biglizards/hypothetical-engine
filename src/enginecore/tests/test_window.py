import pytest
import engine
import inspect

from engine import TestWindow


@pytest.fixture
def window():
    return engine.Window()


# pytest won't run `cyfunction`s even though they are runnable
# so wrap them in regular functions instead, via this great hack that has no flaws whatsoever
# (aside from potential aliasing issues)

classes_to_test = [TestWindow]
cy_function = type(TestWindow.test_window_key_callback)

for i, cls in enumerate(classes_to_test):
    for name, method in inspect.getmembers(cls, predicate=lambda x: isinstance(x, cy_function)):
        if name.startswith("test"):
            arguments = str(inspect.signature(method))  # returns something like "(a, b, c=None, *args, d=2)"
            exec(
                f"""
def {name}{arguments}:
    classes_to_test[{i}].{name}{arguments}
"""
            )
            globals()[name] = locals()[name]
