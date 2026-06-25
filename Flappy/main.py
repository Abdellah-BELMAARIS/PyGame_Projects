import pygame
import asyncio
import random
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Neon - Arcade Edition")

# Colors
DARK_BG = (10, 10, 18)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRID_COLOR = (18, 18, 30)

# Fonts
try:
    FONT_HUD = pygame.font.SysFont("Outfit", 22, bold=True)
    FONT_LARGE = pygame.font.SysFont("Outfit", 50, bold=True)
except:
    try:
        FONT_HUD = pygame.font.SysFont("Segoe UI", 22, bold=True)
        FONT_LARGE = pygame.font.SysFont("Segoe UI", 50, bold=True)
    except:
        FONT_HUD = pygame.font.Font(None, 22)
        FONT_LARGE = pygame.font.Font(None, 50)

FPS = 60


class BirdParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, -0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.life = random.randint(10, 20)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class ExplosionSpark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = random.randint(15, 28)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 5) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class FlappyBird:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.radius = 16
        self.vel = 0
        self.gravity = 0.5
        self.jump_strength = -8.5
        self.angle = 0
        self.alive = True

    def flap(self):
        if self.alive:
            self.vel = self.jump_strength

    def update(self):
        self.vel += self.gravity
        self.y += self.vel

        # Bound checks
        if self.y < self.radius:
            self.y = self.radius
            self.vel = 0
        
        # Heading angle calculation
        # Tilt up when jumping, tilt down when falling
        self.angle = -self.vel * 3.5
        self.angle = max(-30, min(70, self.angle))

    def draw(self, surface):
        rad_angle = math.radians(self.angle)
        
        # Draw a sleek vector bird shape
        # Head/Beak facing right
        beak = (self.x + math.cos(rad_angle) * (self.radius + 6), self.y - math.sin(rad_angle) * (self.radius + 6))
        wing_top = (self.x - math.cos(rad_angle + 1.2) * self.radius, self.y + math.sin(rad_angle + 1.2) * self.radius)
        wing_bot = (self.x - math.cos(rad_angle - 1.2) * self.radius, self.y + math.sin(rad_angle - 1.2) * self.radius)
        
        # Main body glow outline
        pygame.draw.polygon(surface, NEON_PINK, [beak, wing_top, wing_bot], 2)
        # Inner glow core
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 4)


class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 75
        self.gap = 180
        # Random heights for top and bottom pipes
        self.top_height = random.randint(100, HEIGHT - self.gap - 100)
        self.bottom_y = self.top_height + self.gap
        self.bottom_height = HEIGHT - self.bottom_y
        self.speed = 3.5
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        # Draw top neon pipe
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        pygame.draw.rect(surface, (10, 30, 20), top_rect, border_radius=4)
        pygame.draw.rect(surface, NEON_GREEN, top_rect, 2, border_radius=4)
        # Lip edge of top pipe
        pygame.draw.rect(surface, (12, 45, 25), (self.x - 4, self.top_height - 25, self.width + 8, 25), border_radius=2)
        pygame.draw.rect(surface, NEON_GREEN, (self.x - 4, self.top_height - 25, self.width + 8, 25), 2, border_radius=2)

        # Draw bottom neon pipe
        bot_rect = pygame.Rect(self.x, self.bottom_y, self.width, self.bottom_height)
        pygame.draw.rect(surface, (10, 30, 20), bot_rect, border_radius=4)
        pygame.draw.rect(surface, NEON_GREEN, bot_rect, 2, border_radius=4)
        # Lip edge of bottom pipe
        pygame.draw.rect(surface, (12, 45, 25), (self.x - 4, self.bottom_y, self.width + 8, 25), border_radius=2)
        pygame.draw.rect(surface, NEON_GREEN, (self.x - 4, self.bottom_y, self.width + 8, 25), 2, border_radius=2)


async def main():
    run = True
    clock = pygame.time.Clock()

    bird = FlappyBird()
    pipes = [Pipe(WIDTH + 100), Pipe(WIDTH + 450)]
    particles = []
    
    score = 0
    high_score = 0
    game_over = False
    
    shake_duration = 0
    shake_amount = 0

    # Load high score
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                high_score = int(f.read().strip())
        except:
            pass

    game_surface = pygame.Surface((WIDTH, HEIGHT))

    while run:
        clock.tick(FPS)

        # Update trail particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        bird = FlappyBird()
                        pipes = [Pipe(WIDTH + 100), Pipe(WIDTH + 450)]
                        score = 0
                        game_over = False
                        particles.clear()
                else:
                    if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                        bird.flap()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over:
                    bird.flap()

        if not game_over:
            # Emit trail particles
            if bird.alive and random.random() < 0.6:
                particles.append(BirdParticle(bird.x - bird.radius, bird.y, NEON_PINK))

            # Update bird
            bird.update()

            # Update Pipes
            for pipe in pipes[:]:
                pipe.update()
                
                # Check score pass
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    if score > high_score:
                        high_score = score
                        try:
                            with open("highscore.txt", "w") as f:
                                f.write(str(high_score))
                        except:
                            pass
                    # Soft score chime particles
                    for _ in range(5):
                        particles.append(BirdParticle(bird.x, bird.y, GOLD))

                # Remove offscreen pipes and spawn new ones
                if pipe.x < -pipe.width:
                    pipes.remove(pipe)
                    # Find furthest pipe x to spawn 350px after it
                    furthest_x = max(p.x for p in pipes) if pipes else WIDTH
                    pipes.append(Pipe(furthest_x + 350))

            # Check floor crash
            if bird.y + bird.radius >= HEIGHT:
                bird.alive = False
                game_over = True
                shake_duration = 30
                shake_amount = 12
                # Huge splash
                for _ in range(25):
                    particles.append(ExplosionSpark(bird.x, bird.y, NEON_PINK))
                for _ in range(15):
                    particles.append(ExplosionSpark(bird.x, bird.y, GOLD))

            # Pipe Collisions
            if bird.alive:
                bird_rect = pygame.Rect(bird.x - bird.radius + 2, bird.y - bird.radius + 2, bird.radius*2 - 4, bird.radius*2 - 4)
                for pipe in pipes:
                    top_rect = pygame.Rect(pipe.x, 0, pipe.width, pipe.top_height)
                    bot_rect = pygame.Rect(pipe.x, pipe.bottom_y, pipe.width, pipe.bottom_height)
                    
                    if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect):
                        bird.alive = False
                        game_over = True
                        shake_duration = 30
                        shake_amount = 12
                        # Explosion sparks
                        for _ in range(25):
                            particles.append(ExplosionSpark(bird.x, bird.y, NEON_PINK))
                        for _ in range(15):
                            particles.append(ExplosionSpark(bird.x, bird.y, GOLD))
                        break

        # Draw
        game_surface.fill(DARK_BG)
        
        # Draw ambient grid lines
        for x in range(0, WIDTH, 60):
            pygame.draw.line(game_surface, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(game_surface, GRID_COLOR, (0, y), (WIDTH, y))

        # Draw Pipes
        for pipe in pipes:
            pipe.draw(game_surface)

        # Draw particles
        for p in particles:
            p.draw(game_surface)

        # Draw Bird
        bird.draw(game_surface)

        # Draw HUD
        score_txt = FONT_HUD.render(f"SCORE: {score}", 1, NEON_BLUE)
        best_txt = FONT_HUD.render(f"BEST: {high_score}", 1, GOLD)
        game_surface.blit(score_txt, (25, 25))
        game_surface.blit(best_txt, (WIDTH - best_txt.get_width() - 25, 25))

        # Draw Game Over Banner
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            pygame.draw.rect(game_surface, NEON_PINK, over_rect, 3, border_radius=15)

            over_title = FONT_LARGE.render("WING DAMAGE", True, NEON_PINK)
            final_lbl = FONT_HUD.render(f"FINAL SCORE: {score}", True, WHITE)
            restart_hint = FONT_HUD.render("PRESS 'R' TO RESTORE CORES", True, NEON_BLUE)

            game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 35))
            game_surface.blit(final_lbl, (WIDTH // 2 - final_lbl.get_width() // 2, HEIGHT // 3 + 105))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 150))

        # Handle screen shake
        if shake_duration > 0:
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
            shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        WIN.fill((0, 0, 0))
        WIN.blit(game_surface, (offset_x, offset_y))
        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    import os
    asyncio.run(main())
