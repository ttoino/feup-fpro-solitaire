from collections import deque
from random import shuffle

from card import Card, Suit, Symbol
from stack import DragStack, FoundationStack, StockStack, TableauStack, WasteStack


class Game():
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.deck = self.create_deck()
        shuffle(self.deck)
        self.setup_stacks()
        self.deal()

    def create_deck(self):
        return deque(Card(self.app, suit, symbol) for symbol in Symbol for suit in Suit)

    def setup_stacks(self):
        self.foundations = tuple(FoundationStack(self.app, (i*60 + 20, 20)) for i in range(4))
        self.stock = StockStack(self.app, (380, 20))
        self.waste = WasteStack(self.app, (260, 20))
        self.tableaus = tuple(TableauStack(self.app, (i*60 + 20, 100)) for i in range(7))
        self.drag = DragStack(self.app, (0, 0))
        self.stacks = self.foundations + self.tableaus + (self.stock, self.waste, self.drag)

    def deal(self):
        self.stock.cards = self.deck
        self.stock.update()
        for i, stack in enumerate(self.tableaus):
            stack.add_all([self.deck.pop() for _ in range(i+1)])
            stack.update()

    def draw(self, screen):
        for stack in self.stacks:
            stack.draw(screen)
