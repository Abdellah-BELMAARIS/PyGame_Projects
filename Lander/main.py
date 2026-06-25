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
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Lander - Arcade Edition")

# Colors
DARK_BG = (8, 8, 16)
NEON_BLUE = (0, 200, 255)
NEON_GREEN = (0, 255, 100)
NEON_PINK = (255, 0, 150)
NEON_CYAN = (0, 255, 240)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 100)

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

# Procedural terrain vertices: list of (x, y)
# Index 3 (250 to 350) and Index 7 (550 to 650) are flat landing pads!
TERRAIN_POINTS = [
    (0, 560), (100, 520), (200, 540), 
    (240, 490), (340, 490), # PAD 1 (Flat, y = 490)
    (400, 530), (490, 550), 
    (540, 460), (640, 460), # PAD 2 (Flat, y = 460)
    (700, 510), (800, 560)
]


class ExhaustParticle:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx + random.uniform(-0.5, 0.5)
        self.vy = vy + random.uniform(-0.5, 0.5)
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


class LandingSparkle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, -1)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 3) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class LunarLander:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.vx = 1.8
        self.vy = 0.0
        self.angle = 0.0 # Degrees
        self.fuel = 1000
        self.gravity = 0.04
        self.thrust_accel = 0.11
        self.width = 30
        self.height = 30
        self.alive = True
        self.landed = False

    def rotate(self, dir_factor):
        if self.alive and not self.landed:
            self.angle += dir_factor * 2.5
            self.angle = max(-90, min(90, self.angle))

    def fire_thruster(self, particles):
        if not self.alive or self.landed or self.fuel <= 0:
            return
        
        self.fuel -= 3
        rad = math.radians(self.angle)
        
        # Accelerate lander
        self.vx += math.sin(rad) * self.thrust_accel
        self.y_accel = -math.cos(rad) * self.thrust_accel
        self.vy += self.y_accel
        
        # Spawn exhaust particles opposite to heading
        # Tip of exhaust is at bottom center of lander
        offset_x = -math.sin(rad) * 15
        offset_y = math.cos(rad) * 15
        
        particle_vx = -math.sin(rad) * 4
        particle_vy = math.cos(rad) * 4
        
        for _ in range(3):
            particles.append(ExhaustParticle(self.x + offset_x, self.y + offset_y, particle_vx, particle_vy, (255, 140, 0)))

    def update(self):
        if not self.landed:
            self.vy += self.gravity
            self.x += self.vx
            self.y += self.vy

            # Warp boundaries
            if self.x < 0: self.x = WIDTH
            elif self.x > WIDTH: self.x = 0

    def draw(self, surface):
        rad = math.radians(self.angle)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        # 1. Draw landing legs (vector lines)
        leg_l_start = (self.x - 10 * cos_r, self.y + 5 * sin_r)
        leg_l_end = (self.x - 18 * cos_r + 8 * sin_r, self.y + 16 * cos_r + 5 * sin_r)
        leg_r_start = (self.x + 10 * cos_r, self.y - 5 * sin_r)
        leg_r_end = (self.x + 18 * cos_r + 8 * sin_r, self.y + 16 * cos_r - 5 * sin_r)
        
        pygame.draw.line(surface, NEON_BLUE, leg_l_start, leg_l_end, 2)
        pygame.draw.line(surface, NEON_BLUE, leg_r_start, leg_r_end, 2)
        
        # Landing pads feet
        pygame.draw.line(surface, NEON_CYAN, (leg_l_end[0] - 6, leg_l_end[1]), (leg_l_end[0] + 6, leg_l_end[1]), 2)
        pygame.draw.line(surface, NEON_CYAN, (leg_r_end[0] - 6, leg_r_end[1]), (leg_r_end[0] + 6, leg_r_end[1]), 2)

        # 2. Draw module body (vector rectangle / octagon)
        pts = [
            (self.x - 12 * cos_r - 8 * sin_r, self.y + 8 * cos_r - 12 * sin_r),
            (self.x + 12 * cos_r - 8 * sin_r, self.y + 8 * cos_r + 12 * sin_r),
            (self.x + 12 * cos_r + 8 * sin_r, self.y - 8 * cos_r + 12 * sin_r),
            (self.x - 12 * cos_r + 8 * sin_r, self.y - 8 * cos_r - 12 * sin_r)
        ]
        pygame.draw.polygon(surface, NEON_BLUE, pts, 2)
        
        # 3. Inner cabin core dot
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 4)


def get_terrain_height(x):
    # Interpolate height at x
    for i in range(len(TERRAIN_POINTS) - 1):
        x1, y1 = TERRAIN_POINTS[i]
        x2, y2 = TERRAIN_POINTS[i+1]
        if x1 <= x <= x2:
            t = (x - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)
    return HEIGHT


def check_on_pad(x):
    # Returns True if x is inside Pad 1 (240 to 340) or Pad 2 (540 to 640)
    if 240 <= x <= 340:
        return True
    if 540 <= x <= 640:
        return True
    return False


async def main():
    run = True
    clock = pygame.time.Clock()

    lander = LunarLander()
    particles = []
    
    status_message = "PILOT THE LANDER TO A CYAN PAD"
    status_color = NEON_BLUE
    game_over = False
    score_submitted = False
    
    shake_duration = 0
    shake_amount = 0

    game_surface = pygame.Surface((WIDTH, HEIGHT))

    while run:
        clock.tick(FPS)

        # Update particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if game_over or lander.landed:
                    if event.key == pygame.K_r:
                        # Reset game
                        lander = LunarLander()
                        status_message = "PILOT THE LANDER TO A CYAN PAD"
                        status_color = NEON_BLUE
                        game_over = False
                        particles.clear()
                        score_submitted = False

        # Keyboard polling
        keys = pygame.key.get_pressed()
        if lander.alive and not lander.landed:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                lander.rotate(-1)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                lander.rotate(1)
            
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                lander.fire_thruster(particles)
                # Small engine shake vibration
                if random.random() < 0.3:
                    shake_duration = 2
                    shake_amount = 2

        # Physics update
        lander.update()

        # Collision Check against Terrain Height
        terrain_y = get_terrain_height(lander.x)
        lander_bottom_y = lander.y + 16  # approximate feet position
        
        if lander.alive and not lander.landed and lander_bottom_y >= terrain_y:
            # Impact!
            on_pad = check_on_pad(lander.x)
            safe_speed = lander.vy < 1.8 and abs(lander.vx) < 1.0
            safe_angle = abs(lander.angle) < 12.0
            
            # Snap lander to terrain surface
            lander.y = terrain_y - 16
            
            if on_pad and safe_speed and safe_angle:
                # Successful landing!
                lander.landed = True
                lander.vx = 0
                lander.vy = 0
                lander.angle = 0
                status_message = "TOUCHDOWN SUCCESSFUL! CORES ALIGNED"
                status_color = NEON_GREEN
                # Spawn celebratory gold sparkle fountains!
                for _ in range(35):
                    particles.append(LandingSparkle(lander.x, lander.y + 15, GOLD))
                    particles.append(LandingSparkle(lander.x, lander.y + 15, NEON_CYAN))
                shake_duration = 15
                shake_amount = 5
            else:
                # Hull breach crash!
                lander.alive = False
                game_over = True
                
                # Setup failure feedback message
                if not on_pad:
                    status_message = "CRITICAL: MISSED LANDING ZONE"
                elif not safe_speed:
                    status_message = "CRITICAL: IMPACT VELOCITY TOO HIGH"
                else:
                    status_message = "CRITICAL: TILT ANGLE FAILURE"
                status_color = NEON_PINK
                
                # Spawn massive explosion sparks!
                for _ in range(35):
                    particles.append(LandingSparkle(lander.x, lander.y, NEON_PINK))
                    particles.append(LandingSparkle(lander.x, lander.y, GOLD))
                shake_duration = 35
                shake_amount = 14

        # Draw
        game_surface.fill(DARK_BG)

        # Draw stars
        random.seed(33)
        for _ in range(25):
            sx = random.randint(0, WIDTH)
            sy = random.randint(0, HEIGHT - 200)
            pygame.draw.circle(game_surface, (70, 70, 90), (sx, sy), 1)

        # Draw Terrain
        for i in range(len(TERRAIN_POINTS) - 1):
            p1 = TERRAIN_POINTS[i]
            p2 = TERRAIN_POINTS[i+1]
            
            # Draw segment
            # If segment is flat and matches a pad, draw in glowing cyan, else green
            is_pad = p1[1] == p2[1] and (p1[0] == 240 or p1[0] == 540)
            color = NEON_CYAN if is_pad else NEON_GREEN
            pygame.draw.line(game_surface, color, p1, p2, 3)
            
            # Draw underfill glow
            if is_pad:
                glow_poly = [(p1[0], p1[1]), (p2[0], p2[1]), (p2[0], HEIGHT), (p1[0], HEIGHT)]
                faint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(faint, (*NEON_CYAN, 20), glow_poly)
                game_surface.blit(faint, (0,0))

        # Draw particles
        for p in particles:
            p.draw(game_surface)

        # Draw Lander
        if lander.alive:
            lander.draw(game_surface)

        # Draw HUD
        # Fuel Bar
        fuel_lbl = FONT_HUD.render("FUEL MATRIX", True, NEON_BLUE)
        game_surface.blit(fuel_lbl, (25, 25))
        
        fuel_w = int(180 * (max(0, lander.fuel) / 1000.0))
        pygame.draw.rect(game_surface, (25, 25, 45), (25, 50, 180, 10), border_radius=3)
        if fuel_w > 0:
            fuel_color = NEON_BLUE if lander.fuel > 300 else NEON_PINK
            pygame.draw.rect(game_surface, fuel_color, (25, 50, fuel_w, 10), border_radius=3)

        # Status Message
        status_txt = FONT_HUD.render(status_message, True, status_color)
        game_surface.blit(status_txt, (WIDTH // 2 - status_txt.get_width() // 2, 25))

        # Velocity readouts
        vx_txt = FONT_HUD.render(f"H-SPEED: {abs(lander.vx):.1f} M/S", True, WHITE if abs(lander.vx) < 1.0 else NEON_PINK)
        vy_txt = FONT_HUD.render(f"V-SPEED: {lander.vy:.1f} M/S", True, WHITE if lander.vy < 1.8 else NEON_PINK)
        angle_txt = FONT_HUD.render(f"TILT: {int(lander.angle)}°", True, WHITE if abs(lander.angle) < 12 else NEON_PINK)
        
        game_surface.blit(vx_txt, (WIDTH - 180, 25))
        game_surface.blit(vy_txt, (WIDTH - 180, 50))
        game_surface.blit(angle_txt, (WIDTH - 180, 75))

        if (game_over or lander.landed) and not score_submitted:
            score_submitted = True
            if arcade_api:
                # 500 bonus points for landing successfully + remaining fuel
                final_score = (500 + int(lander.fuel)) if lander.landed else 0
                arcade_api.submit_score("Neon Lander", final_score)

        # Game Over Banner
        if game_over or lander.landed:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            pygame.draw.rect(game_surface, status_color, over_rect, 3, border_radius=15)

            title_str = "HULL BREACHED" if game_over else "TOUCHDOWN!"
            over_title = FONT_LARGE.render(title_str, True, status_color)
            restart_hint = FONT_HUD.render("PRESS 'R' TO RESTART CORE", True, NEON_BLUE)

            game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 45))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 125))

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
    asyncio.run(main())
