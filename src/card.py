from enum import Enum

import pygame

import assets


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
        self.surface: pygame.Surface = self.back_asset

    @property
    def asset(self) -> pygame.Surface:
        return assets.card_surfaces[(self.suit, self.symbol)]

    @property
    def back_asset(self) -> pygame.Surface:
        return assets.back_surface

    def draw(self, screen):
        if self.surface.get_height() != self.back_asset.get_height():
            self.surface = self.back_asset if self.flipped else self.asset

        pos = self.app.game_to_screen(self.pos)
        pos = pos[0] + (self.back_asset.get_width() - self.surface.get_width())*.5, pos[1]
        screen.blit(self.surface, pos)

    def flip(self):
        self.flipped = not self.flipped
