
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Player
player = pygame.Rect(WIDTH // 2, HEIGHT // 2, 20, 20)
player_speed = 5
player_angle = 0
player_power = 1
player_health = 100
player_weapon = "single"

# Bullets
bullets = []
bullet_speed = 10
bullet_cooldown = 0

# Enemies
enemies = []
enemy_spawn_timer = 0
enemy_spawn_delay = 120  # Increased delay between enemy spawns

# Game variables
score = 0
kills = 0

# Clock for controlling the frame rate
clock = pygame.time.Clock()

def rotate_ship(rect, angle, color):
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.polygon(surface, color, [(0, 20), (10, 0), (20, 20)])
    return pygame.transform.rotate(surface, -angle)

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    enemy_type = random.choice(["rock", "rock", "alien"])
    if enemy_type == "rock":
        size = random.randint(20, 30)  # Reduced rock size
        health = size // 4  # Reduced rock health
        color = random.choice([WHITE, BLUE, GREEN, YELLOW])
    else:
        size = 20
        health = 20  # Reduced alien health
        color = RED

    if side == "top":
        rect = pygame.Rect(random.randint(0, WIDTH), -size, size, size)
    elif side == "bottom":
        rect = pygame.Rect(random.randint(0, WIDTH), HEIGHT + size, size, size)
    elif side == "left":
        rect = pygame.Rect(-size, random.randint(0, HEIGHT), size, size)
    else:
        rect = pygame.Rect(WIDTH + size, random.randint(0, HEIGHT), size, size)

    return {"rect": rect, "type": enemy_type, "health": health, "max_health": health, "color": color, "angle": random.randint(0, 360)}

# Game loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                # Reset game
                player = pygame.Rect(WIDTH // 2, HEIGHT // 2, 20, 20)
                player_angle = 0
                player_power = 1
                player_health = 100
                player_weapon = "single"
                bullets = []
                enemies = []
                score = 0
                kills = 0
                game_over = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:  # Swapped left and right rotation
            player_angle += 2
        if keys[pygame.K_LEFT]:
            player_angle -= 2
        if keys[pygame.K_UP]:
            player.x += math.sin(math.radians(player_angle)) * player_speed
            player.y -= math.cos(math.radians(player_angle)) * player_speed
        if keys[pygame.K_DOWN]:
            player.x -= math.sin(math.radians(player_angle)) * player_speed
            player.y += math.cos(math.radians(player_angle)) * player_speed
        if keys[pygame.K_LCTRL] and bullet_cooldown <= 0:
            angle_rad = math.radians(player_angle)
            if player_weapon == "single":
                bullets.append([
                    player.centerx + 20 * math.sin(angle_rad),
                    player.centery - 20 * math.cos(angle_rad),
                    math.sin(angle_rad) * bullet_speed,
                    -math.cos(angle_rad) * bullet_speed
                ])
            elif player_weapon == "triple":
                bullets.append([
                    player.centerx + 20 * math.sin(angle_rad),
                    player.centery - 20 * math.cos(angle_rad),
                    math.sin(angle_rad) * bullet_speed,
                    -math.cos(angle_rad) * bullet_speed
                ])
                bullets.append([
                    player.centerx + 20 * math.sin(angle_rad + math.pi / 8),
                    player.centery - 20 * math.cos(angle_rad + math.pi / 8),
                    math.sin(angle_rad + math.pi / 8) * bullet_speed,
                    -math.cos(angle_rad + math.pi / 8) * bullet_speed
                ])
                bullets.append([
                    player.centerx + 20 * math.sin(angle_rad - math.pi / 8),
                    player.centery - 20 * math.cos(angle_rad - math.pi / 8),
                    math.sin(angle_rad - math.pi / 8) * bullet_speed,
                    -math.cos(angle_rad - math.pi / 8) * bullet_speed
                ])
            elif player_weapon == "homing":
                for enemy in enemies:
                    direction = (enemy["rect"].centerx - player.centerx, enemy["rect"].centery - player.centery)
                    length = math.hypot(*direction)
                    if length != 0:
                        direction = (direction[0] / length, direction[1] / length)
                    bullets.append([
                        player.centerx + 20 * math.sin(angle_rad),
                        player.centery - 20 * math.cos(angle_rad),
                        direction[0] * bullet_speed,
                        direction[1] * bullet_speed
                    ])
            bullet_cooldown = 10

        bullet_cooldown -= 1

        # Keep player on screen
        player.clamp_ip(screen.get_rect())
        if player.left < 0:
            player.right = WIDTH
        elif player.right > WIDTH:
            player.left = 0
        if player.top < 0:
            player.bottom = HEIGHT
        elif player.bottom > HEIGHT:
            player.top = 0

        # Update bullets
        for bullet in bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if not screen.get_rect().collidepoint(bullet[0], bullet[1]):
                bullets.remove(bullet)

        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemies.append(spawn_enemy())
            enemy_spawn_timer = 0

        # Update enemies
        for enemy in enemies[:]:
            if enemy["type"] == "rock":
                speed = 1
            else:
                speed = 1.5  # Reduced alien speed

            direction = (player.centerx - enemy["rect"].centerx, player.centery - enemy["rect"].centery)
            length = math.hypot(*direction)
            if length != 0:
                direction = (direction[0] / length, direction[1] / length)

            enemy["rect"].x += direction[0] * speed
            enemy["rect"].y += direction[1] * speed

            if enemy["type"] == "alien":
                enemy["angle"] = math.degrees(math.atan2(-direction[1], direction[0])) - 90
                if random.random() < 0.02:
                    angle_rad = math.radians(enemy["angle"])
                    bullets.append([
                        enemy["rect"].centerx + 20 * math.sin(angle_rad),
                        enemy["rect"].centery - 20 * math.cos(angle_rad),
                        math.sin(angle_rad) * bullet_speed,
                        -math.cos(angle_rad) * bullet_speed
                    ])

            # Check collision with player
            if enemy["rect"].colliderect(player):
                player_health -= 10
                enemies.remove(enemy)
                if player_health <= 0:
                    game_over = True

            # Check collision with bullets
            for bullet in bullets[:]:
                if enemy["rect"].collidepoint(bullet[0], bullet[1]):
                    enemy["health"] -= player_power
                    bullets.remove(bullet)
                    if enemy["health"] <= 0:
                        if enemy["type"] == "rock" and enemy["rect"].width > 20:
                            for _ in range(2):
                                new_enemy = spawn_enemy()
                                new_enemy["rect"].center = enemy["rect"].center
                                new_enemy["rect"].width = new_enemy["rect"].height = enemy["rect"].width // 2
                                new_enemy["health"] = new_enemy["rect"].width // 4
                                new_enemy["max_health"] = new_enemy["health"]
                                new_enemy["color"] = enemy["color"]
                                enemies.append(new_enemy)
                        enemies.remove(enemy)
                        score += 10
                        kills += 1
                        if kills % 10 == 0:
                            if player_weapon == "single":
                                player_weapon = "triple"
                            elif player_weapon == "triple":
                                player_weapon = "homing"
                    break

        # Clear the screen
        screen.fill(BLACK)

        # Draw player
        rotated_player = rotate_ship(player, player_angle, WHITE)
        screen.blit(rotated_player, player.topleft)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), 3)

        # Draw enemies
        for enemy in enemies:
            if enemy["type"] == "rock":
                pygame.draw.rect(screen, enemy["color"], enemy["rect"])
                health_bar_width = enemy["rect"].width * (enemy["health"] / enemy["max_health"])
                health_bar = pygame.Rect(enemy["rect"].x, enemy["rect"].y - 10, health_bar_width, 5)
                pygame.draw.rect(screen, RED, health_bar)
            else:
                rotated_enemy = rotate_ship(enemy["rect"], enemy["angle"], RED)
                screen.blit(rotated_enemy, enemy["rect"].topleft)
                health_bar_width = 20 * (enemy["health"] / enemy["max_health"])
                health_bar = pygame.Rect(enemy["rect"].x, enemy["rect"].y - 10, health_bar_width, 5)
                pygame.draw.rect(screen, RED, health_bar)

        # Draw HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        power_text = font.render(f"Power: {player_power}", True, WHITE)
        screen.blit(power_text, (10, 50))

        health_bar_width = 200 * (player_health / 100)
        health_bar = pygame.Rect(10, HEIGHT - 30, health_bar_width, 20)
        pygame.draw.rect(screen, RED, health_bar)
        health_text = font.render(f"Health: {player_health}", True, WHITE)
        screen.blit(health_text, (220, HEIGHT - 25))

    else:
        # Game over screen
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        kills_text = font.render(f"Enemies Destroyed: {kills}", True, WHITE)
        screen.blit(kills_text, (WIDTH // 2 - kills_text.get_width() // 2, HEIGHT // 2 + 40))
        power_text = font.render(f"Final Weapon: {player_weapon.upper()}", True, WHITE)
        screen.blit(power_text, (WIDTH // 2 - power_text.get_width() // 2, HEIGHT // 2 + 80))

        restart_text = font.render("Press SPACE to restart", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 160))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
