import pygame
import sys
import random
from config import *
from player import PlayerVehicle, Particle
from entities import TrafficVehicle, PickupItem

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Racers - Neon Apex: Night Drive")
clock = pygame.time.Clock()

class GameEngine:
    def __init__(self):
        self.road_width = 380
        self.road_left = (WIDTH - self.road_width) // 2
        self.road_right = self.road_left + self.road_width
        self.player = PlayerVehicle(WIDTH // 2 - 22, HEIGHT - 130)
        
        self.traffic = []
        self.pickups = []
        self.particles = []
        
        self.road_scroll = 0.0
        self.distance = 0.0
        self.score = 0
        self.multiplier = 1.0
        self.state = "START"

    def reset(self):
        self.player = PlayerVehicle(WIDTH // 2 - 22, HEIGHT - 130)
        self.traffic.clear()
        self.pickups.clear()
        self.particles.clear()
        self.road_scroll = 0.0
        self.distance = 0.0
        self.score = 0
        self.multiplier = 1.0
        self.state = "PLAYING"

    def get_game_speed(self):
        base = self.player.base_speed + (self.distance / 1500.0)
        return base * 1.6 if self.player.is_boosting else base

    def update(self):
        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        game_speed = self.get_game_speed()
        self.road_scroll = (self.road_scroll + game_speed) % 60
        self.distance += game_speed * 0.1
        self.score += int(1 * self.multiplier)

        self.player.update(self.road_left, self.road_right, self.particles)

        # Spawning logic
        if len(self.traffic) < 4 and random.random() < 0.03:
            self.traffic.append(TrafficVehicle(self.road_left, self.road_right))
        if len(self.pickups) < 2 and random.random() < 0.015:
            p_type = "NITRO" if random.random() < 0.6 else "SCORE"
            self.pickups.append(PickupItem(self.road_left, self.road_right, p_type))

        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        # Traffic collisions
        for t in self.traffic[:]:
            t.update(game_speed)
            t_rect = pygame.Rect(t.x, t.y, t.width, t.height)
            if player_rect.colliderect(t_rect):
                self.player.health -= 35
                for _ in range(15):
                    self.particles.append(Particle(
                        player_rect.centerx, player_rect.centery,
                        BORDER_COLOR, random.uniform(-4, 4), random.uniform(-4, 4), random.uniform(3, 6), 25
                    ))
                self.traffic.remove(t)
                if self.player.health <= 0:
                    self.state = "GAMEOVER"
            elif t.y > HEIGHT + 100:
                self.traffic.remove(t)

        # Pickup collection
        for p in self.pickups[:]:
            p.update(game_speed)
            dist = ((self.player.x + self.player.width/2 - p.x)**2 + (self.player.y + self.player.height/2 - p.y)**2)**0.5
            if dist < (p.radius + 20):
                if p.item_type == "NITRO":
                    self.player.nitro = min(100.0, self.player.nitro + 35.0)
                elif p.item_type == "SCORE":
                    self.score += 500
                    self.multiplier = min(3.0, self.multiplier + 0.5)
                self.pickups.remove(p)
            elif p.y > HEIGHT + 50:
                self.pickups.remove(p)

        for pt in self.particles[:]:
            pt.update()
            if pt.lifetime <= 0:
                self.particles.remove(pt)

    def render(self, surface):
        surface.fill(BG_COLOR)
        pygame.draw.rect(surface, ROAD_COLOR, (self.road_left, 0, self.road_width, HEIGHT))
        pygame.draw.line(surface, BORDER_COLOR, (self.road_left, 0), (self.road_left, HEIGHT), width=4)
        pygame.draw.line(surface, BORDER_COLOR, (self.road_right, 0), (self.road_right, HEIGHT), width=4)

        lane_x1 = self.road_left + self.road_width // 3
        lane_x2 = self.road_left + (2 * self.road_width) // 3
        for y in range(-60, HEIGHT + 60, 50):
            draw_y = y + int(self.road_scroll)
            pygame.draw.line(surface, (70, 70, 90), (lane_x1, draw_y), (lane_x1, draw_y + 25), width=2)
            pygame.draw.line(surface, (70, 70, 90), (lane_x2, draw_y), (lane_x2, draw_y + 25), width=2)

        for pt in self.particles: pt.draw(surface)
        for p in self.pickups: p.draw(surface)
        for t in self.traffic: t.draw(surface)
        if self.state != "GAMEOVER": self.player.draw(surface)

        if self.state == "PLAYING":
            # HUD Elements
            pygame.draw.rect(surface, (40, 40, 50), (20, 20, 180, 18), border_radius=4)
            pygame.draw.rect(surface, (46, 204, 113), (20, 20, int(180 * (max(0, self.player.health) / 100)), 18), border_radius=4)
            surface.blit(font_ui.render("HULL STRENGTH", True, TEXT_COLOR), (20, 42))

            pygame.draw.rect(surface, (40, 40, 50), (20, 75, 180, 18), border_radius=4)
            pygame.draw.rect(surface, NITRO_COLOR, (20, 75, int(180 * (self.player.nitro / 100)), 18), border_radius=4)
            surface.blit(font_ui.render("NITRO BOOST [SPACE]", True, TEXT_COLOR), (20, 97))

            surface.blit(font_ui.render(f"SCORE: {self.score:,}", True, TEXT_COLOR), (WIDTH - 220, 20))
            surface.blit(font_ui.render(f"DISTANCE: {int(self.distance)}m", True, GOLD_COLOR), (WIDTH - 220, 50))
            surface.blit(font_ui.render(f"MULT: {self.multiplier:.1f}x", True, BORDER_COLOR), (WIDTH - 220, 80))
            
        elif self.state == "START":
            title = font_large.render("NEON APEX: NIGHT DRIVE", True, BORDER_COLOR)
            team = font_sub.render("Developed by Pixel Racers", True, PLAYER_COLOR)
            prompt = font_ui.render("Press [ENTER] or [SPACE] to Launch Engine", True, TEXT_COLOR)
            surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 220))
            surface.blit(team, (WIDTH // 2 - team.get_width() // 2, 290))
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 400))

        elif self.state == "GAMEOVER":
            title = font_large.render("CRASH DETECTED", True, BORDER_COLOR)
            score_txt = font_sub.render(f"Final Score: {self.score:,}  |  Distance: {int(self.distance)}m", True, TEXT_COLOR)
            prompt = font_ui.render("Press [ENTER] to Restart Session", True, GOLD_COLOR)
            surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 220))
            surface.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 300))
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 380))

def main():
    game = GameEngine()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game.state in ["START", "GAMEOVER"] and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    game.reset()
        game.update()
        game.render(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
