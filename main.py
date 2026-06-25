import pygame
import subprocess
import os
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 950, 680
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Retro-Modern Cabinet Arcade")

# Colors (Arcade Neon Palette)
DARK_BG = (8, 8, 16)
GRID_LINE_COLOR = (18, 18, 32)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_PURPLE = (180, 0, 255)
NEON_GREEN = (0, 255, 100)
NEON_ORANGE = (259, 120, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 160)
DARK_CARD = (16, 20, 42, 140)
FPS = 60

# Fonts
try:
    TITLE_FONT = pygame.font.SysFont("Outfit", 45, bold=True)
    HEADER_FONT = pygame.font.SysFont("Outfit", 26, bold=True)
    BODY_FONT = pygame.font.SysFont("Outfit", 18)
    CAT_FONT = pygame.font.SysFont("Outfit", 14, bold=True)
    BTN_FONT = pygame.font.SysFont("Outfit", 22, bold=True)
except:
    try:
        TITLE_FONT = pygame.font.SysFont("Segoe UI", 45, bold=True)
        HEADER_FONT = pygame.font.SysFont("Segoe UI", 26, bold=True)
        BODY_FONT = pygame.font.SysFont("Segoe UI", 18)
        CAT_FONT = pygame.font.SysFont("Segoe UI", 14, bold=True)
        BTN_FONT = pygame.font.SysFont("Segoe UI", 22, bold=True)
    except:
        TITLE_FONT = pygame.font.Font(None, 45)
        HEADER_FONT = pygame.font.Font(None, 26)
        BODY_FONT = pygame.font.Font(None, 18)
        CAT_FONT = pygame.font.Font(None, 14)
        BTN_FONT = pygame.font.Font(None, 22)

# Game Database (Expanded to 15 games)
GAMES = [
    {
        "name": "Tetris",
        "path": "Tetris/main.py",
        "dir": "Tetris",
        "cat": "PUZZLE",
        "desc": "Neon Cyberpunk Tetris featuring soft/hard drop, hold queue, next queue preview, ghost landing projection, and visual line clear explosions.",
        "keys": "Arrows (Move/Rotate), Space (Hard Drop), C/Shift (Hold)"
    },
    {
        "name": "Space Dodge",
        "path": "Space_Dodge/main.py",
        "dir": "Space_Dodge",
        "cat": "SURVIVAL",
        "desc": "Pilot a glowing vector spaceship. Dodge rotating orange meteorites falling in dynamic orbits, leave thruster flame trails, and survive.",
        "keys": "Left/Right Arrows (or A/D to steer)"
    },
    {
        "name": "Pong",
        "path": "pong/main.py",
        "dir": "pong",
        "cat": "RETRO",
        "desc": "Cyberpunk Neon Pong. Deflect a glowing ball that leaves a fading particle path, trigger screen-shakes on scores, and fight with physics.",
        "keys": "P1: W/S keys | P2: Up/Down Arrow keys"
    },
    {
        "name": "Snake",
        "path": "snake/main.py",
        "dir": "snake",
        "cat": "RETRO",
        "desc": "Classic Arcade Neon Snake. Munch glowing food pellets, spawn particle trails, avoid crashing into grid borders or your own growing tail.",
        "keys": "Arrow Keys (or WASD to steer)"
    },
    {
        "name": "Car Racing",
        "path": "Car_Racing/main.py",
        "dir": "Car_Racing",
        "cat": "RACING",
        "desc": "High speed racing. Steer, accelerate, drift on outer track boundaries, and cross the finish line before a smart computer-controlled opponent.",
        "keys": "Arrow Keys (Steer/Drive)"
    },
    {
        "name": "Space Invader",
        "path": "Space_invader/main.py",
        "dir": "Space_invader",
        "cat": "SHOOTER",
        "desc": "Classic shoot-'em-up. Lead your fighter against descending squadrons of alien spaceships, fire yellow laser bolts, and dodge enemy pulses.",
        "keys": "Arrow Keys (Move), Space (Shoot Lasers)"
    },
    {
        "name": "Galaxy Fight",
        "path": "Galaxy_Fight/main.py",
        "dir": "Galaxy_Fight",
        "cat": "VERSUS",
        "desc": "Local 2-player spaceship dogfight. Shoot lasers across the middle divider barrier and deplete your opponent's health shields to win.",
        "keys": "P1: WASD + L-Ctrl (Shoot) | P2: Arrows + R-Ctrl"
    },
    {
        "name": "2048",
        "path": "2048/main.py",
        "dir": "2048",
        "cat": "PUZZLE",
        "desc": "Strategic math puzzle. Slide tiles across a grid to merge matching numbers and unlock the legendary 2048 tile without getting grid-locked.",
        "keys": "Arrow Keys (Slide Tiles in four directions)"
    },
    {
        "name": "Platformer",
        "path": "Platformer/main.py",
        "dir": "Platformer",
        "cat": "ACTION",
        "desc": "Physics 2D platformer. Run across floating platforms as Mask Dude, perform double jumps, and time your moves to dodge glowing fire traps.",
        "keys": "Left/Right Arrows (Move), Space (Double Jump)"
    },
    {
        "name": "Checkers",
        "path": "checkers/main.py",
        "dir": "checkers",
        "cat": "BOARD",
        "desc": "Classic board game of checkers. Plan your moves, jump over opponent tokens to capture them, crown your pieces, and wipe the board.",
        "keys": "Mouse Click (Select and move checkers pieces)"
    },
    {
        "name": "Neon Asteroids",
        "path": "Asteroids/main.py",
        "dir": "Asteroids",
        "cat": "SURVIVAL",
        "desc": "Classic vector space survival. Blast giant radioactive asteroids that shatter into smaller fragments, manage shield cores, and steer against high-speed impacts.",
        "keys": "UP (Thrust), Left/Right (Rotate), Space (Fire Lasers)"
    },
    {
        "name": "Neon Pac-Man",
        "path": "Pacman/main.py",
        "dir": "Pacman",
        "cat": "RETRO",
        "desc": "Munch glowing dot pellets in a cybernetic grid maze, avoid colorful AI-controlled ghosts, and eat power pills to trigger high-score counter hunts.",
        "keys": "Arrow Keys (Steer Pacman through maze paths)"
    },
    {
        "name": "Flappy Neon",
        "path": "Flappy/main.py",
        "dir": "Flappy",
        "cat": "ACTION",
        "desc": "High-speed flight avoidance. Tap to flap your glowing vector bird through moving hazard pipe gates, spawn trailing sparks, and test your split-second reflexes.",
        "keys": "Space / UP Arrow / Left Mouse Click (Flap Wing)"
    },
    {
        "name": "Neon Lander",
        "path": "Lander/main.py",
        "dir": "Lander",
        "cat": "SURVIVAL",
        "desc": "Lunar module gravity descent simulator. Burn fuel thrusters to slow your vertical falling speed, balance roll angle, and perform soft touchdowns on glowing cyan pads.",
        "keys": "UP (Thrust), Left/Right (Rotate Capsule)"
    },
    {
        "name": "Neon Minesweeper",
        "path": "Minesweeper/main.py",
        "dir": "Minesweeper",
        "cat": "PUZZLE",
        "desc": "Tactical radioactive hazard sweeper. Scan cells on a glowing 10x10 matrix, flag mine coordinates, and perform safe sweeps in bright neon spark bursts.",
        "keys": "Left Click (Uncover Cell) | Right Click (Flag Mine)"
    }
]


# Parallax Drifting Stars
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.15, 0.9)
        self.size = random.uniform(0.8, 2.2)
        self.color = random.choice([
            (0, 180, 255),
            (255, 0, 120),
            (120, 120, 180),
            (200, 220, 255)
        ])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


# Text Wrapper
def draw_text_wrap(surface, text, font, color, x, y, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        if font.size(test_line)[0] > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
        
    y_offset = y
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y_offset))
        y_offset += font.get_linesize() + 4


def draw_neon_grid(surface):
    # Base fill
    surface.fill(DARK_BG)
    # Draw faint neon grid
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, GRID_LINE_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, GRID_LINE_COLOR, (0, y), (WIDTH, y))


def launch_game(game):
    print(f"Launching {game['name']}...")
    # Use sys.executable to run the subgame in the exact same python virtual environment
    # Run in working directory of the game to ensure correct relative asset loading
    subprocess.Popen([sys.executable, os.path.basename(game["path"])], cwd=game["dir"])


def main():
    run = True
    clock = pygame.time.Clock()

    # Generate stars
    stars = [Star() for _ in range(80)]

    selected_index = 0
    visible_start = 0
    max_visible_items = 9  # Display at most 9 items at once to avoid overflow
    
    # Layout Coordinates
    list_x, list_y = 45, 105
    list_w, list_h = 390, 520
    item_h = 48
    item_gap = 8

    card_x, card_y = 475, 105
    card_w, card_h = 430, 520

    launch_btn_rect = pygame.Rect(card_x + 30, card_y + card_h - 90, card_w - 60, 55)

    while run:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(GAMES)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(GAMES)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    launch_game(GAMES[selected_index])
                elif event.key == pygame.K_ESCAPE:
                    run = False
                    break
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Adjust sliding visible window offset based on selection index
        if selected_index < visible_start:
            visible_start = selected_index
        elif selected_index >= visible_start + max_visible_items:
            visible_start = selected_index - max_visible_items + 1

        # Render background
        draw_neon_grid(WIN)
        for star in stars:
            star.update()
            star.draw(WIN)

        # Draw Header
        title_surf = TITLE_FONT.render("PYGAME CABINET ARCADE", True, WHITE)
        title_glow = TITLE_FONT.render("PYGAME CABINET ARCADE", True, NEON_PURPLE)
        WIN.blit(title_glow, (WIDTH // 2 - title_surf.get_width() // 2 + 2, 27))
        WIN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 25))

        # Render Left Scrollable List (drawing only the visible window)
        for idx in range(max_visible_items):
            i = visible_start + idx
            if i >= len(GAMES):
                break
                
            game = GAMES[i]
            item_y = list_y + idx * (item_h + item_gap)
            item_rect = pygame.Rect(list_x, item_y, list_w, item_h)
            
            is_hovered = item_rect.collidepoint(mouse_pos)
            is_selected = (i == selected_index)

            # Update selection index on mouse hover
            if is_hovered:
                selected_index = i

            # Launch on mouse click
            if is_hovered and mouse_clicked:
                launch_game(game)

            # Draw list item box
            if is_selected:
                # Glowing selected item
                pygame.draw.rect(WIN, (22, 28, 52), item_rect, border_radius=8)
                pygame.draw.rect(WIN, NEON_BLUE, item_rect, 2, border_radius=8)
                # Left accent indicator line
                pygame.draw.rect(WIN, NEON_BLUE, (list_x + 5, item_y + 8, 4, item_h - 16), border_radius=2)
                text_color = NEON_BLUE
            elif is_hovered:
                # Hover effect
                pygame.draw.rect(WIN, (15, 17, 30), item_rect, border_radius=8)
                pygame.draw.rect(WIN, NEON_PINK, item_rect, 1, border_radius=8)
                text_color = NEON_PINK
            else:
                # Dormant state
                pygame.draw.rect(WIN, (11, 13, 24), item_rect, border_radius=8)
                pygame.draw.rect(WIN, (25, 25, 45), item_rect, 1, border_radius=8)
                text_color = WHITE

            # Render Game Name inside item box
            name_text = HEADER_FONT.render(game["name"], True, text_color)
            WIN.blit(name_text, (list_x + 25, item_y + (item_h - name_text.get_height()) // 2))

            # Draw Category badge inside item box (aligned right)
            cat_color = NEON_GREEN if game["cat"] in ["RETRO", "BOARD"] else (GOLD if game["cat"] == "PUZZLE" else NEON_PINK)
            cat_badge = CAT_FONT.render(game["cat"], True, cat_color)
            badge_rect = pygame.Rect(list_x + list_w - cat_badge.get_width() - 25, item_y + (item_h - 22) // 2, cat_badge.get_width() + 12, 22)
            pygame.draw.rect(WIN, (cat_color[0] // 8, cat_color[1] // 8, cat_color[2] // 8), badge_rect, border_radius=4)
            pygame.draw.rect(WIN, cat_color, badge_rect, 1, border_radius=4)
            WIN.blit(cat_badge, (badge_rect.x + 6, badge_rect.y + 3))

        # Render Scroll Indicators (small arrows if list is scrollable)
        if visible_start > 0:
            # Up arrow indicator
            pygame.draw.polygon(WIN, NEON_BLUE, [(list_x + list_w // 2, list_y - 12), (list_x + list_w // 2 - 8, list_y - 4), (list_x + list_w // 2 + 8, list_y - 4)])
        if visible_start + max_visible_items < len(GAMES):
            # Down arrow indicator
            pygame.draw.polygon(WIN, NEON_BLUE, [(list_x + list_w // 2, list_y + list_h + 4), (list_x + list_w // 2 - 8, list_y + list_h - 4), (list_x + list_w // 2 + 8, list_y + list_h - 4)])

        # Render Right Glassmorphic Card (Details)
        selected_game = GAMES[selected_index]
        
        # Glass card body with alpha blend
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, DARK_CARD, (0, 0, card_w, card_h), border_radius=15)
        WIN.blit(card_surf, (card_x, card_y))
        pygame.draw.rect(WIN, NEON_BLUE, (card_x, card_y, card_w, card_h), 2, border_radius=15)

        # 1. Selected game title
        g_title = TITLE_FONT.render(selected_game["name"], True, WHITE)
        WIN.blit(g_title, (card_x + 30, card_y + 30))

        # 2. Selected Category badge
        c_color = NEON_GREEN if selected_game["cat"] in ["RETRO", "BOARD"] else (GOLD if selected_game["cat"] == "PUZZLE" else NEON_PINK)
        c_badge = CAT_FONT.render(selected_game["cat"], True, c_color)
        c_badge_rect = pygame.Rect(card_x + 30, card_y + 35 + g_title.get_height(), c_badge.get_width() + 16, 26)
        pygame.draw.rect(WIN, (c_color[0] // 8, c_color[1] // 8, c_color[2] // 8), c_badge_rect, border_radius=5)
        pygame.draw.rect(WIN, c_color, c_badge_rect, 1, border_radius=5)
        WIN.blit(c_badge, (c_badge_rect.x + 8, c_badge_rect.y + 5))

        # 3. Description Section
        desc_lbl = HEADER_FONT.render("DESCRIPTION", True, NEON_PINK)
        WIN.blit(desc_lbl, (card_x + 30, card_y + 115))
        draw_text_wrap(WIN, selected_game["desc"], BODY_FONT, GRAY, card_x + 30, card_y + 150, card_w - 60)

        # 4. Controls Section
        ctrl_lbl = HEADER_FONT.render("CONTROLS", True, NEON_GREEN)
        WIN.blit(ctrl_lbl, (card_x + 30, card_y + 275))
        
        # Key-caps details outline
        keys_box_rect = pygame.Rect(card_x + 30, card_y + 310, card_w - 60, 80)
        pygame.draw.rect(WIN, (10, 10, 25), keys_box_rect, border_radius=8)
        pygame.draw.rect(WIN, (35, 35, 60), keys_box_rect, 1, border_radius=8)
        
        # Render the keys inside the box
        draw_text_wrap(WIN, selected_game["keys"], BODY_FONT, WHITE, card_x + 45, card_y + 325, card_w - 90)

        # 5. Glowing Launch Button
        btn_hovered = launch_btn_rect.collidepoint(mouse_pos)
        if btn_hovered:
            pygame.draw.rect(WIN, NEON_BLUE, launch_btn_rect, border_radius=12)
            btn_text = BTN_FONT.render("LAUNCH GAME NATIVE", True, DARK_BG)
            if mouse_clicked:
                launch_game(selected_game)
        else:
            pygame.draw.rect(WIN, DARK_BG, launch_btn_rect, border_radius=12)
            pygame.draw.rect(WIN, NEON_BLUE, launch_btn_rect, 2, border_radius=12)
            btn_text = BTN_FONT.render("LAUNCH GAME NATIVE", True, NEON_BLUE)
            
        WIN.blit(btn_text, (launch_btn_rect.centerx - btn_text.get_width() // 2, launch_btn_rect.centery - btn_text.get_height() // 2))

        # Draw footer/navigation hints
        hint_text = BODY_FONT.render("Use Arrow Keys & Enter, or click to launch games. Press ESC to quit.", True, (80, 80, 100))
        WIN.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 35))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
