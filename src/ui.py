from abc import ABC, abstractmethod
from enum import Enum, auto

import pygame

import assets
import constants


class Button(ABC):
    def __init__(self, pos, size, onclick, enabled):
        super().__init__()
        self.pos = pos
        self.size = size
        self.onclick = onclick
        self.enabled = enabled
        self.hovered = False

    @abstractmethod
    def render(self, scale):
        self.surf = pygame.Surface(self.size).convert_alpha()
        self.surf.fill(constants.TRANSPARENT)
        self.disabled_surf = pygame.Surface(self.size).convert_alpha()
        self.disabled_surf.fill(constants.TRANSPARENT)
        self.hovered_surf = pygame.Surface(self.size).convert_alpha()
        self.hovered_surf.fill(constants.TRANSPARENT)

    @abstractmethod
    def inside(self, mousepos) -> bool:
        return False

    def draw(self, screen):
        if not self.enabled():
            screen.blit(self.disabled_surf, self.pos)
        elif self.hovered:
            screen.blit(self.hovered_surf, self.pos)
        else:
            screen.blit(self.surf, self.pos)


class TextButton(Button):
    font = None

    @classmethod
    def render_font(cls, scale):
        cls.font = pygame.font.Font(assets.normalize_path("Roboto-Medium.ttf"), round(14*scale))

    def __init__(self, pos, width, scale, text, onclick, enabled=lambda: True):
        pos = round(pos[0]*scale), round(pos[1]*scale)
        size = round(width*scale), round(36*scale)
        super().__init__(pos, size, onclick, enabled)
        self.text = text
        self.rect = pygame.Rect(pos, size)

        self.render(scale)

    def render(self, scale):
        super().render(scale)
        text = self.font.render(self.text, True, constants.BLACK)
        text.set_alpha(constants.ENABLED_ALPHA)

        pygame.draw.rect(self.surf, constants.BUTTON_COLOR, (0, 0, *self.size), border_radius=round(4*scale))
        self.surf.blit(text, ((self.size[0]-text.get_width())/2, (self.size[1]-text.get_height())/2))

        pygame.draw.rect(self.hovered_surf, constants.BUTTON_COLOR_HOVER, (0, 0, *self.size), border_radius=round(4*scale))
        self.hovered_surf.blit(text, ((self.size[0]-text.get_width())/2, (self.size[1]-text.get_height())/2))

        text.set_alpha(constants.DISABLED_ALPHA)
        pygame.draw.rect(self.disabled_surf, constants.BUTTON_COLOR_DISABLED, (0, 0, *self.size), border_radius=round(4*scale))
        self.disabled_surf.blit(text, ((self.size[0]-text.get_width())/2, (self.size[1]-text.get_height())/2))

    def inside(self, mousepos) -> bool:
        return self.rect.collidepoint(mousepos)


class IconButton(Button):
    def __init__(self, pos, scale, icon, onclick, enabled=lambda: True):
        pos = round(pos[0]*scale), round(pos[1]*scale)
        size = round(48*scale), round(48*scale)
        super().__init__(pos, size, onclick, enabled)
        self.radius = round(24*scale)
        self.icon = icon
        self.center = self.pos[0] + self.radius, self.pos[1] + self.radius

        self.render(scale)

    def render(self, scale):
        super().render(scale)
        icon = assets.icon_surfaces[self.icon]
        icon.set_alpha(constants.ENABLED_ALPHA)

        self.surf.blit(icon, ((self.size[0]-icon.get_width())/2, (self.size[1]-icon.get_height())/2))

        pygame.draw.circle(self.hovered_surf, constants.BLACK + (constants.DISABLED_ALPHA,), (self.radius, self.radius), self.radius)
        self.hovered_surf.blit(icon, ((self.size[0]-icon.get_width())/2, (self.size[1]-icon.get_height())/2))

        icon.set_alpha(constants.DISABLED_ALPHA)
        self.disabled_surf.blit(icon, ((self.size[0]-icon.get_width())/2, (self.size[1]-icon.get_height())/2))

    def inside(self, mousepos) -> bool:
        return (self.center[0]-mousepos[0])**2 + (self.center[1]-mousepos[1])**2 < self.radius**2


class UIType(Enum):
    HOME = auto()
    GAME = auto()
    WIN = auto()


class UI():
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current = UIType.HOME

        self.draw_methods = {
            UIType.HOME: self.draw_home_ui,
            UIType.GAME: self.draw_game_ui,
            UIType.WIN: self.draw_win_ui
        }
        self.buttons = {
            UIType.HOME: lambda: self.home_buttons,
            UIType.GAME: lambda: self.paused_buttons if self.app.game.paused else self.game_buttons,
            UIType.WIN: lambda: self.win_buttons
        }

    def home(self):
        self.current = UIType.HOME

    def draw_background(self, screen):
        screen.fill(constants.BACKGROUND_COLOR)

    def draw_home_ui(self, screen: pygame.Surface):
        screen.blit(self.home_surf, (0, 0))
        for button in self.home_buttons:
            button.draw(screen)

    def draw_game(self, screen: pygame.Surface):
        self.app.game.draw(screen)
        screen.blit(self.app_bar, (0, 0))
        time = self.app.game.time
        text = self.appbar_font.render(f"{time//60000:02d}:{time/1000%60:05.2f}", True, constants.WHITE)
        text.set_alpha(constants.ENABLED_ALPHA)
        screen.blit(text, ((self.app_bar.get_width()-text.get_width())/2, (self.app_bar.get_height()-text.get_height())/2))
        for button in self.game_buttons:
            button.draw(screen)

    def draw_game_ui(self, screen: pygame.Surface):
        self.draw_game(screen)
        if self.app.game.paused:
            screen.blit(self.paused_surf, (0, 0))
            for button in self.paused_buttons:
                button.draw(screen)
            for button in self.game_buttons:
                button.hovered = False

    def draw_win_ui(self, screen: pygame.Surface):
        self.draw_game(screen)
        screen.blit(self.win_surf, (0, 0))
        for button in self.win_buttons:
            button.draw(screen)

    def draw(self, screen: pygame.Surface):
        self.draw_background(screen)
        self.draw_methods[self.current](screen)

        pygame.display.flip()

    def middle(self, size, scale):
        return size[0]/scale/2

    def render_home(self, size, scale):
        self.home_surf = pygame.Surface(size).convert_alpha()
        self.home_surf.fill(constants.TRANSPARENT)
        text = self.big_font.render("Solitaire", True, constants.WHITE)
        text.set_alpha(constants.ENABLED_ALPHA)
        self.home_surf.blit(text, ((size[0]-text.get_width())/2, 128*scale))

        self.home_buttons = [
            TextButton((self.middle(size, scale)-64, 256), 128, scale, "NEW GAME", lambda: self.app.new_game()),
        ]

    def render_game(self, size, scale):
        self.app_bar = pygame.Surface((size[0], round(constants.APPBAR_HEIGHT*scale))).convert_alpha()
        self.app_bar.fill(constants.APPBAR_COLOR)
        self.appbar_font = pygame.font.Font(assets.normalize_path("Roboto-Medium.ttf"), round(20*scale))

        self.game_buttons = [
            IconButton((self.app.origin[0] + 8, 0), scale, "pause", lambda: self.app.game.pause()),
            IconButton((self.app.origin[0] + 56, 0), scale, "chevron-up", lambda: self.app.game.collect_all()),
            IconButton((self.app.origin[0] + constants.WIDTH - 96, 0), scale, "undo", lambda: self.app.game.undo(), lambda: self.app.game.history.past),
            IconButton((self.app.origin[0] + constants.WIDTH - 48, 0), scale, "redo", lambda: self.app.game.redo(), lambda: self.app.game.history.future)
        ]

        self.paused_surf = pygame.Surface(size).convert_alpha()
        self.paused_surf.fill(constants.BLACK + (constants.DISABLED_ALPHA,))
        text = self.title_font.render("Paused", True, constants.WHITE)
        text.set_alpha(constants.ENABLED_ALPHA)
        width = round(text.get_width() + 32*scale)
        pygame.draw.rect(self.paused_surf, constants.BACKGROUND_COLOR, ((size[0]-width)//2, round(112*scale), width, round(256*scale)), border_radius=round(16*scale))
        self.paused_surf.blit(text, ((size[0]-text.get_width())/2, 128*scale))

        self.paused_buttons = [
            TextButton((self.middle(size, scale)-64, 208), 128, scale, "RESUME", lambda: self.app.game.pause()),
            TextButton((self.middle(size, scale)-64, 256), 128, scale, "NEW GAME", lambda: self.app.new_game()),
            TextButton((self.middle(size, scale)-64, 304), 128, scale, "MAIN MENU", self.home),
        ]

    def render_win(self, size, scale):
        self.win_surf = pygame.Surface(size).convert_alpha()
        self.win_surf.fill(constants.TRANSPARENT)
        text = self.big_font.render("Victory!", True, constants.WHITE)
        text.set_alpha(constants.ENABLED_ALPHA)
        self.win_surf.blit(text, ((size[0]-text.get_width())/2, 320*scale))

        self.win_buttons = [
            TextButton((self.middle(size, scale) - 136, 256), 128, scale, "NEW GAME", lambda: self.app.new_game()),
            TextButton((self.middle(size, scale) + 8, 256), 128, scale, "MAIN MENU", self.home),
        ]

    def render(self, size, scale):
        self.title_font = pygame.font.Font(assets.normalize_path("Roboto-Regular.ttf"), round(48*scale))
        self.big_font = pygame.font.Font(assets.normalize_path("Roboto-Regular.ttf"), round(96*scale))
        TextButton.render_font(scale)
        self.render_home(size, scale)
        self.render_game(size, scale)
        self.render_win(size, scale)

    # region Mouse events
    def on_mousemove(self, event):
        bo = False
        for b in self.buttons[self.current]():
            if b.inside(event.pos) and b.enabled():
                b.hovered = True
                bo = True
            else:
                b.hovered = False
        if bo:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def on_mouseclick_l(self, event):
        for b in self.buttons[self.current]():
            if b.inside(event.pos) and b.enabled():
                b.onclick()
    # endregion
