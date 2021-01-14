import assets
from enum import Enum


class Suit(Enum):
    SPADES = "spades"
    CLUBS = "clubs"
    HEARTS = "hearts"
    DIAMONDS = "diamonds"

    @property
    def is_red(self):
        return self in {Suit.HEARTS, Suit.DIAMONDS}

    @property
    def is_black(self):
        return not self.is_red


class Symbol(Enum):
    ACE = "a"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "j"
    QUEEN = "q"
    KING = "k"

    @property
    def _list(self):
        return [s for s in Symbol]

    def is_next(self, other):
        l = self._list
        return l.index(self) == l.index(other)+1

    def is_previous(self, other):
        l = self._list
        return l.index(self)+1 == l.index(other)


class Card():
    def __init__(self, app, suit: Suit, symbol: Symbol):
        super().__init__()
        self.app = app
        self.suit = suit
        self.symbol = symbol
        self.flipped = True
        self.pos = (0, 0)

    @property
    def asset(self):
        return assets.card_surfaces[(self.suit, self.symbol)]

    @property
    def back_asset(self):
        return assets.back_surface

    def draw(self, screen):
        surface = self.back_asset if self.flipped else self.asset
        screen.blit(surface, self.app.game_to_screen(self.pos))

    def flip(self):
        self.flipped = not self.flipped
