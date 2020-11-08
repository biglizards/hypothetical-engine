from enginelib.editor import Editor

game = Editor(width=1200, height=800, everything_is_reloadable=True,
              save_name='save.json', classes='classes', scripts='scripts')
game.set_vsync(True)

game.run(print_fps=False)
