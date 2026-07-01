import pygame
import random
import sys
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors (Neon Palette)
BG_COLOR = (10, 10, 18)
GRID_COLOR = (20, 20, 35)
SNAKE_HEAD = (0, 255, 150)
SNAKE_BODY_INNER = (0, 200, 100)
SNAKE_BODY_OUTER = (0, 100, 50)
FOOD_COLOR = (255, 0, 100)
FOOD_GLOW = (150, 0, 60)
TEXT_COLOR = (0, 200, 255)
UI_BORDER = (0, 150, 255)
WHITE = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)

# Set up display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake - Arcade Edition")

# Fonts
try:
    FONT_LARGE = pygame.font.SysFont("Outfit", 45, bold=True)
    FONT_MEDIUM = pygame.font.SysFont("Outfit", 30)
    FONT_SMALL = pygame.font.SysFont("Outfit", 20)
except:
    try:
        FONT_LARGE = pygame.font.SysFont("sans-serif", 45, bold=True)
        FONT_MEDIUM = pygame.font.SysFont("sans-serif", 30)
        FONT_SMALL = pygame.font.SysFont("sans-serif", 20)
    except:
        FONT_LARGE = pygame.font.Font(None, 45)
        FONT_MEDIUM = pygame.font.Font(None, 30)
        FONT_SMALL = pygame.font.Font(None, 20)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color):
        for _ in range(15):
            self.particles.append({
                "x": x + GRID_SIZE // 2,
                "y": y + GRID_SIZE // 2,
                "vx": random.uniform(-3.0, 3.0),
                "vy": random.uniform(-3.0, 3.0),
                "life": random.randint(15, 30),
                "max_life": 30,
                "color": color
            })

    def update(self):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            radius = int((p["life"] / p["max_life"]) * 4) + 1
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), radius)

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), 
                          (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                          (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = False

    def handle_keys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w] and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.key in [pygame.K_DOWN, pygame.K_s] and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.key in [pygame.K_LEFT, pygame.K_a] and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.key in [pygame.K_RIGHT, pygame.K_d] and self.direction != (-1, 0):
                self.next_direction = (1, 0)

    def update(self):
        self.direction = self.next_direction
        cur_head = self.positions[0]
        dx, dy = self.direction
        new_head = (cur_head[0] + dx, cur_head[1] + dy)
        
        # Check wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            return False
            
        # Check self collision
        if new_head in self.positions:
            return False
            
        self.positions.insert(0, new_head)
        if not self.grow_pending:
            self.positions.pop()
        else:
            self.grow_pending = False
        return True

    def grow(self):
        self.grow_pending = True

    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            
            if i == 0:
                # Head: Neon mint with eyes
                pygame.draw.rect(surface, SNAKE_HEAD, rect, border_radius=4)
                # Draw small eyes
                eye_color = (0, 0, 0)
                dx, dy = self.direction
                if dx != 0:
                    pygame.draw.circle(surface, eye_color, (x + GRID_SIZE // 2, y + 6), 2)
                    pygame.draw.circle(surface, eye_color, (x + GRID_SIZE // 2, y + 14), 2)
                else:
                    pygame.draw.circle(surface, eye_color, (x + 6, y + GRID_SIZE // 2), 2)
                    pygame.draw.circle(surface, eye_color, (x + 14, y + GRID_SIZE // 2), 2)
            else:
                # Body: Gradient green
                factor = min(1.0, i / len(self.positions))
                color = (
                    int(SNAKE_BODY_INNER[0] * (1 - factor) + SNAKE_BODY_OUTER[0] * factor),
                    int(SNAKE_BODY_INNER[1] * (1 - factor) + SNAKE_BODY_OUTER[1] * factor),
                    int(SNAKE_BODY_INNER[2] * (1 - factor) + SNAKE_BODY_OUTER[2] * factor)
                )
                pygame.draw.rect(surface, color, rect, border_radius=6)
                pygame.draw.rect(surface, SNAKE_HEAD, (x + 4, y + 4, GRID_SIZE - 8, GRID_SIZE - 8), border_radius=3)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position([])
        self.pulse = 0
        self.pulse_dir = 1

    def randomize_position(self, snake_positions):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_positions:
                self.position = pos
                break

    def draw(self, surface):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        
        # Animate glowing pulse
        self.pulse += 0.2 * self.pulse_dir
        if self.pulse > 3 or self.pulse < 0:
            self.pulse_dir *= -1
            
        radius = GRID_SIZE // 2 - 2 + int(self.pulse)
        # Outer neon glow
        pygame.draw.circle(surface, FOOD_GLOW, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), radius + 4)
        # Inner core
        pygame.draw.circle(surface, FOOD_COLOR, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), radius - 1)
        # Center white sparkle
        pygame.draw.circle(surface, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 2)

def draw_grid(surface):
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

def submit_score(score):
    print(f"Game over. Final Score: {score}")
    import sys
    try:
        import arcade_api
    except ImportError:
        sys.path.append("..")
        try:
            import arcade_api
        except ImportError:
            arcade_api = None

    if arcade_api:
        arcade_api.submit_score("Snake", score)
    else:
        print("[Snake] arcade_api not found, score not submitted.")

def get_obstacles(level):
    obstacles = []
    if level == 1:
        pass
    elif level == 2:
        for offset in range(3):
            obstacles.extend([(3 + offset, 4), (4, 4 + offset)])
            obstacles.extend([(GRID_WIDTH - 5 - offset, 4), (GRID_WIDTH - 5, 4 + offset)])
            obstacles.extend([(3 + offset, GRID_HEIGHT - 5), (4, GRID_HEIGHT - 5 - offset)])
            obstacles.extend([(GRID_WIDTH - 5 - offset, GRID_HEIGHT - 5), (GRID_WIDTH - 5, GRID_HEIGHT - 5 - offset)])
    else:
        # Procedural blocks
        random.seed(level * 37)
        num_pillars = min(10, level // 2 + 1)
        for _ in range(num_pillars):
            px = random.randint(5, GRID_WIDTH - 6)
            py = random.randint(5, GRID_HEIGHT - 6)
            length = random.randint(2, 5)
            direction = random.choice([(1,0), (0,1)])
            for i in range(length):
                obstacles.append((px + direction[0]*i, py + direction[1]*i))
    # Filter head spawn area
    obstacles = list(set(obstacles))
    obstacles = [o for o in obstacles if abs(o[0] - GRID_WIDTH//2) > 4 or abs(o[1] - GRID_HEIGHT//2) > 4]
    return obstacles

async def main():
    run = True
    clock = pygame.time.Clock()
    
    snake = Snake()
    food = Food()
    particles = ParticleSystem()
    
    score = 0
    high_score = 0
    level = 1
    max_levels = 20
    food_eaten = 0
    game_won = False
    game_over = False
    score_submitted = False
    
    obstacles = get_obstacles(level)
    food.randomize_position(snake.positions)
    while food.position in obstacles:
        food.randomize_position(snake.positions)
        
    base_speed = 6
    speed = base_speed + level // 2
    
    def trigger_eat_effect():
        fx = food.position[0] * GRID_SIZE
        fy = food.position[1] * GRID_SIZE
        particles.emit(fx, fy, FOOD_COLOR)
        particles.emit(fx, fy, SNAKE_HEAD)
        
    while run:
        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        level = 1
                        food_eaten = 0
                        game_won = False
                        snake.reset()
                        obstacles = get_obstacles(level)
                        food.randomize_position(snake.positions)
                        while food.position in obstacles:
                            food.randomize_position(snake.positions)
                        score = 0
                        speed = base_speed + level // 2
                        game_over = False
                        score_submitted = False
                    elif event.key == pygame.K_q:
                        run = False
                else:
                    snake.handle_keys(event)

        # Game update logic
        if not game_over:
            # Move snake
            alive = snake.update()
            if not alive or snake.positions[0] in obstacles:
                game_over = True
            
            # Check food consumption
            if not game_over and snake.positions[0] == food.position:
                snake.grow()
                trigger_eat_effect()
                score += 10
                food_eaten += 1
                if score > high_score:
                    high_score = score
                
                # Check level clear
                target_food = 5 + level
                if food_eaten >= target_food:
                    if level >= max_levels:
                        game_won = True
                        game_over = True
                    else:
                        # Level Clear Screen Overlay
                        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        pygame.draw.rect(overlay, (5, 5, 10, 220), (0, 0, WIDTH, HEIGHT))
                        WIN.blit(overlay, (0, 0))
                        
                        panel_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
                        pygame.draw.rect(WIN, (15, 15, 25), panel_rect, border_radius=15)
                        pygame.draw.rect(WIN, SNAKE_HEAD, panel_rect, 3, border_radius=15)
                        
                        title = FONT_LARGE.render(f"LEVEL {level} CLEARED", True, SNAKE_HEAD)
                        sub = FONT_MEDIUM.render("NEXT GRID SECTOR INCOMING...", True, WHITE)
                        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
                        WIN.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))
                        
                        pygame.display.flip()
                        await asyncio.sleep(2.0)
                        
                        level += 1
                        food_eaten = 0
                        snake.reset()
                        obstacles = get_obstacles(level)
                        food.randomize_position(snake.positions)
                        while food.position in obstacles:
                            food.randomize_position(snake.positions)
                        speed = base_speed + level // 2
                        continue
                
                food.randomize_position(snake.positions)
                while food.position in obstacles:
                    food.randomize_position(snake.positions)
            
            particles.update()
        else:
            if not score_submitted:
                submit_score(score)
                score_submitted = True

        # Render
        WIN.fill(BG_COLOR)
        draw_grid(WIN)
        
        # Draw obstacles
        for obs in obstacles:
            ox = obs[0] * GRID_SIZE
            oy = obs[1] * GRID_SIZE
            rect = pygame.Rect(ox, oy, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(WIN, UI_BORDER, rect, border_radius=4)
            pygame.draw.rect(WIN, WHITE, (ox + 3, oy + 3, GRID_SIZE - 6, GRID_SIZE - 6), border_radius=2)
            
        # Draw game elements
        food.draw(WIN)
        snake.draw(WIN)
        particles.draw(WIN)
        
        # Draw Score / HUD
        score_text = FONT_MEDIUM.render(f"SCORE: {score}", True, TEXT_COLOR)
        level_text = FONT_MEDIUM.render(f"LEVEL: {level}/20", True, WHITE)
        
        hud_panel = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        pygame.draw.rect(hud_panel, (10, 10, 20, 180), (0, 0, WIDTH, 40))
        WIN.blit(hud_panel, (0, 0))
        pygame.draw.line(WIN, UI_BORDER, (0, 40), (WIDTH, 40), 2)
        
        WIN.blit(score_text, (20, 5))
        WIN.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 5))
        
        # Game Over Screen Overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 10, 200), (0, 0, WIDTH, HEIGHT))
            WIN.blit(overlay, (0, 0))
            
            panel_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
            pygame.draw.rect(WIN, (15, 15, 25), panel_rect, border_radius=15)
            
            if game_won:
                pygame.draw.rect(WIN, SNAKE_HEAD, panel_rect, 3, border_radius=15)
                title = FONT_LARGE.render("GRID MASTER", True, SNAKE_HEAD)
                score_summary = FONT_MEDIUM.render(f"VICTORY SCORE: {score}", True, WHITE)
            else:
                pygame.draw.rect(WIN, FOOD_COLOR, panel_rect, 3, border_radius=15)
                title = FONT_LARGE.render("GAME OVER", True, FOOD_COLOR)
                score_summary = FONT_MEDIUM.render(f"FINAL SCORE: {score}", True, WHITE)
                
            restart_instruction = FONT_SMALL.render("PRESS 'R' TO REPLAY", True, TEXT_COLOR)
            quit_instruction = FONT_SMALL.render("PRESS 'Q' TO QUIT", True, TEXT_COLOR)
            
            WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
            WIN.blit(score_summary, (WIDTH // 2 - score_summary.get_width() // 2, HEIGHT // 2 - 20))
            WIN.blit(restart_instruction, (WIDTH // 2 - restart_instruction.get_width() // 2, HEIGHT // 2 + 40))
            WIN.blit(quit_instruction, (WIDTH // 2 - quit_instruction.get_width() // 2, HEIGHT // 2 + 70))
            
        pygame.display.flip()
        
        clock.tick(speed if not game_over else 15)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
