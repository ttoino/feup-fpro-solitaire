import pygame
from pygame.constants import KMOD_CTRL, K_ESCAPE, K_c, K_d, K_z
import constants
from game import Game
import assets


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

        self.KEYMAPPING = {
            pygame.K_n: lambda e: self.new_game() if e.mod & pygame.KMOD_CTRL else None,
            pygame.K_d: lambda e: self.game.deal_card(),
            pygame.K_c: lambda e: self.game.collect_all(),
            pygame.K_z: lambda e: self.game.undo() if e.mod & pygame.KMOD_CTRL else None,
            pygame.K_y: lambda e: self.game.redo() if e.mod & pygame.KMOD_CTRL else None,
            pygame.K_ESCAPE: lambda e: self.game.cancel_animations()
        }

        pygame.display.set_caption("Solitaire")
        pygame.display.set_icon(assets.get_icon())
        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT), constants.SCREEN_FLAGS, vsync=True)
        self.clock = pygame.time.Clock()
        assets.load_svgs()
        self.on_resize(pygame.event.Event(pygame.VIDEORESIZE, size=(constants.WIDTH, constants.HEIGHT)))

        self.new_game()
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
            for b in btns:
                getattr(self, f"on_mouse{name}", lambda e, b: None)(event, b)
                getattr(self, f"on_mouse{name}_{b}", lambda e: None)(event)
                getattr(self.game, f"on_mouse{name}_{b}", lambda p: None)(pos)
        return inner

    def on_key(self, event):
        self.KEYMAPPING.get(event.key, lambda e: None)(event)

    def loop(self):
        while self.running:
            self.clock.tick(200)
            print(f"FPS: {self.clock.get_fps():3.0f}", end="\r")
            self.events()
            self.draw()

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

        self.origin = ((width - constants.WIDTH*self.scale)*.5, 0)

        assets.render_svgs(self.scale)

    # MOUSE EVENTS
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

    def screen_to_game(self, coords):
        return ((coords[0] - self.origin[0])/self.scale, (coords[1] - self.origin[1])/self.scale)

    def game_to_screen(self, coords):
        return (coords[0]*self.scale + self.origin[0], coords[1]*self.scale + self.origin[1])

    def draw(self):
        self.draw_background()

        if self.game:
            self.game.draw(self.screen)

        pygame.display.flip()

    def draw_background(self):
        self.screen.fill((16, 124, 16))

    def new_game(self):
        self.game = Game(self)


if __name__ == "__main__":
    app = App()
    app.loop()
