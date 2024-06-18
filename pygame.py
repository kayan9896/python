import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Set the screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the title of the window
pygame.display.set_caption("Snake Game")

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Define the snake's starting position and direction
snake_x = SCREEN_WIDTH / 2
snake_y = SCREEN_HEIGHT / 2
snake_direction = "right"

# Define the snake's body
snake_body = [(snake_x, snake_y)]

# Define the food's position
food_x = random.randint(0, SCREEN_WIDTH - 1)
food_y = random.randint(0, SCREEN_HEIGHT - 1)

# Initial speed
speed = 100

# Initial score
score = 0

# Font for the score
font = pygame.font.Font(None, 36)

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake_direction = "up"
            elif event.key == pygame.K_DOWN:
                snake_direction = "down"
            elif event.key == pygame.K_LEFT:
                snake_direction = "left"
            elif event.key == pygame.K_RIGHT:
                snake_direction = "right"
            elif event.key == pygame.K_EQUALS:  # "+" key to increase speed
                speed -= 10
            elif event.key == pygame.K_MINUS:  # "-" key to decrease speed
                speed += 10

    # Move the snake
    if snake_direction == "up":
        snake_y -= 1
    elif snake_direction == "down":
        snake_y += 1
    elif snake_direction == "left":
        snake_x -= 1
    elif snake_direction == "right":
        snake_x += 1

    # Check if the snake has collided with the food
    if snake_x == food_x and snake_y == food_y:
        # Add a new segment to the snake's body
        snake_body.append((snake_x, snake_y))
        # Generate new food
        food_x = random.randint(0, SCREEN_WIDTH - 1)
        food_y = random.randint(0, SCREEN_HEIGHT - 1)
        # Increase the length of the snake by 5%
        snake_body.extend([(snake_x, snake_y)] * int(len(snake_body) * 0.05))

    # Check if the snake has collided with the wall
    if snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT:
        # Game over!
        print("Game over!")
        pygame.quit()
        sys.exit()

    # Update the display
    screen.fill(BLACK)  # Clear the screen
    pygame.draw.rect(screen, WHITE, (snake_x, snake_y, 10, 10))  # Draw the snake
    pygame.draw.rect(screen, RED, (food_x, food_y, 10, 10))  # Draw the food

    # Draw the score
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 150, 10))

    # Draw the speed controls
    text = font.render("+", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 50, 50))
    text = font.render("-", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 50, 100))
    text = font.render("Speed", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 100, 75))

    pygame.display.flip()  # Flip the display

    # Cap the frame rate
    pygame.time.delay(speed)

    # Increase the score
    score += 1
