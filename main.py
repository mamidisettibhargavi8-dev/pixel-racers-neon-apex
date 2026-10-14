import pygame
import sys
import random
from config import *
from player import Player, Particle
from entities import TrafficVehicle, PickupItem

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Racers - Neon Apex: Night Drive")
    clock = pygame.time.Clock()

    # Road layout
    road_width = 380
    road_left = (WIDTH - road_width) // 2
    road_right = road_left + road_width
    
    # Game States: "START", "PLAYING", "LEVEL_CLEAR", "VICTORY", "GAMEOVER"
    state = "START"
    
    # Campaign variables
    level = 1
    max_levels = 3
    score = 0
    distance = 0.0
    track_length = 2000.0  # Meters to reach the finish line for each level!
    road_scroll = 0.0

    player = Player(WIDTH // 2 - 20, HEIGHT - 150)
    traffic = []
    pickups = []
    particles = []

    def start_level(lvl):
        nonlocal distance, road_scroll, traffic, pickups, particles, player, track_length
        distance = 0.0
        road_scroll = 0.0
        traffic.clear()
        pickups.clear()
        particles.clear()
        player = Player(WIDTH // 2 - 20, HEIGHT - 150)
        # Each level gets longer and more intense!
        track_length = 2000.0 + (lvl - 1) * 1000.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if state == "START" and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    level = 1
                    score = 0
                    start_level(level)
                    state = "PLAYING"
                elif state == "LEVEL_CLEAR" and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    level += 1
                    if level > max_levels:
                        state = "VICTORY"
                    else:
                        start_level(level)
                        state = "PLAYING"
                elif state in ["GAMEOVER", "VICTORY"] and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    state = "START"

        if state == "PLAYING":
            # Speed scales dynamically based on level intensity
            base_speed = 5.0 + (level * 1.2) + (distance / 1000.0)
            game_speed = base_speed * 1.5 if player.is_boosting else base_speed

            distance += game_speed * 0.1
            score += int(10 * level)
            road_scroll = (road_scroll + game_speed) % 60

            player.update(road_left, road_right, particles)

            # Check if player reached the finish line!
            if distance >= track_length:
                state = "LEVEL_CLEAR"

            # Spawning traffic (higher levels = denser traffic)
            spawn_rate = 0.025 + (level * 0.01)
            if len(traffic) < (3 + level) and random.random() < spawn_rate:
                traffic.append(TrafficVehicle(road_left, road_right))

            # Spawning pickups
            if len(pickups) < 2 and random.random() < 0.015:
                p_type = "NITRO" if random.random() < 0.6 else "SCORE"
                pickups.append(PickupItem(road_left, road_right, p_type))

            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

            # Traffic Collisions
            for t in traffic[:]:
                t.update(game_speed + level) # Traffic moves faster in higher levels
                t_rect = pygame.Rect(t.x, t.y, t.width, t.height)
                
                if player_rect.colliderect(t_rect):
                    player.health -= 35
                    for _ in range(12):
                        particles.append(Particle(
                            player_rect.centerx, player_rect.centery,
                            BORDER_COLOR, random.uniform(-4, 4), random.uniform(-4, 4), random.uniform(3, 6), 20
                        ))
                    traffic.remove(t)
                    if player.health <= 0:
                        state = "GAMEOVER"
                elif t.y > HEIGHT + 50:
                    traffic.remove(t)

            # Pickups collection
            for p in pickups[:]:
                p.update(game_speed)
                dist_to_p = ((player.x + player.width/2 - p.x)**2 + (player.y + player.height/2 - p.y)**2)**0.5
                if dist_to_p < (p.radius + 20):
                    if p.item_type == "NITRO":
                        player.nitro = min(100.0, player.nitro + 35.0)
                    elif p.item_type == "SCORE":
                        score += 500
                    pickups.remove(p)
                elif p.y > HEIGHT + 50:
                    pickups.remove(p)

            for pt in particles[:]:
                pt.update()
                if pt.lifetime <= 0:
                    particles.remove(pt)

        # --- RENDERING ---
        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, ROAD_COLOR, (road_left, 0, road_width, HEIGHT))
        pygame.draw.line(screen, BORDER_COLOR, (road_left, 0), (road_left, HEIGHT), width=4)
        pygame.draw.line(screen, BORDER_COLOR, (road_right, 0), (road_right, HEIGHT), width=4)

        lane_x1 = road_left + road_width // 3
        lane_x2 = road_left + (2 * road_width) // 3
        for y in range(-60, HEIGHT + 60, 50):
            draw_y = y + int(road_scroll)
            pygame.draw.line(screen, (70, 70, 90), (lane_x1, draw_y), (lane_x1, draw_y + 25), width=2)
            pygame.draw.line(screen, (70, 70, 90), (lane_x2, draw_y), (lane_x2, draw_y + 25), width=2)

        for pt in particles: pt.draw(screen)
        for p in pickups: p.draw(screen)
        for t in traffic: t.draw(screen)
        
        if state in ["PLAYING", "LEVEL_CLEAR"]:
            player.draw(screen)

        # --- HUD & SCREENS ---
        if state == "PLAYING":
            # Hull Health Bar
            pygame.draw.rect(screen, (40, 40, 50), (20, 20, 160, 16), border_radius=4)
            pygame.draw.rect(screen, (46, 204, 113), (20, 20, int(160 * (max(0, player.health) / 100)), 16), border_radius=4)
            screen.blit(font_ui.render("HULL", True, TEXT_COLOR), (20, 40))

            # Nitro Bar
            pygame.draw.rect(screen, (40, 40, 50), (20, 70, 160, 16), border_radius=4)
            pygame.draw.rect(screen, NITRO_COLOR, (20, 70, int(160 * (player.nitro / 100)), 16), border_radius=4)
            screen.blit(font_ui.render("NITRO [SPACE]", True, TEXT_COLOR), (20, 90))

            # Progress / Finish Line Bar
            progress = min(1.0, distance / track_length)
            pygame.draw.rect(screen, (40, 40, 50), (WIDTH - 230, 110, 200, 12), border_radius=4)
            pygame.draw.rect(screen, GOLD_COLOR, (WIDTH - 230, 110, int(200 * progress), 12), border_radius=4)
            
            screen.blit(font_ui.render(f"SCORE: {score:,}", True, TEXT_COLOR), (WIDTH - 230, 20))
            screen.blit(font_ui.render(f"LEVEL: {level} / {max_levels}", True, PLAYER_COLOR), (WIDTH - 230, 50))
            screen.blit(font_ui.render(f"FINISH LINE: {int(track_length - distance)}m", True, GOLD_COLOR), (WIDTH - 230, 80))

        elif state == "START":
            title = font_large.render("NEON APEX: NIGHT DRIVE", True, BORDER_COLOR)
            sub = font_sub.render("Reach the Finish Line Across 3 Intensifying Sectors!", True, PLAYER_COLOR)
            prompt = font_ui.render("Press [ENTER] or [SPACE] to Start Racing", True, TEXT_COLOR)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 270))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 380))

        elif state == "LEVEL_CLEAR":
            title = font_large.render(f"SECTOR {level} CLEARED!", True, GOLD_COLOR)
            sub = font_sub.render("Get ready for heavier traffic and higher speeds...", True, TEXT_COLOR)
            prompt = font_ui.render("Press [ENTER] for Next Sector", True, PLAYER_COLOR)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 220))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 380))

        elif state == "VICTORY":
            title = font_large.render("MISSION ACCOMPLISHED", True, GOLD_COLOR)
            score_txt = font_sub.render(f"Final Championship Score: {score:,}", True, TEXT_COLOR)
            prompt = font_ui.render("Press [ENTER] to Return to Menu", True, PLAYER_COLOR)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 220))
            screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 300))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 380))

        elif state == "GAMEOVER":
            title = font_large.render("CRASH DETECTED", True, BORDER_COLOR)
            score_txt = font_sub.render(f"Score Reached: {score:,} | Sector {level}", True, TEXT_COLOR)
            prompt = font_ui.render("Press [ENTER] to Try Again", True, GOLD_COLOR)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 220))
            screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 300))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 380))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
