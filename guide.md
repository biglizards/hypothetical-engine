Like everything else this guide is a work in progress -- 
I'll do my best to keep it up to date and detailed enough, but no promises

(this is where i'd put my contents page... if i had one)

### Error handling
In an ideal world, my code has no bugs in, so the only exceptions come from user code.
If you want to handle an error, change the `Game.on_error` function. By default it just re-raises the error.
```python
def my_error_handler(e):
    # log but don't crash
    print("oh no an error:", e)    

game = Game(...)
game.on_error = my_error_handler
```