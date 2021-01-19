from abc import ABC, abstractmethod

import pygame

import constants

from card import Card


class Animation(ABC):
    def __init__(self):
        super().__init__()
        self.time = 0
        self.done = False

    @property
    def progress(self):
        return self.time/constants.ANIMATION_LENGTH

    @abstractmethod
    def tick(self, time):
        self.time += time
        if self.time >= constants.ANIMATION_LENGTH:
            self.time = constants.ANIMATION_LENGTH
            self.done = True

    @abstractmethod
    def cancel(self):
        self.done = True
        self.time = constants.ANIMATION_LENGTH

    def map(self, start, offset):
        return start + offset*self.progress


class MoveAnimation(Animation):
    def __init__(self, card: Card, to):
        super().__init__()
        self.card = card
        self.start_pos = card.pos
        self.offset = to[0] - self.start_pos[0], to[1] - self.start_pos[1]

    def tick(self, time):
        super().tick(time)
        self.card.pos = self.map(self.start_pos[0], self.offset[0]), self.map(self.start_pos[1], self.offset[1])

    def cancel(self):
        super().cancel()
        self.card.pos = self.start_pos[0] + self.offset[0], self.start_pos[1] + self.offset[1]


class FlipAnimation(Animation):
    def __init__(self, card: Card):
        super().__init__()
        self.card = card
        self.end = card.flipped

    def tick(self, time):
        super().tick(time)
        surface = self.card.asset if (self.progress > .5) != (self.end) else self.card.back_asset
        self.card.surface = pygame.transform.smoothscale(surface, (round(surface.get_width()*abs(self.map(-1, 2))), surface.get_height()))

    def cancel(self):
        super().cancel()
        self.card.surface = self.card.back_asset if self.end else self.card.asset


class ConcurrentAnimations(Animation):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations

    def tick(self, time):
        for animation in self.animations:
            animation.tick(time)
        self.done = all(map(lambda x: x.done, self.animations))

    def cancel(self):
        for animation in self.animations:
            if not animation.done:
                animation.cancel()
        self.done = True


class SequentialAnimations(Animation):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.current = next(self.animations)

    def tick(self, time):
        self.current.tick(time)
        if self.current.done:
            try:
                self.current = next(self.animations)
            except StopIteration:
                self.done = True

    def cancel(self):
        self.current.cancel()
        for animation in self.animations:
            animation.cancel()
        self.done = True
