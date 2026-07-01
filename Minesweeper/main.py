import pygame
import asyncio
import random
import math
import os
import sys

try:
    import arcade_api
except ImportError:
    sys.path.append("..")
    try:
        import arcade_api
    except:
        arcade_api = None

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 600, 700  # 500x500 for grid + 100 for HUD + 100 padding
GRID_SIZE = 50
HUD_HEIGHT = 120
ROWS, COLS = 10, 10
NUM_MINES = 12

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Minesweeper - Arcade Edition")

# Colors
DARK_BG = (8, 8, 16)
HUD_BG = (12, 12, 24)
GRID_BORDER_COLOR = (0, 200, 255)  # Neon Blue
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
NEON_BLUE = (0, 200, 255)
NEON_PURPLE = (180, 0, 255)
ORANGE = (255, 120, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
DARK_CELL = (20, 20, 35)

# Number Colors
NUM_COLORS = {
    1: (0, 200, 255),    # Neon Cyan
    2: (0, 255, 100),    # Neon Green
    3: (255, 0, 150),    # Neon Pink
    4: (180, 0, 255),    # Neon Purple
    5: (255, 200, 0),    # Neon Gold
    6: (255, 120, 0),    # Neon Orange
    7: (255, 255, 255),  # White
    8: (150, 150, 150)   # Gray
}

# Fonts
try:
    FONT_CELL = pygame.font.SysFont("Outfit", 26, bold=True)
    FONT_HUD = pygame.font.SysFont("Outfit", 20, bold=True)
    FONT_LARGE = pygame.font.SysFont("Outfit", 50, bold=True)
except:
    try:
        FONT_CELL = pygame.font.SysFont("Segoe UI", 26, bold=True)
        FONT_HUD = pygame.font.SysFont("Segoe UI", 20, bold=True)
        FONT_LARGE = pygame.font.SysFont("Segoe UI", 50, bold=True)
    except:
        FONT_CELL = pygame.font.Font(None, 26)
        FONT_HUD = pygame.font.Font(None, 20)
        FONT_LARGE = pygame.font.Font(None, 50)

FPS = 60


class MineSparkle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4.0, 4.0)
        self.vy = random.uniform(-4.0, 4.0)
        self.life = random.randint(15, 28)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class Cell:
    def __init__(self, row, col, rows, cols):
        self.row = row
        self.col = col
        grid_w = cols * GRID_SIZE
        grid_h = rows * GRID_SIZE
        self.x = col * GRID_SIZE + (WIDTH - grid_w) // 2
        self.y = row * GRID_SIZE + HUD_HEIGHT + 20 + (500 - grid_h) // 2
        
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.neighbor_mines = 0

    def draw(self, surface):
        rect = pygame.Rect(self.x + 2, self.y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
        
        if self.revealed:
            pygame.draw.rect(surface, DARK_CELL, rect, border_radius=6)
            pygame.draw.rect(surface, (40, 40, 60), rect, 1, border_radius=6)
            
            if self.is_mine:
                pygame.draw.circle(surface, NEON_PINK, (self.x + GRID_SIZE//2, self.y + GRID_SIZE//2), GRID_SIZE//2 - 10)
                pygame.draw.circle(surface, WHITE, (self.x + GRID_SIZE//2, self.y + GRID_SIZE//2), 4)
            elif self.neighbor_mines > 0:
                color = NUM_COLORS.get(self.neighbor_mines, WHITE)
                text = FONT_CELL.render(str(self.neighbor_mines), 1, color)
                surface.blit(text, (self.x + (GRID_SIZE/2 - text.get_width()/2), self.y + (GRID_SIZE/2 - text.get_height()/2)))
        else:
            pygame.draw.rect(surface, (12, 18, 42), rect, border_radius=6)
            border_color = NEON_BLUE
            if self.flagged:
                border_color = ORANGE
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=6)

            if self.flagged:
                center_x = self.x + GRID_SIZE // 2
                center_y = self.y + GRID_SIZE // 2
                p1 = (center_x - 6, center_y + 8)
                p2 = (center_x - 6, center_y - 8)
                p3 = (center_x + 8, center_y - 2)
                pygame.draw.polygon(surface, ORANGE, [p1, p2, p3])
                pygame.draw.line(surface, ORANGE, (center_x - 6, center_y - 8), (center_x - 6, center_y + 10), 2)


def get_level_params(lvl):
    if lvl == 1:
        return (6, 6, 4)
    elif lvl == 2:
        return (7, 7, 6)
    elif lvl == 3:
        return (8, 8, 8)
    elif lvl == 4:
        return (9, 9, 10)
    else:
        # 10x10 with increasing mine density
        mines = min(45, 10 + lvl * 1.5)
        return (10, 10, int(mines))


class MinesweeperGame:
    def __init__(self, level=1):
        self.level = level
        self.rows, self.cols, self.num_mines = get_level_params(level)
        self.grid = [[Cell(r, c, self.rows, self.cols) for c in range(self.cols)] for r in range(self.rows)]
        self.mines_left = self.num_mines
        self.cells_to_reveal = self.rows * self.cols - self.num_mines
        self.game_over = False
        self.victory = False
        self.particles = []
        self.shake_duration = 0
        self.shake_amount = 0
        self.first_click = True

    def populate_mines(self, start_r, start_c):
        placed = 0
        while placed < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            
            if abs(r - start_r) <= 1 and abs(c - start_c) <= 1:
                continue
                
            if not self.grid[r][c].is_mine:
                self.grid[r][c].is_mine = True
                placed += 1
                
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    self.grid[r][c].neighbor_mines = sum(
                        1 for dr in [-1, 0, 1] for dc in [-1, 0, 1]
                        if 0 <= r + dr < self.rows and 0 <= c + dc < self.cols
                        and self.grid[r + dr][c + dc].is_mine
                    )

    def reveal(self, r, c):
        if self.grid[r][c].revealed or self.grid[r][c].flagged:
            return
            
        self.grid[r][c].revealed = True
        
        if self.grid[r][c].is_mine:
            self.game_over = True
            for row in self.grid:
                for cell in row:
                    if cell.is_mine:
                        cell.revealed = True
            
            cell_x = self.grid[r][c].x + GRID_SIZE // 2
            cell_y = self.grid[r][c].y + GRID_SIZE // 2
            for _ in range(40):
                self.particles.append(MineSparkle(cell_x, cell_y, NEON_PINK))
                self.particles.append(MineSparkle(cell_x, cell_y, ORANGE))
            self.shake_duration = 35
            self.shake_amount = 14
            return

        self.cells_to_reveal -= 1
        
        cell_x = self.grid[r][c].x + GRID_SIZE // 2
        cell_y = self.grid[r][c].y + GRID_SIZE // 2
        for _ in range(3):
            self.particles.append(MineSparkle(cell_x, cell_y, NEON_BLUE))
            
        if self.grid[r][c].neighbor_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal(nr, nc)

        if self.cells_to_reveal == 0 and not self.game_over:
            self.victory = True
            for row in self.grid:
                for cell in row:
                    if cell.is_mine:
                        cell.flagged = True
            self.mines_left = 0

    def flag(self, r, c):
        if self.grid[r][c].revealed:
            return
            
        self.grid[r][c].flagged = not self.grid[r][c].flagged
        self.mines_left += -1 if self.grid[r][c].flagged else 1
        
        cell_x = self.grid[r][c].x + GRID_SIZE // 2
        cell_y = self.grid[r][c].y + GRID_SIZE // 2
        for _ in range(5):
            self.particles.append(MineSparkle(cell_x, cell_y, ORANGE))

    def handle_click(self, pos, right_click=False):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if pygame.Rect(cell.x, cell.y, GRID_SIZE, GRID_SIZE).collidepoint(pos):
                    if right_click:
                        self.flag(r, c)
                    else:
                        if self.first_click:
                            self.populate_mines(r, c)
                            self.first_click = False
                        self.reveal(r, c)
                    break

    def draw_hud(self, surface):
        hud_rect = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, HUD_BG, hud_rect)
        pygame.draw.line(surface, NEON_BLUE, (0, HUD_HEIGHT - 2), (WIDTH, HUD_HEIGHT - 2), 3)

        # Draw Mines Counter
        mines_lbl = FONT_HUD.render("HAZARD SIGNALS", True, ORANGE)
        mines_val = FONT_LARGE.render(f"{max(0, self.mines_left):02d}", True, WHITE)
        surface.blit(mines_lbl, (40, 25))
        surface.blit(mines_val, (40, 50))

        # Draw level stage text
        level_lbl = FONT_HUD.render(f"STAGE {self.level}/20", True, GOLD)
        surface.blit(level_lbl, (WIDTH // 2 - level_lbl.get_width() // 2, 45))

        # Draw Cells Left to Uncover
        cells_lbl = FONT_HUD.render("SECURE GRID LEFT", True, NEON_BLUE)
        cells_val = FONT_LARGE.render(f"{max(0, self.cells_to_reveal):03d}", True, WHITE)
        surface.blit(cells_lbl, (WIDTH - cells_lbl.get_width() - 40, 25))
        surface.blit(cells_val, (WIDTH - cells_val.get_width() - 40, 50))


async def main():
    run = True
    clock = pygame.time.Clock()
    
    level = 1
    max_levels = 20
    game_won = False
    
    game = MinesweeperGame(level)
    score = 0
    score_submitted = False
    
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    while run:
        clock.tick(FPS)

        # Update particles
        for p in game.particles[:]:
            p.update()
            if p.life <= 0:
                game.particles.remove(p)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if game.game_over or game.victory:
                    if event.key == pygame.K_r:
                        level = 1
                        game_won = False
                        game = MinesweeperGame(level)
                        score = 0
                        score_submitted = False
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game.game_over and not game.victory:
                    if event.button == 1: # Left Click
                        game.handle_click(pygame.mouse.get_pos(), False)
                    elif event.button == 3: # Right Click
                        game.handle_click(pygame.mouse.get_pos(), True)

        # Check stage victory
        if game.victory and not game.game_over:
            if level >= max_levels:
                game_won = True
                if not score_submitted:
                    score_submitted = True
                    if arcade_api:
                        final_score = score + 5000
                        arcade_api.submit_score("Neon Minesweeper", final_score)
            else:
                # Level transition
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(overlay, (5, 5, 12, 215), (0, 0, WIDTH, HEIGHT))
                game_surface.fill(DARK_BG)
                for p in game.particles:
                    p.draw(game_surface)
                game_surface.blit(overlay, (0, 0))

                card_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
                pygame.draw.rect(game_surface, (15, 15, 30), card_rect, border_radius=15)
                pygame.draw.rect(game_surface, NEON_GREEN, card_rect, 3, border_radius=15)

                title_str = f"STAGE {level} CLEARED!"
                over_title = FONT_LARGE.render(title_str, True, NEON_GREEN)
                sub_lbl = FONT_HUD.render("NEXT GRID SECTOR INITIALIZING...", True, WHITE)

                game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 45))
                game_surface.blit(sub_lbl, (WIDTH // 2 - sub_lbl.get_width() // 2, HEIGHT // 3 + 115))

                WIN.fill((0, 0, 0))
                WIN.blit(game_surface, (0, 0))
                pygame.display.update()

                await asyncio.sleep(2.5)
                score += (game.rows * game.cols - game.num_mines) * 10
                level += 1
                game = MinesweeperGame(level)
                continue

        # Submit score once on terminal game over
        if game.game_over and not score_submitted:
            score_submitted = True
            if arcade_api:
                cells_revealed = (game.rows * game.cols - game.num_mines) - game.cells_to_reveal
                final_score = score + cells_revealed * 10
                arcade_api.submit_score("Neon Minesweeper", final_score)

        # Draw
        game_surface.fill(DARK_BG)
        
        # Draw cells
        for row in game.grid:
            for cell in row:
                cell.draw(game_surface)

        # Draw particles
        for p in game.particles:
            p.draw(game_surface)

        # Draw HUD
        game.draw_hud(game_surface)

        # Draw Game Over or Grand Victory Banner
        if game.game_over or game_won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 12, 215), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            
            banner_color = NEON_PINK if game.game_over else NEON_GREEN
            pygame.draw.rect(game_surface, banner_color, over_rect, 3, border_radius=15)

            title_str = "CORE BREACH" if game.game_over else "DETECTOR SUPREME"
            over_title = FONT_LARGE.render(title_str, True, banner_color)
            restart_hint = FONT_HUD.render("PRESS 'R' TO REBOOT DETECTOR", True, NEON_BLUE)

            game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 45))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 125))

        # Handle screen shake
        if game.shake_duration > 0:
            offset_x = random.randint(-game.shake_amount, game.shake_amount)
            offset_y = random.randint(-game.shake_amount, game.shake_amount)
            game.shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        WIN.fill((0, 0, 0))
        WIN.blit(game_surface, (offset_x, offset_y))
        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
