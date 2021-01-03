from collections import deque
from random import choice, shuffle

from card import Card, Suit, Symbol


class Game():
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.deck = self.create_deck()
        shuffle(self.deck)

    def create_deck(self):
        return deque(Card(suit, symbol) for symbol in Symbol for suit in Suit)

    def draw(self, screen):
        choice(self.deck).flip()

        for i, card in enumerate(self.deck):
            card.draw(screen, self.parent.game_to_screen(
                ((i % 7)*60 + 20, (i // 7)*80 + 20)))
