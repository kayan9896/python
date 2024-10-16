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

    # Buffer color (slightly lighter blue to represent a raised surface)
    BUFFER_COLOR = (0, 0, 220)  # Slightly darker blue for the buffer border
    BUFFER_INNER_COLOR = BLUE   # Same as table surface

    # Calculate offset based on radius
    pocket_radius = POCKET_RADIUS
    offset = pocket_radius / math.sqrt(2)

    # Buffer height (same as pocket radius)
    buffer_height = pocket_radius

    # Function to draw a buffer
    def draw_buffer(start_x, start_y, length, is_vertical=False, is_top=False):
        if is_vertical:
            if is_top:
                # Top vertical buffer points
                points = [
                    (start_x, start_y + pocket_radius/2),  # Top left
                    (start_x + buffer_height, start_y + pocket_radius),  # Top right
                    (start_x + buffer_height, start_y + length - pocket_radius),  # Bottom right
                    (start_x, start_y + length - pocket_radius/2)  # Bottom left
                ]
            else:
                # Bottom vertical buffer points
                points = [
                    (start_x - buffer_height, start_y + pocket_radius),  # Top left
                    (start_x, start_y + pocket_radius/2),  # Top right
                    (start_x, start_y + length - pocket_radius/2),  # Bottom right
                    (start_x - buffer_height, start_y + length - pocket_radius)  # Bottom left
                ]
        else:
            if is_top:
                # Top horizontal buffer points
                points = [
                    (start_x + pocket_radius/2, start_y),  # Top left
                    (start_x + pocket_radius, start_y + buffer_height),  # Bottom left
                    (start_x + length - pocket_radius, start_y + buffer_height),  # Bottom right
                    (start_x + length - pocket_radius/2, start_y)  # Top right
                ]
            else:
                # Bottom horizontal buffer points
                points = [
                    (start_x + pocket_radius, start_y - buffer_height),  # Top left
                    (start_x + pocket_radius/2, start_y),  # Bottom left
                    (start_x + length - pocket_radius/2, start_y),  # Bottom right
                    (start_x + length - pocket_radius, start_y - buffer_height)  # Top right
                ]

        # Draw buffer border
        pygame.draw.polygon(screen, BUFFER_COLOR, points)

        # Draw buffer inner surface
        if is_vertical:
            if is_top:
                inner_points = [
                    (start_x + 1, start_y + pocket_radius/2 + 1),
                    (start_x + buffer_height - 1, start_y + pocket_radius + 1),
                    (start_x + buffer_height - 1, start_y + length - pocket_radius - 1),
                    (start_x + 1, start_y + length - pocket_radius/2 - 1)
                ]
            else:
                inner_points = [
                    (start_x - buffer_height + 1, start_y + pocket_radius + 1),
                    (start_x - 1, start_y + pocket_radius/2 + 1),
                    (start_x - 1, start_y + length - pocket_radius/2 - 1),
                    (start_x - buffer_height + 1, start_y + length - pocket_radius - 1)
                ]
        else:
            if is_top:
                inner_points = [
                    (start_x + pocket_radius/2 + 1, start_y + 1),
                    (start_x + pocket_radius + 1, start_y + buffer_height - 1),
                    (start_x + length - pocket_radius - 1, start_y + buffer_height - 1),
                    (start_x + length - pocket_radius/2 - 1, start_y + 1)
                ]
            else:
                inner_points = [
                    (start_x + pocket_radius + 1, start_y - buffer_height + 1),
                    (start_x + pocket_radius/2 + 1, start_y - 1),
                    (start_x + length - pocket_radius/2 - 1, start_y - 1),
                    (start_x + length - pocket_radius - 1, start_y - buffer_height + 1)
                ]
        pygame.draw.polygon(screen, BUFFER_INNER_COLOR, inner_points)

    # Draw buffers for top edge
    draw_buffer(EDGE_WIDTH + offset + pocket_radius, EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - 2*pocket_radius), is_top=True)
    draw_buffer(WIDTH/2 + offset + pocket_radius, EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - 2*pocket_radius), is_top=True)

    # Draw buffers for bottom edge
    draw_buffer(EDGE_WIDTH + offset + pocket_radius, HEIGHT - EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - 2*pocket_radius))
    draw_buffer(WIDTH/2 + offset + pocket_radius, HEIGHT - EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - 2*pocket_radius))

    # Draw buffers for left edge
    draw_buffer(EDGE_WIDTH, EDGE_WIDTH + offset + pocket_radius, 
                (HEIGHT - 2*EDGE_WIDTH - 2*offset - 2*pocket_radius), is_vertical=True, is_top=True)

    # Draw buffers for right edge
    draw_buffer(WIDTH - EDGE_WIDTH, EDGE_WIDTH + offset + pocket_radius, 
                (HEIGHT - 2*EDGE_WIDTH - 2*offset - 2*pocket_radius), is_vertical=True)

    
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
