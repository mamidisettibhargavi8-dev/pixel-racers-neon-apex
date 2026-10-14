import pygame
import random
from config import *

class Particle:
    def __init__(self, x, y, color, speed_x, speed_y, size, lifetime):
        self.x, self.y = x, y
        self.color = color
        self.speed_x, self.speed_y = speed_x, speed_y
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 70
        
        # Movement speeds & physics
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.base_speed = 4.0
        self.max_speed = 8.0
        self.acceleration = 0.5
        self.friction = 0.92
        
        # Status attributes required by main.py
        self.health = 100.0
        self.nitro = 100.0
        self.is_boosting = False

    def handle_input(self, keys):
        # Left and Right steering
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x -= self.acceleration
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x += self.acceleration

        # Up arrow / W to accelerate forward
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed_y = min(self.speed_y + self.acceleration, self.max_speed)
        else:
            self.speed_y = max(self.speed_y - self.acceleration, self.base_speed)

        # Nitro boost handling
        self.is_boosting = (keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]) and self.nitro > 0.5
        if self.is_boosting:
            self.nitro = max(0.0, self.nitro - 0.6)

    def update(self, road_left, road_right, particles):
        keys = pygame.key.get_pressed()
        self.handle_input(keys)

        # Apply physics / lateral movement
        self.speed_x *= self.friction
        self.x += self.speed_x

        # Keep player inside the road boundaries horizontally
        if self.x < road_left:
            self.x = road_left
            self.speed_x = 0
        elif self.x + self.width > road_right:
            self.x = road_right - self.width
            self.speed_x = 0

        # Generate nitro particles if boosting
        if self.is_boosting:
            p_x = self.x + self.width / 2 + random.uniform(-4, 4)
            p_y = self.y + self.height
            particles.append(Particle(p_x, p_y, NITRO_COLOR, random.uniform(-0.5, 0.5), random.uniform(3, 7), random.uniform(4, 7), 18))

    def draw(self, surface):
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        # Main car chassis
        pygame.draw.rect(surface, (15, 15, 25), rect, border_radius=8)
        pygame.draw.rect(surface, PLAYER_COLOR, rect, width=2, border_radius=8)
        
        # Windshield
        pygame.draw.rect(surface, (0, 0, 0), (self.x + 8, self.y + 16, self.width - 16, 20), border_radius=4)
        
        # Tail lights (turn neon blue when boosting)
        tail_color = NITRO_COLOR if self.is_boosting else TAIL_LIGHT_COLOR
        pygame.draw.rect(surface, tail_color, (self.x + 4, self.y + self.height - 6, 8, 4))
        pygame.draw.rect(surface, tail_color, (self.x + self.width - 12, self.y + self.height - 6, 8, 4))
