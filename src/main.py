import pygame

import assets
import constants
from game import Game
from ui import UI, UIType


class App():
    def __init__(self):
        super().__init__()
        pygame.init()

        self.EVENTS = {
            pygame.QUIT: self.on_quit,
            pygame.VIDEORESIZE: self.on_resize,
            pygame.MOUSEBUTTONDOWN: self.mouse_event("down"),
            pygame.MOUSEBUTTONUP: self.mouse_event("up"),
            pygame.MOUSEMOTION: self.mouse_event("move"),
            pygame.KEYDOWN: self.on_key
        }

        self.mousedown = {b: False for b in ("l", "r", "m")}
        self.mousedrag = {b: False for b in ("l", "r", "m")}

        pygame.display.set_caption("Solitaire")
        pygame.display.set_icon(assets.get_icon())
        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT), constants.SCREEN_FLAGS, vsync=True)
        self.clock = pygame.time.Clock()
        assets.load_svgs()
        self.game = None
        self.ui = UI(self)
        self.on_resize(pygame.event.Event(pygame.VIDEORESIZE, size=(constants.WIDTH, constants.HEIGHT)))

        self.running = True

    def mouse_event(self, name):
        def inner(event):
            btns = []
            button, buttons = getattr(event, "button", -1), getattr(event, "buttons", [])
            if button == pygame.BUTTON_LEFT or pygame.BUTTON_LEFT in buttons:
                btns.append("l")
            if button == pygame.BUTTON_RIGHT or pygame.BUTTON_RIGHT in buttons:
                btns.append("r")
            if button == pygame.BUTTON_MIDDLE or pygame.BUTTON_MIDDLE in buttons:
                btns.append("m")

            pos = self.screen_to_game(event.pos)
            getattr(self.ui, f"on_mouse{name}", lambda e: None)(event)
            for b in btns:
                getattr(self, f"on_mouse{name}", lambda e, b: None)(event, b)
                getattr(self, f"on_mouse{name}_{b}", lambda e: None)(event)
                getattr(self.ui, f"on_mouse{name}_{b}", lambda e: None)(event)
                if self.game:
                    getattr(self.game, f"on_mouse{name}_{b}", lambda p: None)(pos)
        return inner

    def on_key(self, event):
        print(pygame.key.name(event.key))
        getattr(self, f"on_key_{pygame.key.name(event.key)}".lower(), lambda e: None)(event)

    def loop(self):
        while self.running:
            self.clock.tick(200)
            print(f"FPS: {self.clock.get_fps():3.0f}", end="\r")
            self.events()
            self.ui.draw(self.screen)

    def events(self):
        for event in pygame.event.get():
            try:
                self.EVENTS[event.type](event)
            except KeyError as e:
                print(f"Event {pygame.event.event_name(event.type)} not handled", event.__dict__)

    def on_quit(self, event):
        self.running = False

    def on_resize(self, event):
        width, height = event.size
        if width/height < constants.RATIO:
            self.scale = width/constants.WIDTH
        else:
            self.scale = height/constants.HEIGHT

        self.origin = ((width/self.scale - constants.WIDTH)*.5, constants.APPBAR_HEIGHT)

        assets.render_svgs(self.scale)
        self.ui.render(event.size, self.scale)

    def game_win(self):
        self.game.paused = True
        self.ui.current = UIType.WIN

    # region Mouse events
    def on_mousedown(self, event, b):
        self.mousedown[b] = True

    def on_mousemove(self, event, b):
        if not self.mousedrag[b] and self.mousedown[b]:
            self.mousedrag[b] = True
            self.mouse_event("dragbegin")(event)

        self.mousedrag[b] = self.mousedown[b]

        if self.mousedrag[b]:
            self.mouse_event("drag")(event)

    def on_mouseup(self, event, b):
        self.mousedown[b] = False
        if self.mousedrag[b]:
            self.mouse_event("dragend")(event)
        else:
            self.mouse_event("click")(event)

    def on_mousedragend(self, event, b):
        self.mousedrag[b] = False
    # endregion

    # region Keyboard events
    def on_key_n(self, event):
        if event.mod & pygame.KMOD_CTRL:
            self.new_game()

    def on_key_d(self, event):
        if self.ui.current == UIType.GAME:
            self.game.deal_card()

    def on_key_c(self, event):
        if self.ui.current == UIType.GAME:
            self.game.collect_all()

    def on_key_z(self, event):
        if self.ui.current == UIType.GAME and event.mod & pygame.KMOD_CTRL:
            self.game.undo()

    def on_key_y(self, event):
        if self.ui.current == UIType.GAME and event.mod & pygame.KMOD_CTRL:
            self.game.redo()

    def on_key_s(self, event):
        if self.ui.current == UIType.GAME:
            self.game.cancel_animations()

    def on_key_escape(self, event):
        if self.ui.current == UIType.GAME:
            self.game.pause()

    def on_key_space(self, event):
        if self.ui.current == UIType.GAME:
            self.game.cancel_animations()

    def on_key_f12(self, event):
        self.game_win()
    # endregion

    def screen_to_game(self, coords):
        return (coords[0]/self.scale - self.origin[0], coords[1]/self.scale - self.origin[1])

    def game_to_screen(self, coords):
        return ((coords[0] + self.origin[0])*self.scale, (coords[1] + self.origin[1])*self.scale)

    def new_game(self):
        self.game = Game(self)
        self.ui.current = UIType.GAME


if __name__ == "__main__":
    app = App()
    app.loop()
