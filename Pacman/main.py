import pygame
import asyncio
import random
import math
import sys
import os

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
WIDTH, HEIGHT = 760, 700  # 19 columns * 40px, 15 rows * 40px + 100px HUD
GRID_SIZE = 40
HUD_HEIGHT = 100
ROWS, COLS = 15, 19

# Screen Mode
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Pac-Man - Arcade Edition")

# Colors
DARK_BG = (8, 8, 16)
NEON_BLUE = (0, 200, 255)
NEON_YELLOW = (255, 230, 0)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
NEON_PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# Ghost Colors
GHOST_COLORS = [
    (255, 0, 0),     # Blinky - Red
    (255, 150, 200), # Pinky - Pink
    (0, 255, 255),   # Inky - Cyan
    (255, 150, 0)    # Clyde - Orange
]

# Fonts
try:
    FONT_HUD = pygame.font.SysFont("Outfit", 20, bold=True)
    FONT_LARGE = pygame.font.SysFont("Outfit", 50, bold=True)
except:
    try:
        FONT_HUD = pygame.font.SysFont("Segoe UI", 20, bold=True)
        FONT_LARGE = pygame.font.SysFont("Segoe UI", 50, bold=True)
    except:
        FONT_HUD = pygame.font.Font(None, 20)
        FONT_LARGE = pygame.font.Font(None, 50)

FPS = 60

# Symmetrical arcade Pac-Man maze (15 rows, 19 cols)
# 1 = Wall, 0 = Pellet, 2 = Power Pellet, 3 = Empty
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,3,3,3,1,1,1,0,1,1,1,1],
    [3,3,3,1,0,1,3,3,3,3,3,3,3,1,0,1,3,3,3],
    [1,1,1,1,0,1,3,1,1,1,1,1,3,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,1,3,3,3,1,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,2,0,1,0,0,0,0,0,3,0,0,0,0,0,1,0,2,1],
    [1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]


class EatParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = random.randint(10, 20)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 3) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class PacmanPlayer:
    def __init__(self):
        self.grid_x = 9
        self.grid_y = 10
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + HUD_HEIGHT
        
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        
        self.speed = 3
        self.angle = 0
        self.mouth_flap = 0
        self.mouth_dir = 1

    def handle_keys(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_dir_x, self.next_dir_y = -1, 0
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_dir_x, self.next_dir_y = 1, 0
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_dir_x, self.next_dir_y = 0, -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_dir_x, self.next_dir_y = 0, 1

    def get_center_grid_pixel(self, gx, gy):
        px = gx * GRID_SIZE + GRID_SIZE // 2
        py = gy * GRID_SIZE + GRID_SIZE // 2 + HUD_HEIGHT
        return px, py

    def update(self, maze):
        # Flap mouth
        self.mouth_flap += 0.15 * self.mouth_dir
        if self.mouth_flap > 1.0 or self.mouth_flap < 0.1:
            self.mouth_dir *= -1

        # Check if we are aligned with a grid tile center to allow direction changes
        cur_pixel_x, cur_pixel_y = self.get_center_grid_pixel(self.grid_x, self.grid_y)
        
        dist_x = abs(self.x - cur_pixel_x)
        dist_y = abs(self.y - cur_pixel_y)
        
        if dist_x < self.speed and dist_y < self.speed:
            # Snap to grid center
            self.x, self.y = cur_pixel_x, cur_pixel_y
            
            # Can we turn to next direction?
            next_gx = self.grid_x + self.next_dir_x
            next_gy = self.grid_y + self.next_dir_y
            if 0 <= next_gx < COLS and 0 <= next_gy < ROWS and maze[next_gy][next_gx] != 1:
                self.dir_x, self.dir_y = self.next_dir_x, self.next_dir_y
            
            # Can we continue moving in current direction?
            future_gx = self.grid_x + self.dir_x
            future_gy = self.grid_y + self.dir_y
            if 0 <= future_gx < COLS and 0 <= future_gy < ROWS and maze[future_gy][future_gx] != 1:
                self.grid_x = future_gx
                self.grid_y = future_gy
            else:
                self.dir_x, self.dir_y = 0, 0 # stop on wall

        # Smooth pixel sliding movement
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        
        # Warp tunnel edges
        if self.x < 0:
            self.x = WIDTH
            self.grid_x = COLS - 1
        elif self.x > WIDTH:
            self.x = 0
            self.grid_x = 0

    def draw(self, surface):
        # Draw mouth pie slice based on direction
        # angle calculation
        heading = 0
        if self.dir_x == 1: heading = 0
        elif self.dir_y == 1: heading = 270
        elif self.dir_x == -1: heading = 180
        elif self.dir_y == -1: heading = 90
        
        radius = GRID_SIZE // 2 - 2
        
        # Simple procedural Pacman drawing
        pygame.draw.circle(surface, NEON_YELLOW, (int(self.x), int(self.y)), radius)
        
        # Draw mouth pie cut-out (draw dark wedge in heading direction)
        mouth_angle = self.mouth_flap * 45
        rad_h = math.radians(heading)
        rad_p = math.radians(heading + mouth_angle)
        rad_m = math.radians(heading - mouth_angle)
        
        p1 = (self.x, self.y)
        p2 = (self.x + math.cos(rad_p) * (radius + 2), self.y - math.sin(rad_p) * (radius + 2))
        p3 = (self.x + math.cos(rad_m) * (radius + 2), self.y - math.sin(rad_m) * (radius + 2))
        
        pygame.draw.polygon(surface, DARK_BG, [p1, p2, p3])


class PacmanGhost:
    def __init__(self, index, color, level=1):
        self.index = index
        self.color = color
        self.grid_x = 8 + index % 3
        self.grid_y = 8
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + HUD_HEIGHT
        
        self.dir_x = 0
        self.dir_y = 0
        # Speed scales with level, capped at 3.6
        self.speed = min(3.6, 2.0 + (level - 1) * 0.1)
        self.scared = False
        
        self.target_gx = 0
        self.target_gy = 0

    def snap_to_grid(self):
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + HUD_HEIGHT

    def select_next_move(self, maze):
        # Pick a valid move (excluding backward if possible, unless dead-end)
        valid_dirs = []
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dx, dy in possible_moves:
            # Prevent instant reversal to avoid jittering
            if dx == -self.dir_x and dy == -self.dir_y:
                continue
            gx = self.grid_x + dx
            gy = self.grid_y + dy
            if 0 <= gx < COLS and 0 <= gy < ROWS and maze[gy][gx] != 1:
                valid_dirs.append((dx, dy))
                
        # If dead end, allow backward
        if not valid_dirs:
            backward_x, backward_y = -self.dir_x, -self.dir_y
            bgx = self.grid_x + backward_x
            bgy = self.grid_y + backward_y
            if 0 <= bgx < COLS and 0 <= bgy < ROWS and maze[bgy][bgx] != 1:
                valid_dirs.append((backward_x, backward_y))
                
        if valid_dirs:
            # Choose randomly or target-based
            self.dir_x, self.dir_y = random.choice(valid_dirs)

    def update(self, maze):
        cur_pixel_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        cur_pixel_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + HUD_HEIGHT
        
        dist_x = abs(self.x - cur_pixel_x)
        dist_y = abs(self.y - cur_pixel_y)
        
        if dist_x < self.speed and dist_y < self.speed:
            self.x, self.y = cur_pixel_x, cur_pixel_y
            self.select_next_move(maze)
            self.grid_x += self.dir_x
            self.grid_y += self.dir_y

        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        
        # Wrap tunnel edges
        if self.x < 0:
            self.x = WIDTH
            self.grid_x = COLS - 1
        elif self.x > WIDTH:
            self.x = 0
            self.grid_x = 0

    def draw(self, surface):
        radius = GRID_SIZE // 2 - 3
        
        # Determine color (Scared state: flashing dark blue/white)
        color = self.color
        if self.scared:
            t = pygame.time.get_ticks()
            color = (0, 0, 255) if (t // 200) % 2 == 0 else (200, 200, 255)
            
        # Draw dome top
        pygame.draw.circle(surface, color, (int(self.x), int(self.y - 2)), radius)
        # Draw body rect
        pygame.draw.rect(surface, color, (self.x - radius, self.y - 2, radius * 2, radius))
        
        # Draw squiggly feet base (simple triangles)
        p1 = (self.x - radius, self.y + radius - 2)
        p2 = (self.x - radius + 6, self.y + radius + 4)
        p3 = (self.x, self.y + radius - 2)
        p4 = (self.x + radius - 6, self.y + radius + 4)
        p5 = (self.x + radius, self.y + radius - 2)
        pygame.draw.polygon(surface, color, [p1, p2, p3, p4, p5])

        # Draw eyes (looking in direction)
        eye_offset_x = self.dir_x * 3
        eye_offset_y = self.dir_y * 3
        
        pygame.draw.circle(surface, WHITE, (int(self.x - 5 + eye_offset_x), int(self.y - 4 + eye_offset_y)), 4)
        pygame.draw.circle(surface, WHITE, (int(self.x + 5 + eye_offset_x), int(self.y - 4 + eye_offset_y)), 4)
        
        # Pupils
        pygame.draw.circle(surface, (0, 0, 100) if self.scared else (0, 0, 0), 
                           (int(self.x - 5 + eye_offset_x * 1.5), int(self.y - 4 + eye_offset_y * 1.5)), 2)
        pygame.draw.circle(surface, (0, 0, 100) if self.scared else (0, 0, 0), 
                           (int(self.x + 5 + eye_offset_x * 1.5), int(self.y - 4 + eye_offset_y * 1.5)), 2)


class PacmanGame:
    def __init__(self):
        self.maze = [list(row) for row in MAZE]
        self.player = PacmanPlayer()
        self.ghosts = [PacmanGhost(i, GHOST_COLORS[i], 1) for i in range(4)]
        self.particles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_won = False
        self.game_over = False
        self.score_submitted = False
        self.scared_timer = 0
        
        self.shake_duration = 0
        self.shake_amount = 0

    def draw_maze(self, surface):
        for r in range(ROWS):
            for c in range(COLS):
                val = self.maze[r][c]
                x = c * GRID_SIZE
                y = r * GRID_SIZE + HUD_HEIGHT
                
                if val == 1:
                    # Glowing blue neon walls
                    pygame.draw.rect(surface, (10, 20, 52), (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4), border_radius=6)
                    pygame.draw.rect(surface, NEON_BLUE, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4), 1, border_radius=6)
                elif val == 0:
                    # Regular dot pellet
                    pygame.draw.circle(surface, GOLD, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 3)
                elif val == 2:
                    # Big pulsing power pellet
                    t = pygame.time.get_ticks()
                    pulse_radius = 6 + int(math.sin(t * 0.01) * 2)
                    pygame.draw.circle(surface, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), pulse_radius)

    def count_pellets(self):
        return sum(row.count(0) + row.count(2) for row in self.maze)

    def check_collisions(self):
        # 1. Eat pellets
        player_grid_x = int(self.player.x // GRID_SIZE)
        player_grid_y = int((self.player.y - HUD_HEIGHT) // GRID_SIZE)
        
        if 0 <= player_grid_x < COLS and 0 <= player_grid_y < ROWS:
            cell_val = self.maze[player_grid_y][player_grid_x]
            
            if cell_val == 0:
                # Eat regular pellet
                self.maze[player_grid_y][player_grid_x] = 3
                self.score += 10
                # Spawn eat spark particles
                for _ in range(3):
                    self.particles.append(EatParticle(self.player.x, self.player.y, GOLD))
                    
            elif cell_val == 2:
                # Eat power pellet
                self.maze[player_grid_y][player_grid_x] = 3
                self.score += 50
                # Power pellet eaten!
                self.scared_timer = max(60, 360 - self.level * 15)
                self.score += 50
                for ghost in self.ghosts:
                    ghost.scared = True
                    # Scared ghost speed decreases
                    ghost.speed = 1.2
                self.maze[self.player.grid_y][self.player.grid_x] = 3
                # Spark particles
                for _ in range(12):
                    self.particles.append(EatParticle(self.player.x, self.player.y, NEON_GREEN))
                # Small shake
                self.shake_duration = 10
                self.shake_amount = 4

        # 2. Collision with ghosts
        for ghost in self.ghosts:
            if math.hypot(self.player.x - ghost.x, self.player.y - ghost.y) < GRID_SIZE - 8:
                if ghost.scared:
                    # Pacman eats ghost!
                    self.score += 200
                    ghost.scared = False
                    ghost.speed = 2
                    ghost.grid_x, ghost.grid_y = 9, 7
                    ghost.snap_to_grid()
                    # Spark particles
                    for _ in range(20):
                        self.particles.append(EatParticle(ghost.x, ghost.y, ghost.color))
                    self.shake_duration = 15
                    self.shake_amount = 7
                else:
                    # Ghost eats Pacman!
                    self.lives -= 1
                    self.shake_duration = 30
                    self.shake_amount = 12
                    
                    # Explosion debris
                    for _ in range(25):
                        self.particles.append(EatParticle(self.player.x, self.player.y, NEON_YELLOW))
                    
                    if self.lives > 0:
                        # Respawn
                        self.player = PacmanPlayer()
                        for i, g in enumerate(self.ghosts):
                            g.__init__(i, GHOST_COLORS[i], self.level)
                    else:
                        self.game_over = True
                    break

    def draw_hud(self, surface):
        # Draw glass HUD panel
        hud_rect = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, (12, 12, 24), hud_rect)
        pygame.draw.line(surface, NEON_BLUE, (0, HUD_HEIGHT - 2), (WIDTH, HUD_HEIGHT - 2), 3)

        # Draw Score
        score_lbl = FONT_HUD.render("SCORE", True, NEON_BLUE)
        score_val = FONT_HUD.render(str(self.score), True, WHITE)
        surface.blit(score_lbl, (30, 20))
        surface.blit(score_val, (30, 45))

        # Draw Scared Timer Gauge
        if self.scared_timer > 0:
            timer_lbl = FONT_HUD.render("POWER GAUGE", True, NEON_GREEN)
            surface.blit(timer_lbl, (WIDTH // 2 - timer_lbl.get_width() // 2, 20))
            
            gauge_w = int(200 * (self.scared_timer / 360.0))
            pygame.draw.rect(surface, (25, 25, 45), (WIDTH // 2 - 100, 48, 200, 10), border_radius=3)
            pygame.draw.rect(surface, NEON_GREEN, (WIDTH // 2 - 100, 48, gauge_w, 10), border_radius=3)

        # Draw Lives
        lives_lbl = FONT_HUD.render("CORE LIVES", True, NEON_PINK)
        lives_val = FONT_HUD.render("O " * self.lives if self.lives > 0 else "CRITICAL", True, WHITE)
        surface.blit(lives_lbl, (WIDTH - lives_lbl.get_width() - 30, 20))
        surface.blit(lives_val, (WIDTH - lives_val.get_width() - 30, 45))

        # Draw level stage
        level_lbl = FONT_HUD.render(f"STAGE {self.level}/20", True, GOLD)
        surface.blit(level_lbl, (WIDTH // 2 - level_lbl.get_width() // 2, 20))


async def main():
    run = True
    clock = pygame.time.Clock()
    game = PacmanGame()
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
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = PacmanGame()

        if not game.game_over:
            # Control keys polling
            keys = pygame.key.get_pressed()
            game.player.handle_keys(keys)
            
            # Update objects
            game.player.update(game.maze)
            for ghost in game.ghosts:
                ghost.update(game.maze)
                
            # Manage scared timer
            if game.scared_timer > 0:
                game.scared_timer -= 1
                if game.scared_timer == 0:
                    for ghost in game.ghosts:
                        ghost.scared = False
                        ghost.speed = 2
            
            # Collisions and eating
            game.check_collisions()
            
            # Check level completion (no dots left)
            if game.count_pellets() == 0:
                if game.level >= 20:
                    game.game_won = True
                    game.game_over = True
                    if not game.score_submitted:
                        game.score_submitted = True
                        if arcade_api:
                            arcade_api.submit_score("Neon Pac-Man", game.score + 5000)
                else:
                    # Transition overlay
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
                    game_surface.blit(overlay, (0, 0))

                    card_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
                    pygame.draw.rect(game_surface, (15, 15, 30), card_rect, border_radius=15)
                    pygame.draw.rect(game_surface, NEON_GREEN, card_rect, 3, border_radius=15)

                    title = FONT_LARGE.render(f"STAGE {game.level} CLEARED!", True, NEON_GREEN)
                    sub = FONT_HUD.render("PREPARING SYSTEM INCOMING GRID...", True, WHITE)
                    game_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 + 35))
                    game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 3 + 105))

                    WIN.fill((0, 0, 0))
                    WIN.blit(game_surface, (0, 0))
                    pygame.display.update()

                    await asyncio.sleep(2.5)

                    game.maze = [list(row) for row in MAZE]
                    game.level += 1
                    game.player = PacmanPlayer()
                    for i, ghost in enumerate(game.ghosts):
                        ghost.__init__(i, GHOST_COLORS[i], game.level)
                    game.particles.clear()
                    game.shake_duration = 20
                    game.shake_amount = 6

        # Draw
        game_surface.fill(DARK_BG)
        game.draw_maze(game_surface)
        
        # Draw particles
        for p in game.particles:
            p.draw(game_surface)

        # Draw Pacman and Ghosts
        if not game.game_over and game.player.speed > 0:
            game.player.draw(game_surface)
            for ghost in game.ghosts:
                ghost.draw(game_surface)

        # Draw HUD
        game.draw_hud(game_surface)

        # Draw Game Over Banner
        if game.game_over:
            if not game.score_submitted:
                game.score_submitted = True
                if arcade_api:
                    arcade_api.submit_score("Neon Pac-Man", game.score)
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            
            if game.game_won:
                pygame.draw.rect(game_surface, NEON_GREEN, over_rect, 3, border_radius=15)
                over_title = FONT_LARGE.render("GRID MASTER", True, NEON_GREEN)
                final_lbl = FONT_HUD.render(f"VICTORY SCORE: {game.score}", True, WHITE)
            else:
                pygame.draw.rect(game_surface, NEON_PINK, over_rect, 3, border_radius=15)
                over_title = FONT_LARGE.render("SYSTEM CRITICAL", True, NEON_PINK)
                final_lbl = FONT_HUD.render(f"FINAL SCORE: {game.score}", True, WHITE)
                
            restart_hint = FONT_HUD.render("PRESS 'R' TO REBOOT CORE", True, NEON_BLUE)

            game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 35))
            game_surface.blit(final_lbl, (WIDTH // 2 - final_lbl.get_width() // 2, HEIGHT // 3 + 105))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 150))

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
