import assets
from enum import Enum


class Suit(Enum):
    SPADES = "spades"
    CLUBS = "clubs"
    HEARTS = "hearts"
    DIAMONDS = "diamonds"


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


class Card():
    def __init__(self, suit: Suit, symbol: Symbol):
        super().__init__()
        self.suit = suit
        self.symbol = symbol
        self.flipped = True

    @property
    def asset(self):
        return assets.card_surfaces[(self.suit, self.symbol)]

    @property
    def back_asset(self):
        return assets.back_surface

    def draw(self, screen, pos):
        surface = self.back_asset if self.flipped else self.asset
        screen.blit(surface, pos)

    def flip(self):
        self.flipped = not self.flipped
