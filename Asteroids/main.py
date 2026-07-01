import pygame
import asyncio
import random
import math
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
pygame.display.set_caption("Neon Asteroids - Arcade Edition")

# Colors
DARK_BG = (10, 10, 20)
NEON_BLUE = (0, 200, 255)
NEON_GREEN = (0, 255, 100)
NEON_PINK = (255, 0, 150)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 120)

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


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 15
        self.angle = 0
        self.vx = 0
        self.vy = 0
        self.accel = 0.15
        self.friction = 0.985
        self.alive = True

    def rotate(self, direction):
        # direction: -1 (left), 1 (right)
        self.angle += direction * 4.5

    def thrust(self, particles):
        rad = math.radians(self.angle)
        self.vx += math.sin(rad) * self.accel
        self.vy -= math.cos(rad) * self.accel
        
        # Spawn flame trail particles opposite to heading
        rear_x = self.x - math.sin(rad) * self.radius
        rear_y = self.y + math.cos(rad) * self.radius
        for _ in range(2):
            particles.append(Particle(rear_x, rear_y, (255, 120, 0))) # Orange thruster flame

    def update(self):
        self.vx *= self.friction
        self.vy *= self.friction
        self.x += self.vx
        self.y += self.vy

        # Wrap around screen edges
        if self.x < 0: self.x = WIDTH
        elif self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        elif self.y > HEIGHT: self.y = 0

    def draw(self, surface):
        if not self.alive: return
        rad = math.radians(self.angle)
        
        # 3 points of the triangle ship
        nose = (self.x + math.sin(rad) * self.radius * 1.3, self.y - math.cos(rad) * self.radius * 1.3)
        left_rear = (self.x + math.sin(rad + 2.4) * self.radius, self.y - math.cos(rad + 2.4) * self.radius)
        right_rear = (self.x + math.sin(rad - 2.4) * self.radius, self.y - math.cos(rad - 2.4) * self.radius)
        
        pygame.draw.polygon(surface, NEON_BLUE, [nose, left_rear, right_rear], 2)
        # Inner core glow dot
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)


class Laser:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = 3
        self.speed = 10
        rad = math.radians(angle)
        self.vx = math.sin(rad) * self.speed
        self.vy = -math.cos(rad) * self.speed
        self.life = 45 # frames to live

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, NEON_PINK, (int(self.x), int(self.y)), self.radius)
        # Laser core
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 1)


class Asteroid:
    def __init__(self, x, y, size, level=1):
        self.x = x
        self.y = y
        self.size = size # 3 (large), 2 (medium), 1 (small)
        self.radius = size * 20
        self.speed = random.uniform(1.0, 2.5) * (1.0 + (level - 1) * 0.08)
        self.angle = random.uniform(0, 360)
        rad = math.radians(self.angle)
        self.vx = math.sin(rad) * self.speed
        self.vy = -math.cos(rad) * self.speed
        
        # Generate irregular polygon points for neon outline
        self.points_offset = []
        self.num_points = random.randint(8, 12)
        for i in range(self.num_points):
            pt_angle = (i / self.num_points) * 360
            pt_rad = math.radians(pt_angle)
            dist = self.radius * random.uniform(0.75, 1.15)
            self.points_offset.append((math.sin(pt_rad) * dist, -math.cos(pt_rad) * dist))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Wrap screen
        if self.x < -self.radius: self.x = WIDTH + self.radius
        elif self.x > WIDTH + self.radius: self.x = -self.radius
        if self.y < -self.radius: self.y = HEIGHT + self.radius
        elif self.y > HEIGHT + self.radius: self.y = -self.radius

    def draw(self, surface):
        points = []
        for offset in self.points_offset:
            points.append((self.x + offset[0], self.y + offset[1]))
        pygame.draw.polygon(surface, NEON_GREEN, points, 2)


async def main():
    run = True
    clock = pygame.time.Clock()

    ship = Ship()
    lasers = []
    asteroids = []
    particles = []
    
    score = 0
    lives = 3
    level = 1
    game_won = False
    game_over = False
    score_submitted = False
    
    shake_duration = 0
    shake_amount = 0
    
    # Spawn initial large asteroids
    def spawn_initial():
        asteroids.clear()
        num_asteroids = 3 + level
        for _ in range(num_asteroids):
            # Spawn away from center
            while True:
                ax = random.randint(0, WIDTH)
                ay = random.randint(0, HEIGHT)
                if math.hypot(ax - WIDTH//2, ay - HEIGHT//2) > 150:
                    break
            asteroids.append(Asteroid(ax, ay, 3, level))
            
    spawn_initial()

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
                if game_over:
                    if event.key == pygame.K_r:
                        level = 1
                        game_won = False
                        ship = Ship()
                        spawn_initial()
                        score = 0
                        lives = 3
                        game_over = False
                        particles.clear()
                        lasers.clear()
                        score_submitted = False
                else:
                    if event.key == pygame.K_SPACE and ship.alive:
                        # Shoot laser
                        rad = math.radians(ship.angle)
                        # spawn at tip of ship
                        tip_x = ship.x + math.sin(rad) * ship.radius * 1.3
                        tip_y = ship.y - math.cos(rad) * ship.radius * 1.3
                        lasers.append(Laser(tip_x, tip_y, ship.angle))

        if not game_over:
            # Controls Polling
            keys = pygame.key.get_pressed()
            if ship.alive:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    ship.rotate(-1)
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    ship.rotate(1)
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    ship.thrust(particles)

                ship.update()

            # Update Lasers
            for laser in lasers[:]:
                laser.update()
                if laser.life <= 0:
                    lasers.remove(laser)

            # Update Asteroids
            for asteroid in asteroids:
                asteroid.update()

            # Laser - Asteroid Collisions
            for laser in lasers[:]:
                laser_rect = pygame.Rect(laser.x - 2, laser.y - 2, 4, 4)
                hit_asteroid = None
                for asteroid in asteroids:
                    if math.hypot(laser.x - asteroid.x, laser.y - asteroid.y) < asteroid.radius:
                        hit_asteroid = asteroid
                        break
                
                if hit_asteroid:
                    lasers.remove(laser)
                    # Score reward
                    score += (4 - hit_asteroid.size) * 10
                    
                    # Spawn particles
                    for _ in range(15):
                        particles.append(Particle(hit_asteroid.x, hit_asteroid.y, NEON_GREEN))
                        
                    # Trigger shake
                    shake_duration = 10
                    shake_amount = 5
                    
                    # Split asteroid
                    if hit_asteroid.size > 1:
                        for _ in range(2):
                            asteroids.append(Asteroid(hit_asteroid.x, hit_asteroid.y, hit_asteroid.size - 1, level))
                    asteroids.remove(hit_asteroid)

            # Ship - Asteroid Collisions
            if ship.alive:
                for asteroid in asteroids:
                    if math.hypot(ship.x - asteroid.x, ship.y - asteroid.y) < ship.radius + asteroid.radius:
                        # Crash!
                        ship.alive = False
                        lives -= 1
                        shake_duration = 30
                        shake_amount = 12
                        
                        # Massive ship explosion particles
                        for _ in range(30):
                            particles.append(Particle(ship.x, ship.y, NEON_BLUE))
                        for _ in range(15):
                            particles.append(Particle(ship.x, ship.y, WHITE))
                        
                        # Respawn or Game Over
                        if lives > 0:
                            # Schedule a respawn
                            async def respawn():
                                await asyncio.sleep(2)
                                ship.x = WIDTH // 2
                                ship.y = HEIGHT // 2
                                ship.vx = 0
                                ship.vy = 0
                                ship.angle = 0
                                ship.alive = True
                            asyncio.create_task(respawn())
                        else:
                            game_over = True
                        break

            # Check level clear (all asteroids destroyed)
            if not asteroids and not game_over:
                if level >= 20:
                    game_won = True
                    game_over = True
                    if not score_submitted:
                        score_submitted = True
                        if arcade_api:
                            arcade_api.submit_score("Neon Asteroids", score + 3000)
                else:
                    # Level clear transition overlay
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
                    game_surface.fill(DARK_BG)
                    # draw particles
                    for p in particles:
                        p.draw(game_surface)
                    game_surface.blit(overlay, (0, 0))
                    
                    card_rect = pygame.Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3)
                    pygame.draw.rect(game_surface, (15, 15, 30), card_rect, border_radius=15)
                    pygame.draw.rect(game_surface, NEON_GREEN, card_rect, 3, border_radius=15)
                    
                    title = FONT_LARGE.render(f"LEVEL {level} CLEARED", True, NEON_GREEN)
                    sub = FONT_HUD.render("CHARGING WARP DRIVE CORES...", True, WHITE)
                    game_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 + 35))
                    game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 3 + 105))
                    
                    WIN.fill((0, 0, 0))
                    WIN.blit(game_surface, (0, 0))
                    pygame.display.update()
                    
                    await asyncio.sleep(2.0)
                    
                    level += 1
                    spawn_initial()
                    lasers.clear()
                    particles.clear()
                    ship.x = WIDTH // 2
                    ship.y = HEIGHT // 2
                    ship.vx = 0
                    ship.vy = 0
                    ship.angle = 0
                    ship.alive = True
                    continue

        if game_over and not score_submitted:
            score_submitted = True
            if arcade_api:
                arcade_api.submit_score("Neon Asteroids", score)

        # Draw Scene
        game_surface.fill(DARK_BG)

        # Draw particles
        for p in particles:
            p.draw(game_surface)

        # Draw Asteroids
        for asteroid in asteroids:
            asteroid.draw(game_surface)

        # Draw Lasers
        for laser in lasers:
            laser.draw(game_surface)

        # Draw Ship
        ship.draw(game_surface)

        # Draw HUD
        score_txt = FONT_HUD.render(f"SCORE: {score}", 1, NEON_BLUE)
        level_txt = FONT_HUD.render(f"LEVEL: {level}/20", 1, GOLD)
        lives_txt = FONT_HUD.render(f"CORES: {'O ' * lives if lives > 0 else 'CRITICAL'}", 1, NEON_PINK)
        game_surface.blit(score_txt, (20, 20))
        game_surface.blit(level_txt, (WIDTH // 2 - level_txt.get_width() // 2, 20))
        game_surface.blit(lives_txt, (WIDTH - lives_txt.get_width() - 20, 20))

        # Draw Game Over Banner
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            over_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            pygame.draw.rect(game_surface, (15, 15, 30), over_rect, border_radius=15)
            
            if game_won:
                pygame.draw.rect(game_surface, NEON_GREEN, over_rect, 3, border_radius=15)
                over_title = FONT_LARGE.render("SYSTEM RESTORED", True, NEON_GREEN)
                final_lbl = FONT_HUD.render(f"VICTORY SCORE: {score}", True, WHITE)
            else:
                pygame.draw.rect(game_surface, NEON_PINK, over_rect, 3, border_radius=15)
                over_title = FONT_LARGE.render("SYSTEM FAILURE", True, NEON_PINK)
                final_lbl = FONT_HUD.render(f"FINAL SCORE: {score}", True, WHITE)
                
            restart_hint = FONT_HUD.render("PRESS 'R' TO REBOOT CORES", True, NEON_BLUE)

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
    asyncio.run(main())
