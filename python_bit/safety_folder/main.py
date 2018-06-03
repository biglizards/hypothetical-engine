import engine
import time


class MyWindow(engine.Window):
    def swap_buffers(self):
        super(MyWindow, self).swap_buffers()


window = engine.Window(height=600, width=450, name='not that')

start_time = time.time()
i = 0

while not window.should_close():
    window.clear_colour(0.3, 0.5, 0.8, 1)
    window.swap_buffers()
    window.clear_colour(0.3, 0.5, 0.8, 1)
    engine.poll_events()

    i += 1
    if i == 256:
        duration = time.time() - start_time
        print(duration, 256/duration, "fps")
        start_time = time.time()
        i = 0
