import pygame
import asyncio
import random
import math

pygame.init()

# Window Dimensions
WIDTH, HEIGHT = 800, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Tetris - Arcade Edition")

# Game Configuration
GRID_ROWS = 20
GRID_COLS = 10
BLOCK_SIZE = 30

# Offsets to center the grid on screen
GRID_X = (WIDTH - (GRID_COLS * BLOCK_SIZE)) // 2
GRID_Y = (HEIGHT - (GRID_ROWS * BLOCK_SIZE)) // 2

# Colors (Cyberpunk Neon Palette)
DARK_BG = (10, 10, 18)
GRID_LINE_COLOR = (22, 22, 40)
GRID_BORDER_COLOR = (0, 150, 255)
WHITE = (255, 255, 255)
TEXT_COLOR = (0, 240, 255)
GOLD = (255, 215, 0)
DARK_GRAY = (40, 40, 50)

# Tetromino shapes
SHAPES = {
    'I': [[0, 0, 0, 0],
          [1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, 0, 0]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1],
          [0, 0, 0]],
    'S': [[0, 1, 1],
          [1, 1, 0],
          [0, 0, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1],
          [0, 0, 0]],
    'J': [[1, 0, 0],
          [1, 1, 1],
          [0, 0, 0]],
    'L': [[0, 0, 1],
          [1, 1, 1],
          [0, 0, 0]]
}

SHAPE_COLORS = {
    'I': (0, 240, 255),    # Neon Cyan
    'O': (255, 220, 0),    # Neon Yellow
    'T': (200, 0, 255),    # Neon Purple
    'S': (0, 255, 100),    # Neon Green
    'Z': (255, 50, 50),    # Neon Red
    'J': (0, 100, 255),    # Neon Blue
    'L': (255, 130, 0)     # Neon Orange
}

# Fonts
try:
    FONT_SMALL = pygame.font.SysFont("Outfit", 20, bold=True)
    FONT_MEDIUM = pygame.font.SysFont("Outfit", 30, bold=True)
    FONT_LARGE = pygame.font.SysFont("Outfit", 55, bold=True)
except:
    try:
        FONT_SMALL = pygame.font.SysFont("Segoe UI", 20, bold=True)
        FONT_MEDIUM = pygame.font.SysFont("Segoe UI", 30, bold=True)
        FONT_LARGE = pygame.font.SysFont("Segoe UI", 55, bold=True)
    except:
        FONT_SMALL = pygame.font.Font(None, 20)
        FONT_MEDIUM = pygame.font.Font(None, 30)
        FONT_LARGE = pygame.font.Font(None, 55)

# Particle System for Line Clears
class SparkParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6.0, 6.0)
        self.vy = random.uniform(-4.0, 2.0)
        self.life = random.randint(20, 35)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Slight gravity
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

class Piece:
    def __init__(self, shape_type):
        self.type = shape_type
        self.matrix = [list(row) for row in SHAPES[shape_type]]
        self.color = SHAPE_COLORS[shape_type]
        # Spawn centered horizontally, at the top
        self.x = GRID_COLS // 2 - len(self.matrix[0]) // 2
        self.y = 0

    def rotate(self):
        # Rotate matrix 90 degrees clockwise
        self.matrix = [list(row) for row in zip(*self.matrix[::-1])]

    def get_width(self):
        return len(self.matrix[0])

    def get_height(self):
        return len(self.matrix)

class TetrisGame:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.bag = []
        
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.held_piece_type = None
        self.has_held_this_turn = False
        
        self.particles = []
        self.shake_duration = 0
        self.shake_amount = 0

    def get_new_piece(self):
        # 7-Bag Randomizer system (ensures uniform distribution of pieces)
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        return Piece(self.bag.pop())

    def check_collision(self, piece, offset_x=0, offset_y=0):
        for r, row in enumerate(piece.matrix):
            for c, val in enumerate(row):
                if val:
                    target_x = piece.x + c + offset_x
                    target_y = piece.y + r + offset_y
                    
                    # Boundary checks
                    if target_x < 0 or target_x >= GRID_COLS or target_y >= GRID_ROWS:
                        return True
                    # Check locked pieces
                    if target_y >= 0 and self.grid[target_y][target_x]:
                        return True
        return False

    def rotate_piece(self):
        # Backup original state
        original_matrix = [list(row) for row in self.current_piece.matrix]
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        
        self.current_piece.rotate()
        
        # Super Rotation System (SRS) kick offsets
        # If standard rotation fails, try shifting around to fit
        kicks = [
            (0, 0),    # Try normal
            (-1, 0),   # Kick left 1
            (1, 0),    # Kick right 1
            (0, -1),   # Kick up 1
            (-2, 0),   # Kick left 2 (mainly for I piece)
            (2, 0),    # Kick right 2
        ]
        
        success = False
        for kick_x, kick_y in kicks:
            self.current_piece.x = original_x + kick_x
            self.current_piece.y = original_y + kick_y
            if not self.check_collision(self.current_piece):
                success = True
                break
                
        if not success:
            # Revert if all kicks fail
            self.current_piece.matrix = original_matrix
            self.current_piece.x = original_x
            self.current_piece.y = original_y

    def lock_piece(self):
        for r, row in enumerate(self.current_piece.matrix):
            for c, val in enumerate(row):
                if val:
                    target_y = self.current_piece.y + r
                    target_x = self.current_piece.x + c
                    if target_y >= 0:
                        self.grid[target_y][target_x] = self.current_piece.color
                        
        self.clear_lines()
        
        # Spawn next piece
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        self.has_held_this_turn = False
        
        # Check instant Game Over if new piece spawns in collision
        if self.check_collision(self.current_piece):
            self.game_over = True

    def hold_piece(self):
        if self.has_held_this_turn:
            return
            
        current_type = self.current_piece.type
        
        if self.held_piece_type is None:
            self.held_piece_type = current_type
            self.current_piece = self.next_piece
            self.next_piece = self.get_new_piece()
        else:
            prev_held = self.held_piece_type
            self.held_piece_type = current_type
            self.current_piece = Piece(prev_held)
            
        self.has_held_this_turn = True

    def get_ghost_y(self):
        # Calculate exactly where the piece would land
        ghost_y_offset = 0
        while not self.check_collision(self.current_piece, 0, ghost_y_offset + 1):
            ghost_y_offset += 1
        return self.current_piece.y + ghost_y_offset

    def hard_drop(self):
        ghost_y = self.get_ghost_y()
        drop_distance = ghost_y - self.current_piece.y
        self.current_piece.y = ghost_y
        self.score += drop_distance * 2
        
        # Trigger lock instantly
        self.lock_piece()
        
        # Trigger hard drop screen shake
        self.shake_duration = 8
        self.shake_amount = 5

    def move_down(self):
        if not self.check_collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
            self.score += 1
            return True
        else:
            self.lock_piece()
            return False

    def clear_lines(self):
        lines_to_clear = []
        for r in range(GRID_ROWS):
            if all(self.grid[r][c] is not None for c in range(GRID_COLS)):
                lines_to_clear.append(r)
                
        if not lines_to_clear:
            return
            
        # Spawn line-clear particles
        for r in lines_to_clear:
            y_pos = GRID_Y + r * BLOCK_SIZE + BLOCK_SIZE // 2
            for c in range(GRID_COLS):
                x_pos = GRID_X + c * BLOCK_SIZE + BLOCK_SIZE // 2
                color = self.grid[r][c]
                # Emit sparks
                for _ in range(5):
                    self.particles.append(SparkParticle(x_pos, y_pos, color))
                    
        # Remove lines and insert empty ones at top
        for r in lines_to_clear:
            self.grid.pop(r)
            self.grid.insert(0, [None for _ in range(GRID_COLS)])
            
        # Update Stats
        count = len(lines_to_clear)
        self.lines_cleared += count
        
        # Tetris scoring coefficients
        scoring = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += scoring.get(count, 800) * self.level
        
        # Increase level every 10 lines
        self.level = (self.lines_cleared // 10) + 1
        
        # Screen shake on multi-line clears
        self.shake_duration = count * 6
        self.shake_amount = count * 3

    def draw_grid_background(self, surface):
        # Draw central grid board background
        board_rect = pygame.Rect(GRID_X, GRID_Y, GRID_COLS * BLOCK_SIZE, GRID_ROWS * BLOCK_SIZE)
        pygame.draw.rect(surface, (15, 15, 26), board_rect)
        
        # Draw grid lines
        for r in range(GRID_ROWS + 1):
            pygame.draw.line(surface, GRID_LINE_COLOR, 
                             (GRID_X, GRID_Y + r * BLOCK_SIZE), 
                             (GRID_X + GRID_COLS * BLOCK_SIZE, GRID_Y + r * BLOCK_SIZE))
        for c in range(GRID_COLS + 1):
            pygame.draw.line(surface, GRID_LINE_COLOR, 
                             (GRID_X + c * BLOCK_SIZE, GRID_Y), 
                             (GRID_X + c * BLOCK_SIZE, GRID_Y + GRID_ROWS * BLOCK_SIZE))

        # Draw board neon borders
        pygame.draw.rect(surface, GRID_BORDER_COLOR, board_rect, 3, border_radius=3)

    def draw_block(self, surface, x, y, color, is_ghost=False):
        # Render a single block with neon highlights and gradients
        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        if is_ghost:
            # Ghost outline only
            pygame.draw.rect(surface, color, rect, 2, border_radius=4)
            # Faint center
            faint = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(faint, (*color, 35), (0, 0, BLOCK_SIZE, BLOCK_SIZE), border_radius=4)
            surface.blit(faint, (x, y))
        else:
            # Solid glowing neon block
            pygame.draw.rect(surface, color, rect, border_radius=4)
            # Inner lighter highlight
            highlight_color = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
            pygame.draw.rect(surface, highlight_color, (x + 3, y + 3, BLOCK_SIZE - 6, BLOCK_SIZE - 6), border_radius=2)
            # Edge border shadow
            pygame.draw.rect(surface, (0, 0, 0), rect, 1, border_radius=4)

    def draw_board_pieces(self, surface):
        # Draw locked blocks
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                color = self.grid[r][c]
                if color:
                    self.draw_block(surface, GRID_X + c * BLOCK_SIZE, GRID_Y + r * BLOCK_SIZE, color)

        # Draw Ghost piece projection
        if not self.game_over:
            ghost_y = self.get_ghost_y()
            for r, row in enumerate(self.current_piece.matrix):
                for c, val in enumerate(row):
                    if val:
                        target_y = ghost_y + r
                        target_x = self.current_piece.x + c
                        if target_y >= 0:
                            self.draw_block(surface, 
                                            GRID_X + target_x * BLOCK_SIZE, 
                                            GRID_Y + target_y * BLOCK_SIZE, 
                                            self.current_piece.color, 
                                            is_ghost=True)

        # Draw active moving piece
        if not self.game_over:
            for r, row in enumerate(self.current_piece.matrix):
                for c, val in enumerate(row):
                    if val:
                        target_y = self.current_piece.y + r
                        target_x = self.current_piece.x + c
                        if target_y >= 0:
                            self.draw_block(surface, 
                                            GRID_X + target_x * BLOCK_SIZE, 
                                            GRID_Y + target_y * BLOCK_SIZE, 
                                            self.current_piece.color)

    def draw_sidebars(self, surface):
        # 1. HOLD SIDEBAR (Left)
        hold_title = FONT_MEDIUM.render("HOLD", True, TEXT_COLOR)
        surface.blit(hold_title, (70, GRID_Y))
        
        hold_box = pygame.Rect(40, GRID_Y + 40, 140, 140)
        pygame.draw.rect(surface, (15, 15, 26), hold_box, border_radius=8)
        pygame.draw.rect(surface, GRID_BORDER_COLOR, hold_box, 2, border_radius=8)
        
        if self.held_piece_type:
            # Draw preview in hold box
            self.draw_preview_piece(surface, self.held_piece_type, 40, GRID_Y + 40, 140)

        # 2. NEXT SIDEBAR (Right)
        next_title = FONT_MEDIUM.render("NEXT", True, TEXT_COLOR)
        surface.blit(next_title, (WIDTH - 170, GRID_Y))
        
        next_box = pygame.Rect(WIDTH - 180, GRID_Y + 40, 140, 140)
        pygame.draw.rect(surface, (15, 15, 26), next_box, border_radius=8)
        pygame.draw.rect(surface, GRID_BORDER_COLOR, next_box, 2, border_radius=8)
        
        # Draw preview in next box
        self.draw_preview_piece(surface, self.next_piece.type, WIDTH - 180, GRID_Y + 40, 140)

        # 3. STATS PANEL (Right, below Next)
        stats_y = GRID_Y + 220
        
        # Score Box
        pygame.draw.rect(surface, (15, 15, 26), (WIDTH - 180, stats_y, 140, 75), border_radius=8)
        pygame.draw.rect(surface, GRID_BORDER_COLOR, (WIDTH - 180, stats_y, 140, 75), 1, border_radius=8)
        score_lbl = FONT_SMALL.render("SCORE", True, TEXT_COLOR)
        score_val = FONT_MEDIUM.render(str(self.score), True, WHITE)
        surface.blit(score_lbl, (WIDTH - 180 + 10, stats_y + 8))
        surface.blit(score_val, (WIDTH - 180 + 10, stats_y + 32))
        
        # Level Box
        pygame.draw.rect(surface, (15, 15, 26), (WIDTH - 180, stats_y + 95, 140, 75), border_radius=8)
        pygame.draw.rect(surface, GRID_BORDER_COLOR, (WIDTH - 180, stats_y + 95, 140, 75), 1, border_radius=8)
        level_lbl = FONT_SMALL.render("LEVEL", True, GOLD)
        level_val = FONT_MEDIUM.render(str(self.level), True, WHITE)
        surface.blit(level_lbl, (WIDTH - 180 + 10, stats_y + 95 + 8))
        surface.blit(level_val, (WIDTH - 180 + 10, stats_y + 95 + 32))

        # Lines Box
        pygame.draw.rect(surface, (15, 15, 26), (WIDTH - 180, stats_y + 190, 140, 75), border_radius=8)
        pygame.draw.rect(surface, GRID_BORDER_COLOR, (WIDTH - 180, stats_y + 190, 140, 75), 1, border_radius=8)
        lines_lbl = FONT_SMALL.render("LINES", True, TEXT_COLOR)
        lines_val = FONT_MEDIUM.render(str(self.lines_cleared), True, WHITE)
        surface.blit(lines_lbl, (WIDTH - 180 + 10, stats_y + 190 + 8))
        surface.blit(lines_val, (WIDTH - 180 + 10, stats_y + 190 + 32))

    def draw_preview_piece(self, surface, shape_type, box_x, box_y, box_size):
        # Draw centered preview tetromino inside hold/next box
        matrix = SHAPES[shape_type]
        color = SHAPE_COLORS[shape_type]
        
        pw = len(matrix[0])
        ph = len(matrix)
        
        # Scale block size slightly for small sidebars if needed
        prev_block_size = 22
        
        start_x = box_x + (box_size - (pw * prev_block_size)) // 2
        start_y = box_y + (box_size - (ph * prev_block_size)) // 2
        
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                if val:
                    rx = start_x + c * prev_block_size
                    ry = start_y + r * prev_block_size
                    rect = pygame.Rect(rx, ry, prev_block_size, prev_block_size)
                    pygame.draw.rect(surface, color, rect, border_radius=3)
                    pygame.draw.rect(surface, (0, 0, 0), rect, 1, border_radius=3)

    def draw_hud_header(self, surface):
        # Faint title header
        title_text = FONT_LARGE.render("NEON TETRIS", True, TEXT_COLOR)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 8))

    def draw_particles(self, surface):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
            else:
                p.draw(surface)

async def main():
    run = True
    clock = pygame.time.Clock()
    game = TetrisGame()
    
    # Timing/Gravity controls
    fall_time = 0
    
    # Keyboard repeat timings for smooth horizontal slider
    key_repeat_delay = 150
    key_repeat_rate = 50
    last_move_left = 0
    last_move_right = 0

    # Game state surface for screen shake
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    while run:
        # Dynamic speed calculation based on level (gravity speeds up)
        # Level 1 = 800ms per step, scaling down as level increases
        current_speed = max(60, 800 - (game.level - 1) * 80)
        
        # Clock ticks millisecond increments
        dt = clock.tick(60)
        
        if not game.game_over:
            fall_time += dt
            if fall_time >= current_speed:
                game.move_down()
                fall_time = 0
                
        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = TetrisGame()
                        fall_time = 0
                else:
                    if event.key in [pygame.K_UP, pygame.K_x, pygame.K_w]:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
                    elif event.key in [pygame.K_c, pygame.K_LSHIFT]:
                        game.hold_piece()

        # Continuous Keyboard Polling for fluid controls
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        if not game.game_over:
            # Horizontal Movement (with custom DAS/ARR style smooth scrolling)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if now - last_move_left > key_repeat_rate:
                    if not game.check_collision(game.current_piece, -1, 0):
                        game.current_piece.x -= 1
                    # Set a longer delay for the first tap
                    if last_move_left == 0:
                        last_move_left = now + key_repeat_delay
                    else:
                        last_move_left = now
            else:
                last_move_left = 0
                
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if now - last_move_right > key_repeat_rate:
                    if not game.check_collision(game.current_piece, 1, 0):
                        game.current_piece.x += 1
                    if last_move_right == 0:
                        last_move_right = now + key_repeat_delay
                    else:
                        last_move_right = now
            else:
                last_move_right = 0

            # Soft Drop (fast falling when holding down arrow)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                # Force rapid tick
                if fall_time > 40:
                    game.move_down()
                    fall_time = 0

        # Draw all elements to game surface
        game_surface.fill(DARK_BG)
        game.draw_grid_background(game_surface)
        game.draw_board_pieces(game_surface)
        game.draw_sidebars(game_surface)
        game.draw_hud_header(game_surface)
        game.draw_particles(game_surface)

        # Draw Game Over Overlay Screen
        if game.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 15, 210), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))
            
            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            pygame.draw.rect(game_surface, (255, 50, 50), over_rect, 3, border_radius=15)
            
            over_title = FONT_LARGE.render("GRID LOCKED", True, (255, 50, 50))
            final_score_text = FONT_MEDIUM.render(f"FINAL SCORE: {game.score}", True, WHITE)
            restart_hint = FONT_SMALL.render("PRESS 'R' TO RESTART", True, TEXT_COLOR)
            
            game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 30))
            game_surface.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 3 + 95))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 155))

        # Render Screen Shake offsets if active
        if game.shake_duration > 0:
            offset_x = random.randint(-game.shake_amount, game.shake_amount)
            offset_y = random.randint(-game.shake_amount, game.shake_amount)
            game.shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        # Blit game surface to actual window
        WIN.fill((0, 0, 0))
        WIN.blit(game_surface, (offset_x, offset_y))
        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
