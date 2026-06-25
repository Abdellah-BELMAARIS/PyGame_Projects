import pygame
import random
import math
import asyncio
import os

# Initialize Pygame
pygame.init()

# Constants
FPS = 60
WIDTH, HEIGHT = 800, 900  # 800 for grid, 100 for HUD at top
GRID_SIZE = 800
HUD_HEIGHT = 100
ROWS, COLS = 4, 4
RECT_HEIGHT = GRID_SIZE // ROWS
RECT_WIDTH = GRID_SIZE // COLS
MOVE_VEL = 25

# Colors (Cyberpunk Neon Palette)
DARK_BG = (8, 8, 16)
HUD_BG = (12, 12, 24)
GRID_LINE_COLOR = (22, 22, 42)
GRID_BORDER_COLOR = (180, 0, 255)  # Neon Purple
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)

# Tile Color Map (Neon Cyberpunk Progression)
TILE_COLORS = {
    2: (0, 200, 255),       # Neon Cyan-Blue
    4: (0, 255, 200),       # Neon Cyan-Green
    8: (0, 255, 100),       # Neon Green
    16: (180, 255, 0),      # Neon Lime
    32: (255, 200, 0),      # Neon Gold
    64: (255, 120, 0),      # Neon Orange
    128: (255, 0, 100),     # Neon Pink
    256: (255, 0, 200),     # Neon Magenta
    512: (180, 0, 255),     # Neon Purple
    1024: (100, 0, 255),    # Neon Violet
    2048: (255, 215, 0),    # Legendary Gold
    4096: (255, 255, 255)   # Supernova White
}

# Fonts
try:
    FONT_TILE = pygame.font.SysFont("Outfit", 46, bold=True)
    FONT_HUD_LABEL = pygame.font.SysFont("Outfit", 16, bold=True)
    FONT_HUD_VAL = pygame.font.SysFont("Outfit", 26, bold=True)
    FONT_OVERLAY = pygame.font.SysFont("Outfit", 60, bold=True)
    FONT_OVERLAY_SUB = pygame.font.SysFont("Outfit", 22, bold=True)
except:
    try:
        FONT_TILE = pygame.font.SysFont("Segoe UI", 46, bold=True)
        FONT_HUD_LABEL = pygame.font.SysFont("Segoe UI", 16, bold=True)
        FONT_HUD_VAL = pygame.font.SysFont("Segoe UI", 26, bold=True)
        FONT_OVERLAY = pygame.font.SysFont("Segoe UI", 60, bold=True)
        FONT_OVERLAY_SUB = pygame.font.SysFont("Segoe UI", 22, bold=True)
    except:
        FONT_TILE = pygame.font.Font(None, 46)
        FONT_HUD_LABEL = pygame.font.Font(None, 16)
        FONT_HUD_VAL = pygame.font.Font(None, 26)
        FONT_OVERLAY = pygame.font.Font(None, 60)
        FONT_OVERLAY_SUB = pygame.font.Font(None, 22)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon 2048 - Arcade Edition")


class MergeParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4.5, 4.5)
        self.vy = random.uniform(-4.5, 4.5)
        self.life = random.randint(15, 28)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Slight gravity
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 6) + 1
        # Inner glowing circle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)
        # Faint outer halo
        if self.life > 10:
            halo = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*self.color, 45), (radius * 2, radius * 2), radius * 2)
            surface.blit(halo, (int(self.x) - radius * 2, int(self.y) - radius * 2))


class Tile:
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        return TILE_COLORS.get(self.value, TILE_COLORS[4096])

    def draw(self, window):
        color = self.get_color()
        # Draw tile with shifted y for HUD
        draw_y = self.y + HUD_HEIGHT
        rect = pygame.Rect(self.x + 6, draw_y + 6, RECT_WIDTH - 12, RECT_HEIGHT - 12)
        
        # 1. Neon glowing box body
        pygame.draw.rect(window, (color[0] // 6, color[1] // 6, color[2] // 6), rect, border_radius=12)
        pygame.draw.rect(window, color, rect, 2, border_radius=12)
        
        # 2. Inner glossy highlight
        highlight_color = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
        pygame.draw.rect(window, highlight_color, (self.x + 12, draw_y + 12, RECT_WIDTH - 24, RECT_HEIGHT - 24), 1, border_radius=8)

        # 3. Draw text number
        val_str = str(self.value)
        text = FONT_TILE.render(val_str, 1, WHITE)
        
        # Draw shadow
        text_shadow = FONT_TILE.render(val_str, 1, (10, 10, 15))
        window.blit(text_shadow, (self.x + (RECT_WIDTH / 2 - text.get_width() / 2) + 2, draw_y + (RECT_HEIGHT / 2 - text.get_height() / 2) + 2))
        window.blit(text, (self.x + (RECT_WIDTH / 2 - text.get_width() / 2), draw_y + (RECT_HEIGHT / 2 - text.get_height() / 2)))

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


class Game2048:
    def __init__(self):
        self.tiles = {}
        self.score = 0
        self.high_score = self.load_high_score()
        self.particles = []
        self.shake_duration = 0
        self.shake_amount = 0
        self.game_over = False
        
        self.generate_initial_tiles()

    def load_high_score(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high_score(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def generate_initial_tiles(self):
        self.tiles.clear()
        for _ in range(2):
            self.spawn_new_tile()

    def get_random_pos(self):
        empty_cells = []
        for r in range(ROWS):
            for c in range(COLS):
                if f"{r}{c}" not in self.tiles:
                    empty_cells.append((r, c))
        if not empty_cells:
            return None
        return random.choice(empty_cells)

    def spawn_new_tile(self):
        pos = self.get_random_pos()
        if pos:
            row, col = pos
            # Spawn a 2 (90% chance) or 4 (10% chance)
            self.tiles[f"{row}{col}"] = Tile(random.choice([2, 2, 2, 2, 2, 2, 2, 2, 2, 4]), row, col)

    def draw_grid_background(self, window):
        # Draw background board
        board_rect = pygame.Rect(0, HUD_HEIGHT, WIDTH, GRID_SIZE)
        pygame.draw.rect(window, (11, 11, 20), board_rect)
        
        # Draw faint neon grid lines
        for r in range(1, ROWS):
            y = r * RECT_HEIGHT + HUD_HEIGHT
            pygame.draw.line(window, GRID_LINE_COLOR, (0, y), (WIDTH, y), 4)

        for col in range(1, COLS):
            x = col * RECT_WIDTH
            pygame.draw.line(window, GRID_LINE_COLOR, (x, HUD_HEIGHT), (x, HEIGHT), 4)

        # Draw outer glowing border
        pygame.draw.rect(window, GRID_BORDER_COLOR, board_rect, 4)

    def draw_hud(self, window):
        # Glassmorphic top HUD panel
        hud_rect = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(window, HUD_BG, hud_rect)
        pygame.draw.line(window, NEON_BLUE, (0, HUD_HEIGHT - 2), (WIDTH, HUD_HEIGHT - 2), 3)

        # Draw Title
        title_lbl = FONT_OVERLAY_SUB.render("NEON 2048", True, WHITE)
        title_lbl_glow = FONT_OVERLAY_SUB.render("NEON 2048", True, NEON_BLUE)
        window.blit(title_lbl_glow, (25, 26))
        window.blit(title_lbl, (23, 24))
        
        desc_lbl = FONT_HUD_LABEL.render("MERGE THE SHINING TILES", True, (100, 110, 140))
        window.blit(desc_lbl, (23, 56))

        # Score box
        score_box_w = 140
        score_box_h = 60
        score_box_x = WIDTH - score_box_w * 2 - 30
        score_box_y = 20

        # Draw Score Box
        pygame.draw.rect(window, (20, 24, 48), (score_box_x, score_box_y, score_box_w, score_box_h), border_radius=8)
        pygame.draw.rect(window, NEON_BLUE, (score_box_x, score_box_y, score_box_w, score_box_h), 1, border_radius=8)
        
        lbl = FONT_HUD_LABEL.render("SCORE", True, NEON_BLUE)
        val = FONT_HUD_VAL.render(str(self.score), True, WHITE)
        window.blit(lbl, (score_box_x + 12, score_box_y + 6))
        window.blit(val, (score_box_x + 12, score_box_y + 24))

        # Best Box
        best_box_x = WIDTH - score_box_w - 20
        pygame.draw.rect(window, (20, 24, 48), (best_box_x, score_box_y, score_box_w, score_box_h), border_radius=8)
        pygame.draw.rect(window, GOLD, (best_box_x, score_box_y, score_box_w, score_box_h), 1, border_radius=8)
        
        lbl_b = FONT_HUD_LABEL.render("BEST", True, GOLD)
        val_b = FONT_HUD_VAL.render(str(self.high_score), True, WHITE)
        window.blit(lbl_b, (best_box_x + 12, score_box_y + 6))
        window.blit(val_b, (best_box_x + 12, score_box_y + 24))

    def draw(self, window):
        window.fill(DARK_BG)
        self.draw_grid_background(window)

        # Draw Tiles
        for tile in self.tiles.values():
            tile.draw(window)

        # Draw Particles
        for particle in self.particles:
            particle.draw(window)

        # Draw HUD
        self.draw_hud(window)

        # Draw Game Over Overlay
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 15, 215), (0, 0, WIDTH, HEIGHT))
            window.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(window, (15, 15, 30), over_rect, border_radius=15)
            pygame.draw.rect(window, NEON_PINK, over_rect, 3, border_radius=15)

            over_title = FONT_OVERLAY.render("GRID LOCKED", True, NEON_PINK)
            final_lbl = FONT_HUD_VAL.render(f"FINAL SCORE: {self.score}", True, WHITE)
            restart_hint = FONT_OVERLAY_SUB.render("PRESS R TO REPLAY", True, NEON_BLUE)

            window.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 35))
            window.blit(final_lbl, (WIDTH // 2 - final_lbl.get_width() // 2, HEIGHT // 3 + 105))
            window.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 160))

    def update_tiles(self, sorted_tiles):
        self.tiles.clear()
        for tile in sorted_tiles:
            self.tiles[f"{tile.row}{tile.col}"] = tile

    def check_lost(self):
        if len(self.tiles) < 16:
            return False
            
        # Grid is full, check if any adjacent tiles have matching values
        for r in range(ROWS):
            for c in range(COLS):
                val = self.tiles[f"{r}{c}"].value
                # Check right
                if c + 1 < COLS and self.tiles[f"{r}{c+1}"].value == val:
                    return False
                # Check down
                if r + 1 < ROWS and self.tiles[f"{r+1}{c}"].value == val:
                    return False
        return True

    async def move_tiles(self, direction):
        updated = True
        blocks = set()
        clock = pygame.time.Clock()

        # Define sorting and direction parameters
        if direction == "left":
            sort_func = lambda x: x.col
            reverse = False
            delta = (-MOVE_VEL, 0)
            boundary_check = lambda tile: tile.col == 0
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row}{tile.col - 1}")
            merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
            move_check = lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
            ceil = True
        elif direction == "right":
            sort_func = lambda x: x.col
            reverse = True
            delta = (MOVE_VEL, 0)
            boundary_check = lambda tile: tile.col == COLS - 1
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row}{tile.col + 1}")
            merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
            move_check = lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
            ceil = False
        elif direction == "up":
            sort_func = lambda x: x.row
            reverse = False
            delta = (0, -MOVE_VEL)
            boundary_check = lambda tile: tile.row == 0
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row - 1}{tile.col}")
            merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
            move_check = lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
            ceil = True
        elif direction == "down":
            sort_func = lambda x: x.row
            reverse = True
            delta = (0, MOVE_VEL)
            boundary_check = lambda tile: tile.row == ROWS - 1
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row + 1}{tile.col}")
            merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
            move_check = lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
            ceil = False

        move_occurred = False

        while updated:
            clock.tick(FPS)
            updated = False
            sorted_tiles = sorted(self.tiles.values(), key=sort_func, reverse=reverse)

            for i, tile in enumerate(sorted_tiles):
                if boundary_check(tile):
                    continue

                next_tile = get_next_tile(tile)
                if not next_tile:
                    tile.move(delta)
                    move_occurred = True
                    updated = True
                elif (
                    tile.value == next_tile.value
                    and tile not in blocks
                    and next_tile not in blocks
                ):
                    if merge_check(tile, next_tile):
                        tile.move(delta)
                        updated = True
                    else:
                        # Perform Merge!
                        next_tile.value *= 2
                        self.score += next_tile.value
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()

                        sorted_tiles.pop(i)
                        blocks.add(next_tile)
                        move_occurred = True
                        
                        # Particle emission on merge!
                        tile_color = next_tile.get_color()
                        center_x = next_tile.x + RECT_WIDTH // 2
                        center_y = next_tile.y + RECT_HEIGHT // 2 + HUD_HEIGHT
                        for _ in range(14):
                            self.particles.append(MergeParticle(center_x, center_y, tile_color))

                        # Shake trigger!
                        self.shake_duration = 10
                        self.shake_amount = min(8, int(math.log2(next_tile.value)) * 2 - 2)
                elif move_check(tile, next_tile):
                    tile.move(delta)
                    move_occurred = True
                    updated = True

                tile.set_pos(ceil)

            self.update_tiles(sorted_tiles)
            # Re-draw during movement to animate nicely
            self.draw(WINDOW)
            pygame.display.update()
            await asyncio.sleep(0)

        if move_occurred:
            self.spawn_new_tile()
            if self.check_lost():
                self.game_over = True

    async def run(self):
        clock = pygame.time.Clock()
        run = True
        
        # Action flag to prevent duplicate registers during async slides
        sliding = False

        while run:
            clock.tick(FPS)
            
            # Update particles
            for particle in self.particles[:]:
                particle.update()
                if particle.life <= 0:
                    self.particles.remove(particle)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.__init__()
                    elif not sliding:
                        if event.key in [pygame.K_LEFT, pygame.K_a]:
                            sliding = True
                            await self.move_tiles("left")
                            sliding = False
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            sliding = True
                            await self.move_tiles("right")
                            sliding = False
                        elif event.key in [pygame.K_UP, pygame.K_w]:
                            sliding = True
                            await self.move_tiles("up")
                            sliding = False
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            sliding = True
                            await self.move_tiles("down")
                            sliding = False

            # Draw everything
            # Handle screen shake
            if self.shake_duration > 0:
                offset_x = random.randint(-self.shake_amount, self.shake_amount)
                offset_y = random.randint(-self.shake_amount, self.shake_amount)
                self.shake_duration -= 1
            else:
                offset_x = 0
                offset_y = 0

            # Render off-center for shake
            shaken_surface = pygame.Surface((WIDTH, HEIGHT))
            self.draw(shaken_surface)
            
            WINDOW.fill(DARK_BG)
            WINDOW.blit(shaken_surface, (offset_x, offset_y))
            pygame.display.update()
            
            await asyncio.sleep(0)

        pygame.quit()


if __name__ == "__main__":
    game = Game2048()
    asyncio.run(game.run())