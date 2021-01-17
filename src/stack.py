from abc import ABC, abstractmethod
from collections import deque

import pygame
from animation import ConcurrentAnimations, MoveAnimation

from card import Card, Symbol
import assets
import constants


class Stack(ABC):
    def __init__(self, app, pos):
        super().__init__()
        self.app = app
        self.pos = pos
        self.cards: deque[Card] = deque()
        self.draw_empty = True

    @property
    def card_on_top(self):
        if self.is_empty:
            return None
        return self.cards[-1]

    @property
    def card_on_bottom(self):
        if self.is_empty:
            return None
        return self.cards[0]

    @property
    def is_empty(self):
        return self.size == 0

    @property
    def size(self):
        return len(self.cards)

    @property
    def rect(self):
        return pygame.Rect(self.pos, (constants.CARD_WIDTH, constants.CARD_HEIGHT))

    def reset_pos(self):
        for card, pos in zip(self.cards, self.get_card_pos()):
            card.pos = pos

    def animate(self):
        anims = []
        poss = self.get_card_pos()
        for card, pos in zip(self.cards, poss):
            if card.pos != pos:
                anims.append(MoveAnimation(card, pos))
        return ConcurrentAnimations(anims)

    def draw(self, screen):
        if self.draw_empty:
            screen.blit(assets.empty_surface, self.app.game_to_screen(self.pos))
        for card in self.cards:
            card.draw(screen)

    @abstractmethod
    def get_card_pos(self):
        pass

    @abstractmethod
    def can_enter(self, card, amount):
        return True

    def get_cards_to_drag(self, pos):
        if self.rect.collidepoint(pos):
            return 1
        return 0


# Fanned down
class TableauStack(Stack):
    def __init__(self, app, pos):
        super().__init__(app, pos)

    @property
    def rect(self):
        if self.is_empty:
            return super().rect

        pos = list(self.get_card_pos())[-1]
        return pygame.Rect(self.pos, (constants.CARD_WIDTH, pos[1] - self.pos[1] + constants.CARD_HEIGHT))

    def get_card_pos(self):
        x, y = self.pos
        for card in self.cards:
            yield (x, y)
            y += constants.MARGIN if card.flipped else constants.BIG_MARGIN

    def can_enter(self, card: Card, amount):
        if self.is_empty:
            return card.symbol == Symbol.KING

        return self.card_on_top.suit.is_black == card.suit.is_red and card.symbol.is_previous(self.card_on_top.symbol)

    def get_cards_to_drag(self, pos):
        if not self.rect.collidepoint(pos) or self.is_empty:
            return 0

        p = self.get_card_pos()
        next(p)
        for i, j in enumerate(p):
            if pos[1] < j[1]:
                return 0 if self.cards[i].flipped else self.size-i

        return 1


# Squared
class FoundationStack(Stack):
    def __init__(self, app, pos):
        super().__init__(app, pos)

    def get_card_pos(self):
        return [self.pos]*self.size

    def can_enter(self, card: Card, amount):
        if amount != 1:
            return False

        if self.is_empty:
            return card.symbol == Symbol.ACE

        return self.card_on_top.suit == card.suit and card.symbol.is_next(self.card_on_top.symbol)


# Deck
class StockStack(FoundationStack):
    def __init__(self, app, pos):
        super().__init__(app, pos)

    def get_card_pos(self):
        return [self.pos]*self.size

    def can_enter(self, card: Card, amount):
        return False

    def get_cards_to_drag(self, pos):
        return 0


# Fanned sideways
class WasteStack(Stack):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        self.draw_empty = False

    @property
    def rect(self):
        if self.size >= 3:
            return pygame.Rect(self.pos[0] + constants.CARD_WIDTH_MARGIN, self.pos[1], self.pos[0] + constants.CARD_WIDTH, constants.CARD_HEIGHT)
        if self.size >= 2:
            return pygame.Rect(self.pos[0] + constants.CARD_WIDTH_MARGIN*.5, self.pos[1], constants.CARD_WIDTH, constants.CARD_HEIGHT)

        return super().rect

    def get_card_pos(self):
        yield from [self.pos]*max(self.size-2, 1)
        if self.size >= 2:
            yield self.pos[0] + constants.CARD_WIDTH_MARGIN*.5, self.pos[1]
        if self.size >= 3:
            yield self.pos[0] + constants.CARD_WIDTH_MARGIN, self.pos[1]

    def can_enter(self, card, amount):
        return False

    def get_cards_to_drag(self, pos):
        if pygame.Rect(list(self.get_card_pos()).pop(), (constants.CARD_WIDTH, constants.CARD_HEIGHT)).collidepoint(pos):
            return 1
        return 0


# Follows the mouse
class DragStack(TableauStack):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        self.offset = (0, 0)
        self.draw_empty = False
        self.source_stack = None

    def _set_mouse_pos(self, mp):
        self.pos = (mp[0] - self.offset[0], mp[1] - self.offset[1])
        self.reset_pos()

    mouse_pos = property(fset=_set_mouse_pos)

    def get_cards_to_drag(self, pos):
        return 0
