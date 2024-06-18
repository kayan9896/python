import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.SysFont('Arial', 20)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the music
music_dir = 'path_to_your_music_directory'
music_files = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
current_song = 0
shuffle = False
playing = False

# Function to play the next song
def play_next():
    global current_song
    if shuffle:
        current_song = random.choice([i for i, song in enumerate(music_files) if i != current_song])
    else:
        current_song = (current_song + 1) % len(music_files)
    pygame.mixer.music.load(os.path.join(music_dir, music_files[current_song]))
    pygame.mixer.music.play()
    update_text()

# Function to update the text on the screen
def update_text():
    screen.fill(BLACK)
    text = FONT.render(music_files[current_song], True, WHITE)
    screen.blit(text, (10, 10))
    if shuffle:
        text = FONT.render('Shuffle: On', True, WHITE)
    else:
        text = FONT.render('Shuffle: Off', True, WHITE)
    screen.blit(text, (10, 30))
    if playing:
        text = FONT.render('Playing', True, WHITE)
    else:
        text = FONT.render('Paused', True, WHITE)
    screen.blit(text, (10, 50))
    pygame.display.flip()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if playing:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                playing = not playing
                update_text()
            elif event.key == pygame.K_RIGHT:
                play_next()
            elif event.key == pygame.K_s:
                shuffle = not shuffle
                update_text()

    # Start playing music if it's not already playing
    if not pygame.mixer.music.get_busy() and playing:
        play_next()

# Quit Pygame
pygame.quit()
