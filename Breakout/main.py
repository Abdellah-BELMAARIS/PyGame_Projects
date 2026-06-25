import pygame
import asyncio
import random
import math
import os
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()
if not pygame.mixer.get_init():
    try:
        pygame.mixer.init(22050, -16, 1, 512)
    except:
        pass

# Constants
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Breakout - Arcade Edition")

# Colors
DARK_BG = (8, 8, 16)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
NEON_PURPLE = (180, 0, 255)
NEON_ORANGE = (255, 120, 0)
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

# Try to import arcade_api for high score submission
try:
    import arcade_api
except ImportError:
    # Fallback if run standalone or in subfolder without copy
    sys.path.append("..")
    try:
        import arcade_api
    except:
        arcade_api = None

# Procedural Sound Synthesizer
def synth_sfx(freq, duration, type="square", volume=0.08):
    if not pygame.mixer or not pygame.mixer.get_init():
        return None
    try:
        import array
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buffer = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            if type == "square":
                val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif type == "sine":
                val = math.sin(2 * math.pi * freq * t)
            elif type == "triangle":
                val = (abs((i % (sample_rate / freq)) / (sample_rate / freq) - 0.5) - 0.25) * 4
            elif type == "noise":
                val = random.uniform(-1.0, 1.0)
            else:
                val = 0.0
            
            # Linear decay envelope
            decay = 1.0 - (i / num_samples)
            sample = int(val * 32767 * volume * decay)
            buffer[i] = max(-32768, min(32767, sample))
        return pygame.mixer.Sound(buffer)
    except Exception as e:
        print("Synth error:", e)
        return None

# Pre-synthesize Sounds
SOUNDS = {
    "paddle": synth_sfx(440, 0.08, "triangle"),
    "brick_standard": synth_sfx(660, 0.06, "square"),
    "brick_armored": synth_sfx(330, 0.1, "square"),
    "brick_explosive": synth_sfx(120, 0.3, "noise", volume=0.15),
    "powerup": synth_sfx(587, 0.15, "sine"),
    "laser": synth_sfx(880, 0.08, "sine"),
    "gameover": synth_sfx(220, 0.5, "sawtooth" if "sawtooth" else "square"),
    "victory": synth_sfx(880, 0.4, "sine")
}

def play_sfx(name):
    sound = SOUNDS.get(name)
    if sound:
        sound.play()

# Entity Classes
class Particle:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx + random.uniform(-1, 1)
        self.vy = vy + random.uniform(-1, 1)
        self.color = color
        self.life = random.randint(15, 30)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity drift
        self.life -= 1

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        radius = int((self.life / self.max_life) * 4) + 1
        # Create a tiny surface to support alpha
        p_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (self.color[0], self.color[1], self.color[2], alpha), (radius, radius), radius)
        surface.blit(p_surf, (int(self.x - radius), int(self.y - radius)))

class LaserBolt:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 4
        self.h = 15
        self.speed = 8
        self.rect = pygame.Rect(self.x - self.w//2, self.y, self.w, self.h)

    def update(self):
        self.y -= self.speed
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, NEON_PINK, self.rect, border_radius=2)
        # Inner glow
        pygame.draw.rect(surface, WHITE, (self.rect.x + 1, self.rect.y + 2, self.w - 2, self.h - 4), border_radius=1)

class PowerUpPod:
    # Types: 'MULTIBALL', 'LASER', 'SHIELD'
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.w = 22
        self.h = 22
        self.speed = 3
        self.rect = pygame.Rect(self.x - self.w//2, self.y, self.w, self.h)
        self.color = NEON_BLUE if type == 'MULTIBALL' else (NEON_PINK if type == 'LASER' else NEON_GREEN)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=6)
        # Core icon drawing
        if self.type == 'MULTIBALL':
            pygame.draw.circle(surface, WHITE, (self.rect.centerx, self.rect.centery), 4)
        elif self.type == 'LASER':
            pygame.draw.line(surface, WHITE, (self.rect.centerx, self.rect.y + 4), (self.rect.centerx, self.rect.y + 18), 3)
        elif self.type == 'SHIELD':
            pygame.draw.line(surface, WHITE, (self.rect.x + 4, self.rect.centery + 3), (self.rect.x + 18, self.rect.centery + 3), 3)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 6
        angle = random.uniform(-math.pi/4, -3*math.pi/4)
        self.vx = self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        self.trail = []

    def update(self):
        # Save trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        # Draw fading light trail
        for idx, pos in enumerate(self.trail):
            alpha = int((idx / len(self.trail)) * 100)
            tr = int((idx / len(self.trail)) * self.radius) + 1
            t_surf = pygame.Surface((tr*2, tr*2), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (0, 200, 255, alpha), (tr, tr), tr)
            surface.blit(t_surf, (int(pos[0] - tr), int(pos[1] - tr)))

        # Core Ball
        pygame.draw.circle(surface, NEON_BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 3)

class Paddle:
    def __init__(self):
        self.w = 120
        self.h = 16
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 50
        self.vx = 0
        self.speed = 8
        self.friction = 0.85
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.laser_timer = 0
        self.laser_active = False

    def move(self, dx):
        self.vx += dx * 1.5
        # Clamp velocity
        self.vx = max(-self.speed * 1.3, min(self.speed * 1.3, self.vx))

    def update(self):
        self.x += self.vx
        self.vx *= self.friction
        
        # Keep paddle inside boundaries
        if self.x < 15:
            self.x = 15
            self.vx = 0
        elif self.x + self.w > WIDTH - 15:
            self.x = WIDTH - 15 - self.w
            self.vx = 0

        self.rect.x = int(self.x)
        self.rect.width = self.w

        if self.laser_active and self.laser_timer > 0:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_active = False

    def draw(self, surface):
        p_color = NEON_PINK if self.laser_active else NEON_BLUE
        # Draw neon glowing capsule paddle
        pygame.draw.rect(surface, p_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 3, self.rect.y + 3, self.rect.width - 6, self.rect.height - 6), border_radius=6)
        
        # Draw side indicators
        if self.laser_active:
            # Laser gun nozzles on left and right
            pygame.draw.rect(surface, NEON_PINK, (self.rect.x - 4, self.rect.y - 6, 6, 8), border_radius=2)
            pygame.draw.rect(surface, NEON_PINK, (self.rect.right - 2, self.rect.y - 6, 6, 8), border_radius=2)

class Brick:
    # Categories: 'STANDARD', 'ARMORED', 'EXPLOSIVE'
    def __init__(self, x, y, w, h, category, score_val=100):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.category = category
        self.score_val = score_val
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        if category == 'STANDARD':
            self.hits_left = 1
            self.color = random.choice([NEON_BLUE, NEON_PURPLE, NEON_GREEN])
        elif category == 'ARMORED':
            self.hits_left = 2
            self.color = GRAY
        elif category == 'EXPLOSIVE':
            self.hits_left = 1
            self.color = NEON_ORANGE
            self.pulse_time = random.uniform(0, 2*math.pi)

    def hit(self):
        self.hits_left -= 1
        if self.category == 'ARMORED' and self.hits_left == 1:
            self.color = (130, 100, 100) # cracked look color
        return self.hits_left <= 0

    def update(self):
        if self.category == 'EXPLOSIVE':
            self.pulse_time += 0.1
            pulse = (math.sin(self.pulse_time) + 1) / 2
            # Flashes brighter orange to red
            self.color = (255, int(100 + pulse * 70), int(pulse * 30))

    def draw(self, surface):
        if self.category == 'ARMORED':
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
            pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=4)
            if self.hits_left == 2:
                # Armored plates markings
                pygame.draw.line(surface, WHITE, (self.x + 8, self.y + 4), (self.x + 8, self.y + self.h - 4), 1)
                pygame.draw.line(surface, WHITE, (self.x + self.w - 8, self.y + 4), (self.x + self.w - 8, self.y + self.h - 4), 1)
        elif self.category == 'EXPLOSIVE':
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
            pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=4)
            # Hazardous warning stripes in core
            pygame.draw.line(surface, WHITE, (self.x + 10, self.y + self.h - 4), (self.x + self.w - 10, self.y + 4), 2)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
            pygame.draw.rect(surface, WHITE, (self.rect.x + 2, self.rect.y + 2, self.w - 4, self.h - 4), 1, border_radius=3)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.05, 0.4)
        self.size = random.uniform(0.5, 1.8)
        self.color = random.choice([(0, 100, 255), (255, 0, 100), (100, 100, 150)])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


async def main():
    run = True
    clock = pygame.time.Clock()

    # Game state variables
    score = 0
    lives = 3
    game_over = False
    victory = False
    shake_duration = 0
    shake_amount = 0
    
    # Bottom safety shield barrier
    shield_active = False
    shield_y = HEIGHT - 20
    
    # Initialize Lists
    stars = [Star() for _ in range(50)]
    paddle = Paddle()
    balls = [Ball(WIDTH // 2, HEIGHT - 100)]
    bricks = []
    particles = []
    lasers = []
    powerups = []

    active_powerup_banner = ""
    banner_timer = 0

    # Game layout surface
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    # Helper: trigger screen shake
    def trigger_shake(duration, amount):
        nonlocal shake_duration, shake_amount
        shake_duration = duration
        shake_amount = amount

    # Helper: Spawn brick grid
    def build_brick_matrix():
        bricks.clear()
        cols = 10
        rows = 6
        brick_w = 70
        brick_h = 24
        x_start = (WIDTH - (cols * (brick_w + 6))) // 2
        y_start = 80
        
        for r in range(rows):
            for c in range(cols):
                bx = x_start + c * (brick_w + 6)
                by = y_start + r * (brick_h + 6)
                
                # Determine brick type procedurally
                rand_val = random.random()
                if rand_val < 0.12:
                    cat = 'EXPLOSIVE'
                    score_val = 150
                elif rand_val < 0.28:
                    cat = 'ARMORED'
                    score_val = 200
                else:
                    cat = 'STANDARD'
                    score_val = 100
                    
                bricks.append(Brick(bx, by, brick_w, brick_h, cat, score_val))

    build_brick_matrix()

    # Helper: Spawn particles on brick hit
    def spawn_brick_particles(brick):
        for _ in range(15):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-4, 1)
            particles.append(Particle(brick.rect.centerx, brick.rect.centery, vx, vy, brick.color))

    # Helper: Explosive detonate chain reaction
    def detonate_brick(expl_brick):
        play_sfx("brick_explosive")
        trigger_shake(15, 8)
        
        # Spawn cloud of glowing particles
        for _ in range(30):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)
            particles.append(Particle(expl_brick.rect.centerx, expl_brick.rect.centery, vx, vy, expl_brick.color))
            
        # Range check for adjacent bricks
        detonation_radius = 90
        adjacent_to_destroy = []
        
        for b in bricks:
            if b == expl_brick:
                continue
            dist = math.hypot(b.rect.centerx - expl_brick.rect.centerx, b.rect.centery - expl_brick.rect.centery)
            if dist <= detonation_radius:
                adjacent_to_destroy.append(b)
                
        for ab in adjacent_to_destroy:
            if ab in bricks:
                # Add score
                nonlocal score
                score += ab.score_val
                spawn_brick_particles(ab)
                bricks.remove(ab)
                # If nested explosive, detonate as well!
                if ab.category == 'EXPLOSIVE':
                    detonate_brick(ab)

    # Main Game Loop
    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        mouse_clicked = False

        # Event processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break
                
                if event.key == pygame.K_r:
                    # Restart Game Core
                    score = 0
                    lives = 3
                    game_over = False
                    victory = False
                    shield_active = False
                    balls = [Ball(WIDTH // 2, HEIGHT - 100)]
                    lasers.clear()
                    powerups.clear()
                    particles.clear()
                    paddle = Paddle()
                    build_brick_matrix()
                    active_powerup_banner = ""
                    banner_timer = 0
                    
                if event.key == pygame.K_SPACE and not game_over and not victory:
                    # Trigger laser if active
                    if paddle.laser_active:
                        play_sfx("laser")
                        lasers.append(LaserBolt(paddle.rect.x + 5, paddle.rect.y))
                        lasers.append(LaserBolt(paddle.rect.right - 5, paddle.rect.y))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
                    # Mouse click fires lasers as well
                    if paddle.laser_active and not game_over and not victory:
                        play_sfx("laser")
                        lasers.append(LaserBolt(paddle.rect.x + 5, paddle.rect.y))
                        lasers.append(LaserBolt(paddle.rect.right - 5, paddle.rect.y))

        # Horizontal Steering Keyboard Inputs
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            paddle.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            paddle.move(1)

        # Update Logic
        if not game_over and not victory:
            paddle.update()
            
            # Update banner timer
            if banner_timer > 0:
                banner_timer -= 1
            else:
                active_powerup_banner = ""

            # 1. Update stars background
            for star in stars:
                star.update()

            # 2. Update balls
            for ball in list(balls):
                ball.update()

                # Boundary Collision: Left / Right walls
                if ball.x - ball.radius < 10:
                    ball.x = 10 + ball.radius
                    ball.vx *= -1
                    trigger_shake(3, 2)
                elif ball.x + ball.radius > WIDTH - 10:
                    ball.x = WIDTH - 10 - ball.radius
                    ball.vx *= -1
                    trigger_shake(3, 2)

                # Boundary Collision: Ceiling
                if ball.y - ball.radius < 60:  # Top HUD height boundary
                    ball.y = 60 + ball.radius
                    ball.vy *= -1
                    trigger_shake(3, 2)

                # Boundary Collision: Bottom wall (lose ball)
                if ball.y + ball.radius > HEIGHT:
                    if ball in balls:
                        balls.remove(ball)

                # Bottom Safety Shield Deflect
                if shield_active and ball.y + ball.radius >= shield_y:
                    ball.y = shield_y - ball.radius
                    ball.vy *= -1
                    shield_active = False # consumed
                    play_sfx("paddle")
                    trigger_shake(6, 4)
                    active_powerup_banner = "SHIELD CONSUMED"
                    banner_timer = 60

                # Collision: Ball with Paddle
                # Check bounding box overlap first
                if ball.vy > 0:  # Only deflect if falling
                    ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius*2, ball.radius*2)
                    if ball_rect.colliderect(paddle.rect):
                        ball.y = paddle.rect.y - ball.radius
                        ball.vy *= -1
                        
                        # Calculate impact displacement to steer reflection angle
                        hit_offset = (ball.x - paddle.rect.centerx) / (paddle.rect.width / 2.0)
                        # Steer horizontally based on where it hit the paddle
                        ball.vx = ball.speed * 1.3 * hit_offset
                        # Re-normalize speed
                        current_speed = math.hypot(ball.vx, ball.vy)
                        ball.vx = (ball.vx / current_speed) * ball.speed
                        ball.vy = -(abs(ball.vy) / current_speed) * ball.speed
                        
                        play_sfx("paddle")
                        trigger_shake(4, 3)

                # Collision: Ball with Bricks
                ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius*2, ball.radius*2)
                for brick in list(bricks):
                    if ball_rect.colliderect(brick.rect):
                        # Determine side of impact
                        overlap_left = ball.x + ball.radius - brick.rect.x
                        overlap_right = brick.rect.right - (ball.x - ball.radius)
                        overlap_top = ball.y + ball.radius - brick.rect.y
                        overlap_bottom = brick.rect.bottom - (ball.y - ball.radius)
                        
                        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                        
                        if min_overlap == overlap_left:
                            ball.vx = -abs(ball.vx)
                            ball.x = brick.rect.x - ball.radius
                        elif min_overlap == overlap_right:
                            ball.vx = abs(ball.vx)
                            ball.x = brick.rect.right + ball.radius
                        elif min_overlap == overlap_top:
                            ball.vy = -abs(ball.vy)
                            ball.y = brick.rect.y - ball.radius
                        elif min_overlap == overlap_bottom:
                            ball.vy = abs(ball.vy)
                            ball.y = brick.rect.bottom + ball.radius

                        # Resolve hit logic
                        score += 50 # direct impact score
                        if brick.hit():
                            score += brick.score_val
                            spawn_brick_particles(brick)
                            if brick in bricks:
                                bricks.remove(brick)
                            
                            # Explosive core impact
                            if brick.category == 'EXPLOSIVE':
                                detonate_brick(brick)
                            else:
                                play_sfx("brick_standard" if brick.category == 'STANDARD' else "brick_armored")

                            # Procedural Powerup spawning
                            if random.random() < 0.22:
                                p_type = random.choice(['MULTIBALL', 'LASER', 'SHIELD'])
                                powerups.append(PowerUpPod(brick.rect.centerx, brick.rect.bottom, p_type))
                        else:
                            play_sfx("brick_armored")
                            trigger_shake(4, 2)
                        break # process next ball or next frame

            # 3. Update Lasers
            for laser in list(lasers):
                laser.update()
                if laser.y < 50:
                    lasers.remove(laser)
                    continue
                
                # Check hit with bricks
                for brick in list(bricks):
                    if laser.rect.colliderect(brick.rect):
                        if laser in lasers:
                            lasers.remove(laser)
                        
                        score += 30
                        if brick.hit():
                            score += brick.score_val
                            spawn_brick_particles(brick)
                            if brick in bricks:
                                bricks.remove(brick)
                            if brick.category == 'EXPLOSIVE':
                                detonate_brick(brick)
                            else:
                                play_sfx("brick_standard" if brick.category == 'STANDARD' else "brick_armored")
                        else:
                            play_sfx("brick_armored")
                        break

            # 4. Update Powerup Pods
            for p_pod in list(powerups):
                p_pod.update()
                if p_pod.y > HEIGHT:
                    powerups.remove(p_pod)
                    continue
                
                # Catch with paddle
                if p_pod.rect.colliderect(paddle.rect):
                    play_sfx("powerup")
                    powerups.remove(p_pod)
                    score += 200
                    
                    if p_pod.type == 'MULTIBALL':
                        # Spawn 2 new balls
                        active_powerup_banner = "MULTIBALL CORE ENGAGED"
                        banner_timer = 90
                        if len(balls) > 0:
                            b_source = balls[0]
                            # Spawn left/right angled balls
                            b1 = Ball(b_source.x, b_source.y)
                            b1.vx, b1.vy = -4, -4
                            b2 = Ball(b_source.x, b_source.y)
                            b2.vx, b2.vy = 4, -4
                            balls.append(b1)
                            balls.append(b2)
                        else:
                            balls.append(Ball(WIDTH//2, HEIGHT - 100))
                    elif p_pod.type == 'LASER':
                        active_powerup_banner = "LASER CANNONS READY (SPACE / CLICK)"
                        banner_timer = 120
                        paddle.laser_active = True
                        paddle.laser_timer = 400 # frames active
                    elif p_pod.type == 'SHIELD':
                        active_powerup_banner = "SAFETY DEFLECTION CORE CHARGED"
                        banner_timer = 90
                        shield_active = True

            # 5. Check Life depletion / Game Over
            if len(balls) == 0:
                lives -= 1
                trigger_shake(15, 6)
                if lives <= 0:
                    game_over = True
                    play_sfx("gameover")
                    # Submit high score via API
                    if arcade_api:
                        arcade_api.submit_score("Neon Breakout", score)
                else:
                    # Spawn new ball
                    balls.append(Ball(WIDTH // 2, HEIGHT - 120))

            # 6. Check Victory
            if len(bricks) == 0:
                victory = True
                play_sfx("victory")
                if arcade_api:
                    arcade_api.submit_score("Neon Breakout", score)

            # 7. Update explosive brick flashing
            for brick in bricks:
                brick.update()

        # Update particles
        for p in list(particles):
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # RENDER GRAPHICS
        # Draw background and neon borders
        game_surface.fill(DARK_BG)
        
        # Draw stars
        for star in stars:
            star.draw(game_surface)
            
        # Draw grid accent lines
        for gx in range(0, WIDTH, 80):
            pygame.draw.line(game_surface, (15, 15, 30), (gx, 60), (gx, HEIGHT))
        for gy in range(60, HEIGHT, 80):
            pygame.draw.line(game_surface, (15, 15, 30), (0, gy), (WIDTH, gy))

        # Draw Side Borders
        pygame.draw.rect(game_surface, (25, 25, 45), (0, 60, WIDTH, HEIGHT-60), 10, border_radius=5)
        # Inner thin glowing neon border
        pygame.draw.rect(game_surface, NEON_BLUE, (5, 65, WIDTH-10, HEIGHT-70), 2, border_radius=3)

        # Draw Bricks
        for brick in bricks:
            brick.draw(game_surface)

        # Draw Lasers
        for laser in lasers:
            laser.draw(game_surface)

        # Draw Powerups
        for p_pod in powerups:
            p_pod.draw(game_surface)

        # Draw Safety Shield line
        if shield_active:
            pygame.draw.line(game_surface, NEON_GREEN, (15, shield_y), (WIDTH - 15, shield_y), 3)
            # Fading particle pulse underneath
            if random.random() < 0.3:
                particles.append(Particle(random.randint(20, WIDTH-20), shield_y, 0, 0.5, NEON_GREEN))

        # Draw Paddle & Balls
        paddle.draw(game_surface)
        for ball in balls:
            ball.draw(game_surface)

        # Draw Particles
        for p in particles:
            p.draw(game_surface)

        # Draw HUD (Score & Lives & Powerup Banners)
        # HUD divider line
        pygame.draw.line(game_surface, (30, 30, 55), (0, 60), (WIDTH, 60), 3)
        pygame.draw.line(game_surface, NEON_BLUE, (0, 60), (WIDTH, 60), 1)

        # Score text
        score_lbl = FONT_HUD.render("SCORE MATRIX", True, NEON_BLUE)
        score_val = FONT_HUD.render(f"{score:06d}", True, WHITE)
        game_surface.blit(score_lbl, (20, 12))
        game_surface.blit(score_val, (20, 32))

        # Center Powerup Banner
        if active_powerup_banner:
            banner_surf = FONT_HUD.render(active_powerup_banner, True, NEON_GREEN if "SHIELD" in active_powerup_banner or "SAFETY" in active_powerup_banner else NEON_PINK)
            game_surface.blit(banner_surf, (WIDTH//2 - banner_surf.get_width()//2, 22))

        # Lives indicator
        lives_lbl = FONT_HUD.render("MATRIX CORES", True, NEON_PINK)
        game_surface.blit(lives_lbl, (WIDTH - 150, 12))
        # Draw little pink capsules for lives
        for l in range(3):
            lx = WIDTH - 150 + l * 24
            ly = 34
            l_rect = pygame.Rect(lx, ly, 16, 10)
            if l < lives:
                pygame.draw.rect(game_surface, NEON_PINK, l_rect, border_radius=3)
                pygame.draw.rect(game_surface, WHITE, (lx + 2, ly + 2, 12, 6), border_radius=2)
            else:
                pygame.draw.rect(game_surface, (35, 20, 35), l_rect, 1, border_radius=3)

        # Render Game Over or Victory Banners
        if game_over or victory:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (5, 5, 12, 220), (0, 0, WIDTH, HEIGHT))
            game_surface.blit(overlay, (0, 0))

            banner_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
            bg_border = NEON_GREEN if victory else NEON_PINK
            pygame.draw.rect(game_surface, (15, 15, 30), banner_rect, border_radius=15)
            pygame.draw.rect(game_surface, bg_border, banner_rect, 3, border_radius=15)

            title_str = "GRID CLEARED" if victory else "MATRIX OFFLINE"
            over_title = FONT_LARGE.render(title_str, True, bg_border)
            final_score_txt = FONT_HUD.render(f"FINAL SCORE: {score}", True, WHITE)
            restart_hint = FONT_HUD.render("PRESS 'R' TO RESTART SYSTEM", True, NEON_BLUE)

            game_surface.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3 + 30))
            game_surface.blit(final_score_txt, (WIDTH // 2 - final_score_txt.get_width() // 2, HEIGHT // 3 + 90))
            game_surface.blit(restart_hint, (WIDTH // 2 - restart_hint.get_width() // 2, HEIGHT // 3 + 130))

        # Handle screen shake offsets
        if shake_duration > 0:
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
            shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        # Blit game layout to hardware display window
        WIN.fill((0, 0, 0))
        WIN.blit(game_surface, (offset_x, offset_y))
        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
