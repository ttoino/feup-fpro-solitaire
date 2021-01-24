from collections import deque
from random import shuffle

import constants
from animation import Animation
from card import Card, Suit, Symbol
from history import History
from move import ConcurrentMoves, FlipMove, Move, MoveMove, SequentialMoves
from stack import DragStack, FoundationStack, Stack, StockStack, TableauStack, WasteStack


class Game():
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.history = History(self)
        self.animations: set[Animation] = set()
        self.deck = self.create_deck()
        shuffle(self.deck)
        self.setup_stacks()
        self.deal()
        self.paused = False
        self.time = 0

    # region Commands
    def create_deck(self):
        return deque(Card(self.app, suit, symbol) for symbol in Symbol for suit in Suit)

    def setup_stacks(self):
        self.foundations = tuple(FoundationStack(self.app, (i*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN)) for i in range(4))
        self.waste = WasteStack(self.app, (4*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN))
        self.stock = StockStack(self.app, (6*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.BIG_MARGIN))
        self.tableaus = tuple(TableauStack(self.app, (i*constants.CARD_WIDTH_MARGIN + constants.BIG_MARGIN, constants.CARD_HEIGHT_MARGIN + constants.BIG_MARGIN)) for i in range(7))
        self.drag = DragStack(self.app, (0, 0))
        self.clickable_stacks: tuple[Stack] = self.foundations + self.tableaus + (self.stock, self.waste)
        self.stacks: tuple[Stack] = (self.stock, self.waste) + tuple(reversed(self.tableaus)) + tuple(reversed(self.foundations)) + (self.drag,)

    def deal(self):
        self.stock.cards = self.deck
        self.stock.reset_pos()
        moves = []
        k = 1
        for i, stack in enumerate(self.tableaus):
            for j in range(i+1):
                m = MoveMove(self.stock, stack, 1)
                if i == j:
                    m = ConcurrentMoves((m, FlipMove(self.stock.cards[-k])))
                moves.append(m)
                k += 1

        self.animations.add(SequentialMoves(moves).redo())

    def undo(self):
        if self.paused:
            return

        self.cancel_animations()
        self.history.undo()

    def redo(self):
        if self.paused:
            return

        self.cancel_animations()
        self.history.redo()

    def deal_card(self):
        if self.paused:
            return

        self.cancel_animations()
        if self.stock.is_empty:
            self.history.add_move(ConcurrentMoves(tuple(FlipMove(c) for c in self.waste.cards) + (MoveMove(self.waste, self.stock, self.waste.size, True),)))
        else:
            self.history.add_move(ConcurrentMoves((FlipMove(self.stock.card_on_top), MoveMove(self.stock, self.waste, 1))))

    def _collect_card_move(self, stack: Stack, foundation: FoundationStack) -> Move:
        move = MoveMove(stack, foundation, 1)
        if len(stack.cards) > 1 and stack.cards[-2].flipped:
            move = ConcurrentMoves((FlipMove(stack.cards[-2]), move))
        return move

    def collect_card(self, stack: Stack):
        if stack.is_empty:
            return

        for f in self.foundations:
            if f.can_enter(stack.card_on_top, 1):
                self.cancel_animations()
                self.history.add_move(self._collect_card_move(stack, f))
                return

    def collect_all(self):
        if self.paused:
            return

        self.cancel_animations()
        moves = []
        b = True
        while b:
            b = False
            for stack in self.tableaus + (self.waste,):
                for f in self.foundations:
                    if not stack.is_empty and f.can_enter(stack.card_on_top, 1):
                        move = self._collect_card_move(stack, f)
                        moves.append(move)
                        move.redo()
                        b = True
                        continue
        if moves:
            m = SequentialMoves(moves)
            list(m.undo().animations)
            self.history.add_move(m)

    def cancel_animations(self):
        if self.paused:
            return

        for animation in self.animations:
            animation.cancel()

    def pause(self):
        self.paused = not self.paused
    # endregion

    def draw(self, screen):
        if not self.paused:
            for animation in set(self.animations):
                animation.tick(self.app.clock.get_time())
                if animation.done:
                    self.animations.remove(animation)

            if not self.animations and all(f.size == 13 for f in self.foundations):
                print("WIN")
                self.app.game_win()
            else:
                self.time += self.app.clock.get_time()

        for stack in self.stacks:
            stack.draw(screen)

    # region Mouse
    def clicked_stack(self, pos):
        for s in self.clickable_stacks:
            if s.rect.collidepoint(pos):
                return s

    def on_mouseclick_l(self, pos):
        if self.paused:
            return

        if self.clicked_stack(pos) == self.stock:
            self.deal_card()

    def on_mouseclick_m(self, pos):
        if self.paused:
            return

        s = self.clicked_stack(pos)
        if s and s.get_cards_to_drag(pos) == 1:
            self.collect_card(s)
        else:
            self.collect_all()

    def on_mousedrag_l(self, pos):
        if self.paused:
            return

        self.drag.mouse_pos = pos

    def on_mousedragbegin_l(self, pos):
        if self.paused:
            return

        for s in self.stacks:
            c = s.get_cards_to_drag(pos)
            if c:
                self.cancel_animations()
                self.drag.cards += list(s.cards)[s.size-c:]
                self.drag.source_stack = s
                self.drag.offset = (pos[0] - self.drag.cards[0].pos[0], pos[1] - self.drag.cards[0].pos[1])

    def on_mousedragend_l(self, pos):
        if self.paused:
            return

        if self.drag.is_empty:
            return

        for s in self.stacks:
            if s.rect.collidepoint(pos) and s.can_enter(self.drag.card_on_bottom, self.drag.size):
                move = MoveMove(self.drag.source_stack, s, self.drag.size)
                if self.drag.source_stack in self.tableaus and self.drag.source_stack.size > self.drag.size and self.drag.source_stack.cards[-self.drag.size-1].flipped:
                    move = ConcurrentMoves((FlipMove(self.drag.source_stack.cards[-self.drag.size-1]), move))
                self.history.add_move(move)
                break

        self.drag.cards.clear()
        self.animations.add(self.drag.source_stack.animate())
    # endregion
