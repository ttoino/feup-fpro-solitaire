from abc import ABC, abstractmethod
from collections import deque

from card import Card, Symbol
import assets


class Stack(ABC):
    def __init__(self, app, pos):
        super().__init__()
        self.app = app
        self.pos = pos
        self.cards: deque[Card] = deque()
        self.draw_empty = True

    # Properties
    @property
    def card_on_top(self):
        if len(self.cards) == 0:
            return None
        return self.cards[-1]

    @property
    def card_on_bottom(self):
        if len(self.cards) == 0:
            return None
        return self.cards[0]

    @property
    def is_empty(self):
        return len(self.cards) == 0

    # Manipulation methods
    def add(self, card):
        self.cards.append(card)
        card.pos = self.get_card_pos(self.cards.index(card))

    def add_all(self, cards):
        self.cards.extend(cards)

        pos = list(self.get_card_pos())
        for card in cards:
            card.pos = pos[self.cards.index(card)]

    def empty(self):
        self.cards.clear()

    def move_card(self, other):
        other.add(self.cards.pop())

    def move_cards(self, other, amount):
        cards_to_move = reversed([self.cards.pop() for _ in range(amount)])
        other.add_all(cards_to_move)

    def move_all(self, other):
        other.add_all(self.cards)
        self.empty()

    def update(self):
        pos = list(self.get_card_pos())
        for i, card in enumerate(self.cards):
            card.pos = pos[i]

    # Drawing
    def draw(self, screen):
        if self.draw_empty:
            screen.blit(assets.empty_surface, self.app.game_to_screen(self.pos))
        for card in self.cards:
            card.draw(screen)

    # Other
    @abstractmethod
    def get_card_pos(self):
        pass

    @abstractmethod
    def can_enter(self, card):
        return True


# Fanned down
class TableauStack(Stack):
    def __init__(self, app, pos):
        super().__init__(app, pos)

    def get_card_pos(self):
        x, y = self.pos
        for card in self.cards:
            yield (x, y)
            y += 10 if card.flipped else 20

    def can_enter(self, card: Card):
        if self.is_empty:
            return card.symbol == Symbol.KING

        return self.card_on_top.suit.is_black == card.suit.is_red and card.symbol.is_next(self.card_on_top.symbol)

    def update(self):
        super().update()

        if self.card_on_top.flipped:
            self.card_on_top.flip()


# Squared
class FoundationStack(Stack):
    def __init__(self, app, pos):
        super().__init__(app, pos)

    def get_card_pos(self):
        return [self.pos]*len(self.cards)

    def can_enter(self, card: Card):
        if self.is_empty:
            return card.symbol == Symbol.ACE

        return self.card_on_top.suit == card.suit and card.symbol.is_next(self.card_on_top.symbol)


# Deck
class StockStack(FoundationStack):
    def __init__(self, app, pos):
        super().__init__(app, pos)

    def get_card_pos(self):
        return [self.pos]*len(self.cards)

    def can_enter(self, card: Card):
        return True


# Fanned sideways
class WasteStack(Stack):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        self.draw_empty = False

    def get_card_pos(self):
        return [self.pos]*len(self.cards)

    def can_enter(self, card):
        return True


class DragStack(TableauStack):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        self.offset = (0, 0)
        # self.draw_empty = False

    def _set_mouse_pos(self, mp):
        self.pos = (mp[0] - self.offset[0], mp[1] - self.offset[1])

    mouse_pos = property(fset=_set_mouse_pos)
