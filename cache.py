import pygame

_cached_gradients = {}
_cached_scanlines = {}


def create_gradient_surface(width, height, top_color, bottom_color):
    if height <= 0 or width <= 0:
        return pygame.Surface((max(width, 1), max(height, 1)))
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient


def get_cached_gradient(width, height, top_color, bottom_color):
    key = (width, height, top_color, bottom_color)
    if key not in _cached_gradients:
        _cached_gradients[key] = create_gradient_surface(width, height, top_color, bottom_color)
    return _cached_gradients[key]


def get_scanline_overlay(width, height):
    key = (width, height)
    if key not in _cached_scanlines:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 3):
            pygame.draw.line(surf, (0, 0, 0, 25), (0, y), (width, y))
        _cached_scanlines[key] = surf
    return _cached_scanlines[key]


def clear_caches():
    _cached_gradients.clear()
    _cached_scanlines.clear()
