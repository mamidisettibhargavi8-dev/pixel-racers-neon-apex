import pygame

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 900, 700
FPS = 60

# Synthwave Color Palette
BG_COLOR = (15, 12, 29)
ROAD_COLOR = (30, 30, 45)
BORDER_COLOR = (255, 0, 128)
PLAYER_COLOR = (0, 240, 255)
TAIL_LIGHT_COLOR = (255, 30, 60)
NITRO_COLOR = (0, 255, 180)
TEXT_COLOR = (240, 240, 240)
GOLD_COLOR = (255, 215, 0)

# Fonts
font_ui = pygame.font.SysFont("Trebuchet MS", 22, bold=True)
font_large = pygame.font.SysFont("Trebuchet MS", 54, bold=True)
font_sub = pygame.font.SysFont("Trebuchet MS", 26)
