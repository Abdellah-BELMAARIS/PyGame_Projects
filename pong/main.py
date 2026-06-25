import pygame
import asyncio
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - Neon Cyberpunk Edition")

FPS = 60

# Neon Color Palette
DARK_BG = (10, 10, 18)
GRID_COLOR = (20, 20, 35)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_RADIUS = 8
WINNING_SCORE = 10

# Load fonts
try:
    SCORE_FONT = pygame.font.SysFont("Outfit", 50, bold=True)
    MESSAGE_FONT = pygame.font.SysFont("Outfit", 40, bold=True)
except:
    try:
        SCORE_FONT = pygame.font.SysFont("Segoe UI", 50, bold=True)
        MESSAGE_FONT = pygame.font.SysFont("Segoe UI", 40, bold=True)
    except:
        SCORE_FONT = pygame.font.SysFont("sans-serif", 50, bold=True)
        MESSAGE_FONT = pygame.font.SysFont("sans-serif", 40, bold=True)

# Particle Spark for Hits
class HitSpark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4.0, 4.0)
        self.vy = random.uniform(-4.0, 4.0)
        self.life = random.randint(15, 25)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 3) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

class Paddle:
    VEL = 5

    def __init__(self, x, y, width, height, color):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, win):
        # Draw main glowing paddle body
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), border_radius=4)
        
        # Outer glow layers
        glow_color = (max(0, self.color[0]-50), max(0, self.color[1]-50), max(0, self.color[2]-50))
        for offset in range(1, 4):
            pygame.draw.rect(
                win, 
                glow_color, 
                (self.x - offset, self.y - offset, self.width + offset*2, self.height + offset*2), 
                1, 
                border_radius=4 + offset
            )

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    MAX_VEL = 9

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL if random.choice([True, False]) else -self.MAX_VEL
        self.y_vel = random.uniform(-2, 2)
        self.trail = []

    def draw(self, win):
        # Draw fading neon trail
        for i, pos in enumerate(self.trail):
            factor = (i + 1) / len(self.trail)
            radius = int(self.radius * factor * 0.9)
            color = (
                int(NEON_GREEN[0] * factor),
                int(NEON_GREEN[1] * factor),
                int(NEON_GREEN[2] * factor)
            )
            pygame.draw.circle(win, color, (int(pos[0]), int(pos[1])), radius)

        # Draw ball core
        pygame.draw.circle(win, NEON_GREEN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(win, WHITE, (int(self.x), int(self.y)), self.radius - 3)

    def move(self):
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)
            
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = random.uniform(-2.0, 2.0)
        self.x_vel = self.MAX_VEL if self.x_vel < 0 else -self.MAX_VEL
        self.trail.clear()

def draw_neon_grid(surface):
    surface.fill(DARK_BG)
    
    # Grid lines
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))
        
    # Divider line
    for i in range(10, HEIGHT, HEIGHT // 15):
        if i % 2 == 1:
            continue
        pygame.draw.rect(surface, (50, 50, 80), (WIDTH // 2 - 2, i, 4, HEIGHT // 15), border_radius=2)

def draw(win, paddles, ball, left_score, right_score, sparks):
    draw_neon_grid(win)

    # Draw Scores with a futuristic glowing style
    left_score_text = SCORE_FONT.render(f"{left_score}", 1, NEON_BLUE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, NEON_PINK)
    
    # Slight shadow/glow effect
    left_glow = SCORE_FONT.render(f"{left_score}", 1, (0, 100, 150))
    right_glow = SCORE_FONT.render(f"{right_score}", 1, (150, 0, 80))
    
    win.blit(left_glow, (WIDTH // 4 - left_score_text.get_width() // 2 + 2, 22))
    win.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
    
    win.blit(right_glow, (WIDTH * (3/4) - right_score_text.get_width() // 2 + 2, 22))
    win.blit(right_score_text, (WIDTH * (3/4) - right_score_text.get_width() // 2, 20))

    for paddle in paddles:
        paddle.draw(win)

    ball.draw(win)

    for spark in sparks:
        spark.draw(win)

    pygame.display.update()

def handle_collision(ball, left_paddle, right_paddle, sparks):
    # Bounce top and bottom
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.y_vel *= -1
        # Wall bounce sparks
        for _ in range(5):
            sparks.append(HitSpark(ball.x, ball.y - ball.radius, NEON_GREEN))
    elif ball.y + ball.radius >= HEIGHT:
        ball.y = HEIGHT - ball.radius
        ball.y_vel *= -1
        # Wall bounce sparks
        for _ in range(5):
            sparks.append(HitSpark(ball.x, ball.y + ball.radius, NEON_GREEN))

    # Ball left movement check (Paddle 1)
    if ball.x_vel < 0:
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                ball.x_vel *= -1
                
                # Dynamic physics bounce angle based on hit location
                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
                
                # Sparks
                for _ in range(12):
                    sparks.append(HitSpark(ball.x - ball.radius, ball.y, NEON_BLUE))
    else:
        # Ball right movement check (Paddle 2)
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1
                
                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
                
                # Sparks
                for _ in range(12):
                    sparks.append(HitSpark(ball.x + ball.radius, ball.y, NEON_PINK))

def handle_paddle_movement(keys, left_paddle, right_paddle):
    # Left Paddle controls: W / S
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT:
        left_paddle.move(up=False)

    # Right Paddle controls: Arrow keys
    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)

async def main():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(15, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, NEON_BLUE)
    right_paddle = Paddle(WIDTH - 15 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, NEON_PINK)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0
    
    sparks = []
    
    # Screen shake parameters
    shake_duration = 0
    shake_amount = 0
    
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    while run:
        clock.tick(FPS)
        
        # Draw everything to game surface
        draw(game_surface, [left_paddle, right_paddle], ball, left_score, right_score, sparks)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle, sparks)

        # Update sparks
        for spark in sparks[:]:
            spark.update()
            if spark.life <= 0:
                sparks.remove(spark)

        # Score checks
        if ball.x < 0:
            right_score += 1
            ball.reset()
            # Trigger screen shake
            shake_duration = 15
            shake_amount = 8
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()
            # Trigger screen shake
            shake_duration = 15
            shake_amount = 8

        # Check Winner
        won = False
        if left_score >= WINNING_SCORE:
            won = True
            win_text = "BLUE PLAYER WINS!"
            win_color = NEON_BLUE
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "PINK PLAYER WINS!"
            win_color = NEON_PINK

        if won:
            # Render Winner Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 15, 220), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))
            
            # Winner Banner
            banner_rect = pygame.Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3)
            pygame.draw.rect(game_surface, (15, 15, 30), banner_rect, border_radius=15)
            pygame.draw.rect(game_surface, win_color, banner_rect, 3, border_radius=15)
            
            text = MESSAGE_FONT.render(win_text, 1, win_color)
            shadow_text = MESSAGE_FONT.render(win_text, 1, (10, 10, 10))
            restart_hint = MESSAGE_FONT.render("RESETTING GAME...", 1, WHITE)
            
            game_surface.blit(shadow_text, (WIDTH // 2 - text.get_width() // 2 + 2, HEIGHT // 2 - 40 + 2))
            game_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 2 + 20))
            
            # Draw it to main screen and pause
            WIN.fill((0, 0, 0))
            WIN.blit(game_surface, (0, 0))
            pygame.display.update()
            
            await asyncio.sleep(4)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0

        # Handle screen shake offset
        if shake_duration > 0:
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
            shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        # Blit the game surface to window with shake offset
        WIN.fill((0, 0, 0))
        WIN.blit(game_surface, (offset_x, offset_y))
        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())