import pygame
import subprocess
import os
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 150, 255)
HOVER_BLUE = (100, 180, 255)

FONT = pygame.font.SysFont("comicsans", 30)
TITLE_FONT = pygame.font.SysFont("comicsans", 50, bold=True)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Dashboard")

GAMES = [
    {"name": "2048", "path": "2048/main.py", "dir": "2048"},
    {"name": "Car Racing", "path": "Car_Racing/main.py", "dir": "Car_Racing"},
    {"name": "Checkers", "path": "checkers/main.py", "dir": "checkers"},
    {"name": "Galaxy Fight", "path": "Galaxy_Fight/main.py", "dir": "Galaxy_Fight"},
    {"name": "Platformer", "path": "Platformer/main.py", "dir": "Platformer"},
    {"name": "Pong", "path": "pong/main.py", "dir": "pong"},
    {"name": "Space Dodge", "path": "Space_Dodge/main.py", "dir": "Space_Dodge"},
    {"name": "Space Invader", "path": "Space_invader/main.py", "dir": "Space_invader"},
    {"name": "Snake", "path": "snake/main.py", "dir": "snake"},
]

def draw_button(rect, text, is_hovered):
    color = HOVER_BLUE if is_hovered else BLUE
    pygame.draw.rect(WIN, color, rect, border_radius=10)
    pygame.draw.rect(WIN, BLACK, rect, 2, border_radius=10)
    
    text_surface = FONT.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    WIN.blit(text_surface, text_rect)

def draw_background():
    WIN.fill((30, 30, 40)) # Dark blue-grey background
    # Draw simple grid pattern
    for i in range(0, WIDTH, 40):
        pygame.draw.line(WIN, (40, 40, 50), (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pygame.draw.line(WIN, (40, 40, 50), (0, i), (WIDTH, i))

def main():
    run = True
    clock = pygame.time.Clock()

    # Calculate button positions
    button_width = 210
    button_height = 55
    padding = 25
    cols = 3
    
    start_x = (WIDTH - (cols * button_width + (cols - 1) * padding)) // 2
    start_y = 170

    buttons = []
    for i, game in enumerate(GAMES):
        row = i // cols
        col = i % cols
        x = start_x + col * (button_width + padding)
        y = start_y + row * (button_height + padding)
        buttons.append({"rect": pygame.Rect(x, y, button_width, button_height), "game": game})

    while run:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        draw_background()
        
        title_surface = TITLE_FONT.render("PyGame Collection", True, WHITE)
        # Simple shadow for title
        title_shadow = TITLE_FONT.render("PyGame Collection", True, BLACK)
        WIN.blit(title_shadow, (WIDTH // 2 - title_surface.get_width() // 2 + 3, 53))
        WIN.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))

        for button in buttons:
            is_hovered = button["rect"].collidepoint(mouse_pos)
            draw_button(button["rect"], button["game"]["name"], is_hovered)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        # Launch game
                        game = button["game"]
                        print(f"Launching {game['name']}...")
                        # Run as a separate process to avoid conflicts
                        # Use sys.executable to ensure the same environment is used
                        subprocess.Popen([sys.executable, os.path.basename(game["path"])], cwd=game["dir"])

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
