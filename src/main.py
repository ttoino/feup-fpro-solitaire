import pygame
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
            pygame.MOUSEBUTTONDOWN: self.on_mousedown,
            pygame.MOUSEBUTTONUP: self.on_mouseup,
            pygame.MOUSEMOTION: self.on_mousemove,
            pygame.KEYDOWN: self.on_key
        }

        self.KEYMAPPING = {
            pygame.K_SPACE: self.test
        }

        self.mousedown = False
        self.mousedrag = False

        pygame.display.set_caption("Solitaire")
        pygame.display.set_icon(assets.get_icon())
        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT), constants.SCREEN_FLAGS, vsync=True)
        self.clock = pygame.time.Clock()
        assets.load_svgs()
        self.on_resize(pygame.event.Event(pygame.VIDEORESIZE, size=(constants.WIDTH, constants.HEIGHT)))

        self.start_game()

        self.running = True

    def loop(self):
        while self.running:
            self.clock.tick(500)
            print(f"FPS: {self.clock.get_fps():3.0f}", end="\r")
            self.events()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            try:
                self.EVENTS[event.type](event)
            except Exception as e:
                pass

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

    def on_mousedown(self, event):
        # print("MOUSE DOWN")
        self.mousedown = True

    def on_mousemove(self, event):
        # print("MOUSE MOVE")
        if not self.mousedrag and self.mousedown:
            self.mousedrag = True
            self.on_mousedragbegin(event)

        self.mousedrag = self.mousedown

        if self.mousedrag:
            self.on_mousedrag(event)

    def on_mouseup(self, event):
        # print("MOUSE UP")
        self.mousedown = False
        if self.mousedrag:
            self.on_mousedragend(event)
        else:
            self.on_mouseclick(event)

    def on_mouseclick(self, event):
        # print("CLICK")
        pass

    def on_mousedragbegin(self, event):
        # print("BEGIN DRAG")
        pass

    def on_mousedragend(self, event):
        # print("END DRAG")
        self.mousedrag = False
        pass

    def on_mousedrag(self, event):
        self.game.drag.mouse_pos = self.screen_to_game(event.pos)

        # print("MOUSE DRAG")
        pass

    def on_key(self, event):
        self.KEYMAPPING[event.key]()

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

    def start_game(self):
        self.game = Game(self)

    def test(self):
        self.game.stock.draw_card()


if __name__ == "__main__":
    app = App()
    app.loop()
