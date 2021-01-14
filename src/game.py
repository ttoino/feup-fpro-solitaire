from collections import deque
from random import shuffle

import constants
from card import Card, Suit, Symbol
from stack import DragStack, FoundationStack, Stack, StockStack, TableauStack, WasteStack


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
        self.foundations = tuple(FoundationStack(self.app, (i*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN)) for i in range(4))
        self.waste = WasteStack(self.app, (4*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN))
        self.stock = StockStack(self.app, (6*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN), self.waste)
        self.tableaus = tuple(TableauStack(self.app, (i*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.CARD_HEIGHT_MARGIN + constants.BIG_MARGIN)) for i in range(7))
        self.drag = DragStack(self.app, (0, 0))
        self.clickable_stacks: tuple[Stack] = self.foundations + self.tableaus + (self.stock, self.waste)
        self.stacks: tuple[Stack] = self.clickable_stacks + (self.drag,)

    def deal(self):
        self.stock.cards = self.deck
        self.stock.update()
        for i, stack in enumerate(self.tableaus):
            stack.add_all([self.deck.pop() for _ in range(i+1)])
            stack.update()

    def draw(self, screen):
        for stack in self.stacks:
            stack.draw(screen)

    def clicked_stack(self, pos):
        for s in self.clickable_stacks:
            if s.rect.collidepoint(pos):
                return s

    def on_mouseclick_l(self, pos):
        if self.clicked_stack(pos) == self.stock:
            self.stock.draw_card()

    def collect_card(self, stack: Stack):
        for f in self.foundations:
            if f.can_enter(stack.card_on_top, 1):
                stack.move_card(f)
                stack.update()
                return True

    def collect_all(self):
        b = True
        while b:
            b = False
            for s in self.tableaus + (self.waste,):
                if not s.is_empty and self.collect_card(s):
                    b = True

    def on_mouseclick_m(self, pos):
        s = self.clicked_stack(pos)
        if s and s.get_cards_to_drag(pos) == 1:
            self.collect_card(s)
        else:
            self.collect_all()

    def on_mousedrag_l(self, pos):
        self.drag.mouse_pos = pos

    def on_mousedragbegin_l(self, pos):
        for s in self.stacks:
            c = s.get_cards_to_drag(pos)
            if c:
                s.move_cards(self.drag, c)
                self.drag.source_stack = s
                self.drag.offset = (pos[0] - self.drag.cards[0].pos[0], pos[1] - self.drag.cards[0].pos[1])

    def on_mousedragend_l(self, pos):
        if self.drag.is_empty:
            return

        for s in self.stacks:
            if s.rect.collidepoint(pos) and s.can_enter(self.drag.card_on_bottom, self.drag.size):
                self.drag.move_all(s)
                s.update()
                break

        self.drag.move_all(self.drag.source_stack)
        self.drag.source_stack.update()
