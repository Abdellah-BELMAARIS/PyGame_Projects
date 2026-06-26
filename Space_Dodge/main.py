import pygame
import time
import random
import asyncio
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

pygame.font.init()

# Constants
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge - Hyper Neon Edition")

# Try to load background, fallback to dark blue gradient if missing
try:
    BG = pygame.transform.scale(pygame.image.load("bg.jpg"), (WIDTH, HEIGHT))
    HAS_BG = True
except Exception as e:
    print(f"Could not load background image: {e}. Using procedural background.")
    HAS_BG = False

PLAYER_WIDTH = 45
PLAYER_HEIGHT = 55
PLAYER_VEL = 7

STAR_WIDTH = 15
STAR_HEIGHT = 15
STAR_VEL = 4

# Colors
CYAN = (0, 240, 255)
DEEP_BLUE = (0, 80, 180)
ORANGE = (255, 100, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
DARK_BG = (10, 10, 22)

# Try to load a premium font
try:
    FONT = pygame.font.SysFont("Outfit", 30, bold=True)
    FONT_LARGE = pygame.font.SysFont("Outfit", 60, bold=True)
except:
    try:
        FONT = pygame.font.SysFont("Segoe UI", 30, bold=True)
        FONT_LARGE = pygame.font.SysFont("Segoe UI", 60, bold=True)
    except:
        FONT = pygame.font.SysFont("sans-serif", 30, bold=True)
        FONT_LARGE = pygame.font.SysFont("sans-serif", 60, bold=True)

# Particle Systems
class ThrusterParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(3.0, 6.0)
        self.life = random.randint(15, 25)
        self.max_life = self.life
        self.color = random.choice([CYAN, (0, 150, 255), (150, 240, 255)])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 5) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

class DebrisParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6.0, 6.0)
        self.vy = random.uniform(-6.0, 6.0)
        self.life = random.randint(25, 45)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity-like pull downwards
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 6) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

class Meteor:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.vel = random.uniform(STAR_VEL - 0.5, STAR_VEL + 2.5)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2.5, 2.5)
        self.color = random.choice([ORANGE, (255, 60, 60), GOLD])
        self.trail = []

    def update(self):
        self.y += self.vel
        self.angle += self.rot_speed
        
        # Track trail
        self.trail.append((self.x + self.size // 2, self.y + self.size // 2))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, surface):
        # Draw fading fire trail
        for i, pos in enumerate(self.trail):
            factor = (i + 1) / len(self.trail)
            radius = int((self.size // 2) * factor * 0.8) + 1
            alpha_color = (
                int(self.color[0] * factor),
                int(self.color[1] * factor),
                int(self.color[2] * factor)
            )
            pygame.draw.circle(surface, alpha_color, (int(pos[0]), int(pos[1])), radius)

        # Draw rotated square/diamond shape for meteor body
        cx = int(self.x + self.size // 2)
        cy = int(self.y + self.size // 2)
        r = self.size // 2
        
        points = []
        for a in [0, 90, 180, 270]:
            rad = math.radians(a + self.angle)
            points.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
            
        pygame.draw.polygon(surface, self.color, points)
        # Inner highlights
        pygame.draw.polygon(surface, WHITE, points, 1)

def draw_player_ship(surface, rect):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    # Outer engine glow layers
    for offset in range(3, 0, -1):
        points = [
            (x + w // 2, y - offset),
            (x + w + offset, y + h + offset),
            (x + w // 2, y + h - 5 + offset),
            (x - offset, y + h + offset)
        ]
        pygame.draw.polygon(surface, (0, 120 // offset, 255 // offset), points, 1)
        
    # Main Spaceship Body (Cyan Cyberpunk Triangle)
    body_points = [
        (x + w // 2, y),
        (x + w, y + h),
        (x + w // 2, y + h - 6),
        (x, y + h)
    ]
    pygame.draw.polygon(surface, CYAN, body_points)
    
    # Center stripe
    stripe_points = [
        (x + w // 2, y + 8),
        (x + w // 2 + 3, y + h - 10),
        (x + w // 2 - 3, y + h - 10)
    ]
    pygame.draw.polygon(surface, WHITE, stripe_points)

def load_high_score():
    try:
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def save_high_score(score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except:
        pass

async def main():
    run = True
    clock = pygame.time.Clock()
    
    player = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 20,
                         PLAYER_WIDTH, PLAYER_HEIGHT)
    
    start_time = time.time()
    elapsed_time = 0
    
    star_add_increment = 2000
    star_count = 0
    
    meteors = []
    thruster_particles = []
    debris_particles = []
    
    hit = False
    score = 0
    score_submitted = False
    high_score = load_high_score()
    
    # Screen shake variables
    shake_amount = 0
    shake_duration = 0
    
    # Procedural background stars (in case bg.jpg is missing)
    bg_stars = []
    for _ in range(50):
        bg_stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 2.0)])

    # Setup game surface for rendering offscreen (enables easy screen-shake)
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time
        
        # Spawn new meteors
        if star_count > star_add_increment:
            for _ in range(random.randint(2, 4)):
                star_x = random.randint(20, WIDTH - 40)
                size = random.randint(15, 30)
                meteor = Meteor(star_x, -size, size)
                meteors.append(meteor)
                
            # Slowly speed up spawning as time goes on
            star_add_increment = max(300, star_add_increment - 40)
            star_count = 0
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # Ship Movement Controls
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        # Spawn engine thruster particles at bottom center of the player ship
        if not hit:
            thruster_particles.append(ThrusterParticle(player.x + PLAYER_WIDTH // 2, player.y + PLAYER_HEIGHT - 5))

        # Update thruster particles
        for tp in thruster_particles[:]:
            tp.update()
            if tp.life <= 0:
                thruster_particles.remove(tp)

        # Update debris particles
        for dp in debris_particles[:]:
            dp.update()
            if dp.life <= 0:
                debris_particles.remove(dp)

        # Update background stars
        for bs in bg_stars:
            bs[1] += bs[2]
            if bs[1] > HEIGHT:
                bs[1] = 0
                bs[0] = random.randint(0, WIDTH)

        # Update and Collide Meteors
        for meteor in meteors[:]:
            meteor.update()
            if meteor.y > HEIGHT:
                meteors.remove(meteor)
            elif not hit:
                # Check collision using Pygame rect collision (with slight inset padding for better gameplay feel)
                meteor_rect = pygame.Rect(meteor.x + 2, meteor.y + 2, meteor.size - 4, meteor.size - 4)
                if meteor_rect.colliderect(player):
                    hit = True
                    shake_duration = 30
                    shake_amount = 12
                    
                    # Spawn massive explosion debris!
                    # Orange/Yellow debris for meteor
                    for _ in range(30):
                        debris_particles.append(DebrisParticle(meteor.x + meteor.size//2, meteor.y + meteor.size//2, meteor.color))
                    # Cyan/White debris for ship
                    for _ in range(45):
                        debris_particles.append(DebrisParticle(player.x + PLAYER_WIDTH//2, player.y + PLAYER_HEIGHT//2, CYAN))
                        debris_particles.append(DebrisParticle(player.x + PLAYER_WIDTH//2, player.y + PLAYER_HEIGHT//2, WHITE))
                    break

        # Render Game Elements to Game Surface
        game_surface.fill(DARK_BG)
        
        # 1. Draw Background
        if HAS_BG:
            game_surface.blit(BG, (0, 0))
        else:
            # Draw scrolling procedural stars
            for bs in bg_stars:
                r = int(bs[2]) + 1
                pygame.draw.circle(game_surface, (150, 180, 220), (int(bs[0]), int(bs[1])), r)
                
        # 2. Draw Particles
        for tp in thruster_particles:
            tp.draw(game_surface)
        for dp in debris_particles:
            dp.draw(game_surface)

        # 3. Draw Meteors
        for meteor in meteors:
            meteor.draw(game_surface)

        # 4. Draw Player Ship (if alive)
        if not hit:
            draw_player_ship(game_surface, player)

        # 5. Draw Sleek Cyberpunk HUD
        # Semi-transparent top bar
        hud_bar = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        pygame.draw.rect(hud_bar, (10, 12, 30, 200), (0, 0, WIDTH, 50))
        game_surface.blit(hud_bar, (0, 0))
        pygame.draw.line(game_surface, CYAN, (0, 50), (WIDTH, 50), 2)

        # Draw elapsed time as score
        if not hit:
            score = int(elapsed_time * 10)
            if score > high_score:
                high_score = score
                save_high_score(high_score)
        else:
            if not score_submitted:
                score_submitted = True
                if arcade_api:
                    arcade_api.submit_score("Space Dodge", score)

        score_text = FONT.render(f"SCORE: {score}", 1, CYAN)
        high_score_text = FONT.render(f"HIGH SCORE: {high_score}", 1, GOLD)
        
        game_surface.blit(score_text, (20, 10))
        game_surface.blit(high_score_text, (WIDTH - high_score_text.get_width() - 20, 10))

        # 6. Handle Game Over Screen
        if hit and len(debris_particles) == 0:
            # Draw glowing Game Over Banner
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 15, 200), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            pygame.draw.rect(game_surface, ORANGE, over_rect, 3, border_radius=15)

            lost_title = FONT_LARGE.render("SYSTEM FAILURE", 1, ORANGE)
            final_score_text = FONT.render(f"FINAL SCORE: {score}", 1, WHITE)
            restart_text = FONT.render("PRESS R TO RESTART", 1, CYAN)

            game_surface.blit(lost_title, (WIDTH // 2 - lost_title.get_width() // 2, HEIGHT // 3 + 30))
            game_surface.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 3 + 100))
            game_surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 3 + 150))

            # Replay input check
            if keys[pygame.K_r]:
                hit = False
                player.x = WIDTH // 2 - PLAYER_WIDTH // 2
                meteors.clear()
                thruster_particles.clear()
                debris_particles.clear()
                start_time = time.time()
                star_add_increment = 2000
                star_count = 0
                score_submitted = False

        # Handle Screen Shake Offset
        if shake_duration > 0:
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
            shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        # Blit game surface to the main window with screen shake offset
        WIN.fill((0, 0, 0))
        WIN.blit(game_surface, (offset_x, offset_y))
        pygame.display.update()
        
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())