from collections import deque

from move import Move


class History():
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.past: deque[Move] = deque()
        self.future: deque[Move] = deque()

    def undo(self):
        if len(self.past) == 0:
            return

        move = self.past.pop()
        self.game.animations.add(move.undo())
        self.future.append(move)

    def redo(self):
        if len(self.future) == 0:
            return

        move = self.future.pop()
        self.game.animations.add(move.redo())
        self.past.append(move)

    def add_move(self, move):
        self.past.append(move)
        self.future.clear()
        self.game.animations.add(move.redo())
