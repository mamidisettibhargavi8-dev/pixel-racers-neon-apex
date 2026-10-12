import pygame
import random
from config import *

class TrafficVehicle:
    def __init__(self, road_left, road_right):
        self.width = random.choice([42, 46])
        self.height = random.choice([70, 85])
        self.x = random.randint(road_left + 10, road_right - self.width - 10)
        self.y = -random.randint(120, 400)
        self.speed_y = random.uniform(2.5, 4.5)
        self.color = random.choice([(255, 70, 70), (255, 165, 0), (180, 70, 255), (200, 200, 200)])

    def update(self, game_speed):
        self.y += (game_speed - self.speed_y)

    def draw(self, surface):
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        pygame.draw.rect(surface, self.color, rect, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), (self.x + 6, self.y + self.height - 24, self.width - 12, 14), border_radius=3)

class PickupItem:
    def __init__(self, road_left, road_right, item_type):
        self.item_type = item_type  # "NITRO" or "SCORE"
        self.radius = 12
        self.x = random.randint(road_left + 20, road_right - 20)
        self.y = -random.randint(200, 500)

    def update(self, game_speed):
        self.y += game_speed

    def draw(self, surface):
        color = NITRO_COLOR if self.item_type == "NITRO" else GOLD_COLOR
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, width=2)
