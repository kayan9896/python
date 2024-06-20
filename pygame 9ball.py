import pygame
import math

# Initialize Pygame
pygame.init()

# Define some colors
WHITE = (255, 255, 255)
BROWN = (102, 51, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Set up some constants
WIDTH, HEIGHT = 800, 400
EDGE_WIDTH = 20
POCKET_RADIUS = 15
DIAMOND_SIZE = 5

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_arc(x, y, radius, start_angle, end_angle, color):
    pygame.draw.arc(screen, color, (x, y, radius * 2, radius * 2), start_angle, end_angle, 3)

# Function to draw a diamond
def draw_diamond(x, y, size, color):
    pygame.draw.polygon(screen, color, [(x, y-size), (x+size, y), (x, y+size), (x-size, y)])

# Function to draw the pool table
def draw_pool_table():
    # Draw the blue surface
    screen.fill(BLUE)

    # Draw the edges
    pygame.draw.rect(screen, BROWN, (0, 0, WIDTH, EDGE_WIDTH))
    pygame.draw.rect(screen, BROWN, (0, HEIGHT-EDGE_WIDTH, WIDTH, EDGE_WIDTH))
    pygame.draw.rect(screen, BROWN, (0, 0, EDGE_WIDTH, HEIGHT))
    pygame.draw.rect(screen, BROWN, (WIDTH-EDGE_WIDTH, 0, EDGE_WIDTH, HEIGHT))

    # Draw the pockets
    draw_arc(0, 0, POCKET_RADIUS, 3*math.pi / 2, 0, BLACK)  # Top-left corner
    draw_arc(WIDTH-POCKET_RADIUS*2, 0, POCKET_RADIUS, math.pi, 3*math.pi/2, BLACK)  # Top-right corner
    draw_arc(0, HEIGHT - POCKET_RADIUS*2, POCKET_RADIUS, 0, math.pi / 2, BLACK)  # Bottom-left corner
    draw_arc(WIDTH - POCKET_RADIUS*2, HEIGHT - POCKET_RADIUS*2, POCKET_RADIUS, math.pi / 2, math.pi , BLACK)  # Bottom-right corner
    draw_arc(WIDTH / 2 - POCKET_RADIUS*2, 0, POCKET_RADIUS, math.pi, 0, BLACK)  # Top center
    draw_arc(WIDTH / 2 - POCKET_RADIUS*2, HEIGHT - POCKET_RADIUS*2, POCKET_RADIUS, 0, math.pi, BLACK)  # Bottom center


    # Draw the diamond spots
    for i in range(3):
        draw_diamond(EDGE_WIDTH/2 + (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)
        draw_diamond(WIDTH - EDGE_WIDTH/2 - (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)

        draw_diamond(EDGE_WIDTH/2 + (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), HEIGHT - EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)
        draw_diamond(WIDTH - EDGE_WIDTH/2 - (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), HEIGHT - EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)
        draw_diamond(EDGE_WIDTH/2, EDGE_WIDTH/2 + (HEIGHT-EDGE_WIDTH*2)/4 * (i+1), DIAMOND_SIZE, WHITE)
        draw_diamond(WIDTH-EDGE_WIDTH/2, EDGE_WIDTH/2 + (HEIGHT-EDGE_WIDTH*2)/4 * (i+1), DIAMOND_SIZE, WHITE)

    
    # Draw the head string
    pygame.draw.line(screen, WHITE, (int(EDGE_WIDTH + (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2), EDGE_WIDTH), (int(EDGE_WIDTH + (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2), HEIGHT - EDGE_WIDTH), 2)

    # Draw the foot spot
    pygame.draw.circle(screen, WHITE, (int(WIDTH - EDGE_WIDTH - (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2), int(HEIGHT/2)), DIAMOND_SIZE)
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_pool_table()

    pygame.display.flip()

pygame.quit()
