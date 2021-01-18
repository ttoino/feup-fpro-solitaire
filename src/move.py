from abc import ABC, abstractmethod
from typing import Generator
from animation import Animation, ConcurrentAnimations, FlipAnimation, SequentialAnimations

from stack import Stack


class Move(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def undo(self) -> Animation:
        pass

    @abstractmethod
    def redo(self) -> Animation:
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
        self.from_stack.cards.extend(cards)
        return ConcurrentAnimations((self.from_stack.animate(), self.to_stack.animate()))

    def redo(self):
        cards = [self.from_stack.cards.pop() for _ in range(self.amount)]
        if not self.reverse:
            cards = reversed(cards)
        self.to_stack.cards.extend(cards)
        return ConcurrentAnimations((self.from_stack.animate(), self.to_stack.animate()))


class FlipMove(Move):
    def __init__(self, card):
        super().__init__()
        self.card = card

    def undo(self):
        self.card.flip()
        return FlipAnimation(self.card)

    def redo(self):
        self.card.flip()
        return FlipAnimation(self.card)


class ConcurrentMoves(Move):
    def __init__(self, moves):
        super().__init__()
        self.moves = moves

    def undo(self):
        return ConcurrentAnimations([move.undo() for move in self.moves])

    def redo(self):
        return ConcurrentAnimations([move.redo() for move in self.moves])


class SequentialMoves(Move):
    def __init__(self, moves):
        super().__init__()
        self.moves = moves

    def undo(self):
        return SequentialAnimations(move.undo() for move in reversed(self.moves))

    def redo(self):
        return SequentialAnimations(move.redo() for move in self.moves)
