import pygame
from constants import VERTICAL, HORIZONTAL

pygame.init()

WIDTH, HEIGHT = VERTICAL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WU DONG Running")

font_title = pygame.font.Font(None, 48)
font_header = pygame.font.Font(None, 36)
font_menu_section = pygame.font.Font(None, 28)
font_normal = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 22)
font_popup = pygame.font.Font(None, 32)


def reset_screen(orientation):
    global WIDTH, HEIGHT, screen
    if orientation == "vertical":
        WIDTH, HEIGHT = VERTICAL
    else:
        WIDTH, HEIGHT = HORIZONTAL
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
