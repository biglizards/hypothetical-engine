import engine
import time

st = time.time()

for _ in range(2**22):
    engine.foo.inc()

print(time.time() - st)
