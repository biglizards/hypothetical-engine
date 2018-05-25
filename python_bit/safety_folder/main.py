import engine
import time


class MyWindow(engine.Window):
    def swap_buffers(self):
        super(MyWindow, self).swap_buffers()
        print("swapping buffers")


window = MyWindow(height=600, width=450, name='not that')

start_time = time.time()
i = 0

while not window.should_close():
    window.swap_buffers()
    engine.poll_events()

    i += 1
    if i == 16384:
        duration = time.time() - start_time
        print(duration, 16384/duration, "fps")
        start_time = time.time()
        i = 0
