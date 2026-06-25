import pygame
import os

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# rgb (Cyberpunk Neon Palette)
RED = (255, 0, 120)       # Neon Pink/Red for Player 1
WHITE = (0, 240, 255)     # Neon Cyan/Blue for Player 2
BLUE = (0, 255, 150)      # Neon Mint Green for Valid Moves
BLACK = (10, 10, 18)      # Dark space background
GREY = (45, 45, 65)       # Outline color
GOLD = (255, 215, 0)      # Victory gold

CROWN = None
if os.path.exists('assets/crown.png'):
    CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))
elif os.path.exists('../assets/crown.png'):
    CROWN = pygame.transform.scale(pygame.image.load('../assets/crown.png'), (44, 25))