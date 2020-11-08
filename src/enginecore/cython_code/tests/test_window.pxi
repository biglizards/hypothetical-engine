from hypothesis import given
from hypothesis.strategies import floats, lists
from pytest import approx
import engine

IF FALSE:
    # this is a hack to get code inspection working
    include "../window.pxi"

# callback tests
class TestWindow:
    @given(lists(floats(0, 1), 4, 4))
    def test_window_clear_color(self, window, colors):
        """Given a colour (represented by a list of floats), set the window to that colour.
        note: this doesnt actually get the value on the screen, but the one in the buffer.
        Assuming OpenGL works, there should be no difference"""
        window.clear_colour(*colors)
        assert window.read_pixel(0, 0) == approx([x*255 for x in colors], abs=1)

    @staticmethod
    def test_window_closes(window):
        assert not window.should_close()
        window.close()
        assert window.should_close()

    @staticmethod
    def test_getters_and_setters_work(window):
        # this test sometimes fails because the window doesn't update fast enough
        # so the width gets overwritten by the old width since in glfw you can't update them individually
        # the fix is to use glfwGetVideoMode instead of glfwGetWindowSize
        window.width, window.height = 111, 222
        assert window.width == 111
        assert window.height == 222

        assert window.get_window_size() == (111, 222)


    @staticmethod
    def test_window_key_callback(window):
        """Test that key callbacks can be set, and are triggered correctly on key press"""
        callback_count = 0

        def __test__key_callback(window_, key_code, _scancode, action, _mods):
            nonlocal callback_count
            assert window_ is window
            assert key_code == engine.KEY_A
            if callback_count == 0:  # the first action is a key press
                assert action == engine.KEY_PRESS
            else:  # the second action is a key release
                assert action == engine.KEY_RELEASE
            callback_count += 1

        window.key_callback = __test__key_callback

        cdef Window c_window = window;

        # test the callback is called the correct number of times
        key_callback(c_window.window, engine.KEY_A, 0, engine.KEY_PRESS, 0)
        engine.poll_events()
        assert callback_count == 1

        key_callback(c_window.window, engine.KEY_A, 0, engine.KEY_RELEASE, 0)
        engine.poll_events()
        assert callback_count == 2

    @staticmethod
    def test_error_propagation_works(window):
        cdef Window c_window = window;
        def callback(*_args):
            return 1/0
        window.key_callback = callback
        key_callback(c_window.window, engine.KEY_A, 0, engine.KEY_PRESS, 0)  # press a
        try:
            engine.poll_events()
            assert False, "an exception should have been raised"
        except ZeroDivisionError:
            pass