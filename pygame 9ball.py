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

    # Calculate offset based on radius
    pocket_radius = POCKET_RADIUS
    offset = pocket_radius / math.sqrt(2)

    # Draw the pockets
    # For each corner pocket, start from inner edge intersection and offset the center

    # Top-left corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (EDGE_WIDTH + offset, EDGE_WIDTH + offset), 
                      pocket_radius)

    # Top-right corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (WIDTH - EDGE_WIDTH - offset, EDGE_WIDTH + offset), 
                      pocket_radius)

    # Bottom-left corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (EDGE_WIDTH + offset, HEIGHT - EDGE_WIDTH - offset), 
                      pocket_radius)

    # Bottom-right corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (WIDTH - EDGE_WIDTH - offset, HEIGHT - EDGE_WIDTH - offset), 
                      pocket_radius)

    # Top middle pocket
    pygame.draw.circle(screen, BLACK, (WIDTH // 2, EDGE_WIDTH), pocket_radius)

    # Bottom middle pocket
    pygame.draw.circle(screen, BLACK, (WIDTH // 2, HEIGHT - EDGE_WIDTH), pocket_radius)


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
