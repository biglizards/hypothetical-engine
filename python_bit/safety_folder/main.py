from editor import Editor, Drag
from game import Game


class CustomEditor(Editor, Drag):
    pass


class CustomGame(Game):
    pass


game = CustomEditor(width=1200, height=800)

game.run(True)
