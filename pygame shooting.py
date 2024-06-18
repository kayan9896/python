import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
PLAYER_SIZE = 50
BULLET_SIZE = 10
ENEMY_SIZE = 50
FPS = 60
PLAYER_SPEED = 5
BULLET_FIRING_RATE = 200 # Milliseconds between shots
SCORE_FONT_SIZE = 36

# Set up some colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the player
player = pygame.Rect(WIDTH / 2, HEIGHT - PLAYER_SIZE * 2, PLAYER_SIZE, PLAYER_SIZE)

# Set up the bullets
bullets = []
last_bullet_time = 0

# Set up the enemies
enemies = [pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), random.randint(-HEIGHT, 0), ENEMY_SIZE, ENEMY_SIZE) for _ in range(10)]

# Set up the game state
state = "main_menu"
score = 0

# Set up the clock
clock = pygame.time.Clock()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if state == "main_menu":
                    state = "game"
                elif state == "game_over":
                    state = "game"
                    player = pygame.Rect(WIDTH / 2, HEIGHT - PLAYER_SIZE * 2, PLAYER_SIZE, PLAYER_SIZE)
                    bullets = []
                    enemies = [pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), random.randint(-HEIGHT, 0), ENEMY_SIZE, ENEMY_SIZE) for _ in range(10)]
                    score = 0
            elif event.key == pygame.K_ESCAPE:
                if state == "game_over":
                    state = "main_menu"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "game" and len(bullets) < 5 and pygame.time.get_ticks() - last_bullet_time > BULLET_FIRING_RATE:
                bullets.append(pygame.Rect(player.centerx, player.top, BULLET_SIZE, BULLET_SIZE))
                last_bullet_time = pygame.time.get_ticks()

    # Game logic
    if state == "game":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED

        # Ensure the player doesn't move off the screen
        if player.x < 0:
            player.x = 0
        elif player.x > WIDTH - PLAYER_SIZE:
            player.x = WIDTH - PLAYER_SIZE

        for bullet in bullets:
            bullet.y -= 5
            if bullet.y < 0:
                bullets.remove(bullet)

        for enemy in enemies:
            enemy.y += 2
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                enemies.append(pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), random.randint(-HEIGHT, 0), ENEMY_SIZE, ENEMY_SIZE))

        for bullet in bullets:
            for enemy in enemies:
                if bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    enemies.append(pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), random.randint(-HEIGHT, 0), ENEMY_SIZE, ENEMY_SIZE))
                    score += 1

        for enemy in enemies:
            if player.colliderect(enemy):
                state = "game_over"
                player = pygame.Rect(WIDTH / 2, HEIGHT - PLAYER_SIZE * 2, PLAYER_SIZE, PLAYER_SIZE)

    # Draw everything
    screen.fill((0, 0, 0))
    if state == "main_menu":
        font = pygame.font.Font(None, SCORE_FONT_SIZE)
        text = font.render("Press space to start", True, WHITE)
        screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))
    elif state == "game":
        pygame.draw.rect(screen, WHITE, player)
        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, bullet)
        for enemy in enemies:
            pygame.draw.rect(screen, RED, enemy)
        font = pygame.font.Font(None, SCORE_FONT_SIZE)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))
    elif state == "game_over":
        font = pygame.font.Font(None, SCORE_FONT_SIZE)
        text = font.render(f"You died! Your score was {score}. Press space to restart or escape to go back to main menu.", True, WHITE)
        screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

