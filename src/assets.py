import os
import sys

import pygame
from svg import Parser, Rasterizer
import card

card_svgs = None
back_svg = None
empty_svg = None

card_surfaces = None
back_surface = None
empty_surface = None


def get_icon():
    return render_svg(load_svg("icon.svg"), 1, False)


def load_svgs():
    global card_svgs, back_svg, empty_svg
    card_svgs = {(suit, symbol): load_svg(f"{suit.value}_{symbol.value}.svg") for suit in card.Suit for symbol in card.Symbol}
    back_svg = load_svg("back.svg")
    empty_svg = load_svg("empty.svg")


def render_svgs(scale):
    global card_surfaces, back_surface, empty_surface
    card_surfaces = dict(
        map(lambda t: (t[0], render_svg(t[1], scale)), card_svgs.items()))
    back_surface = render_svg(back_svg, scale)
    empty_surface = render_svg(empty_svg, scale)


def normalize_path(file):
    dir = getattr(sys, "_MEIPASS", "")
    return os.path.join(dir, "assets", file)


def load_svg(file):
    return Parser.parse_file(normalize_path(file))


rasterizer = Rasterizer()


def render_svg(svg, scale, convert=True):
    global rasterizer
    surface_size = round(svg.width * scale), round(svg.height * scale)
    buffer = rasterizer.rasterize(svg, *surface_size, scale)
    surface = pygame.image.frombuffer(buffer, surface_size, "RGBA")
    return surface.convert_alpha() if convert else surface
