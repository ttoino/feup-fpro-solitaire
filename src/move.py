from abc import ABC, abstractmethod

from stack import Stack


class Move(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def redo(self):
        pass


class MoveMove(Move):
    def __init__(self, from_stack: Stack, to_stack: Stack, amount, reverse=False):
        super().__init__()
        self.from_stack = from_stack
        self.to_stack = to_stack
        self.amount = amount
        self.reverse = reverse

    def undo(self):
        cards = [self.to_stack.cards.pop() for _ in range(self.amount)]
        if not self.reverse:
            cards = reversed(cards)
        self.from_stack.add_all(cards)
        self.from_stack.update()
        self.to_stack.update()

    def redo(self):
        cards = [self.from_stack.cards.pop() for _ in range(self.amount)]
        if not self.reverse:
            cards = reversed(cards)
        self.to_stack.add_all(cards)
        self.from_stack.update()
        self.to_stack.update()


class FlipMove(Move):
    def __init__(self, card):
        super().__init__()
        self.card = card

    def undo(self):
        self.card.flip()

    def redo(self):
        self.card.flip()


class ConcurrentMoves(Move):
    def __init__(self, moves):
        super().__init__()
        self.moves = moves

    def undo(self):
        for move in self.moves:
            move.undo()

    def redo(self):
        for move in self.moves:
            move.redo()


# TODO
class SequentialMoves(Move):
    def __init__(self, moves):
        super().__init__()
        self.moves = moves

    def undo(self):
        for move in self.moves:
            move.undo()

    def redo(self):
        for move in self.moves:
            move.redo()
