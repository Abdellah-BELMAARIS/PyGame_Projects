import pygame
import os
import asyncio
import random

# Initialize Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Divide - Galaxy Versus")

# Colors (Cyberpunk Neon Palette)
DARK_BG = (8, 8, 16)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game elements
BORDER_WIDTH = 8
BORDER = pygame.Rect(WIDTH // 2 - BORDER_WIDTH // 2, 0, BORDER_WIDTH, HEIGHT)
BORDER_COLOR = (180, 0, 255)  # Neon Purple Laser Wall

# Fonts
try:
    HEALTH_FONT = pygame.font.SysFont('Outfit', 22, bold=True)
    WINNER_FONT = pygame.font.SysFont('Outfit', 65, bold=True)
    HUD_LABEL_FONT = pygame.font.SysFont('Outfit', 14, bold=True)
except:
    try:
        HEALTH_FONT = pygame.font.SysFont('Segoe UI', 22, bold=True)
        WINNER_FONT = pygame.font.SysFont('Segoe UI', 65, bold=True)
        HUD_LABEL_FONT = pygame.font.SysFont('Segoe UI', 14, bold=True)
    except:
        HEALTH_FONT = pygame.font.Font(None, 22)
        WINNER_FONT = pygame.font.Font(None, 65)
        HUD_LABEL_FONT = pygame.font.Font(None, 14)

FPS = 60
VEL = 5
BULLET_VEL = 9
MAX_BULLETS = 4
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Load assets
try:
    YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png')).convert_alpha()
    YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

    RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_red.png')).convert_alpha()
    RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

    SPACE_RAW = pygame.image.load(os.path.join('Assets', 'space.png')).convert()
    SPACE = pygame.transform.scale(SPACE_RAW, (WIDTH, HEIGHT))
    HAS_ASSETS = True
except Exception as e:
    print(f"Error loading assets: {e}. Using vector fallback.")
    HAS_ASSETS = False


# Particle Classes
class ThrusterParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-0.8, 0.8)
        self.life = random.randint(8, 15)
        self.max_life = self.life
        self.color = color

    def update(self, direction_factor):
        # Move opposite to the heading direction
        self.x -= direction_factor * 1.5
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class HitSpark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4.5, 4.5)
        self.vy = random.uniform(-4.5, 4.5)
        self.life = random.randint(12, 24)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 3) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


def draw_hud(win, red_health, yellow_health):
    # Left Player (Yellow/Cyan) HUD Panel
    h_width, h_height = 200, 48
    
    # Yellow/Cyan side HUD
    y_hud_surf = pygame.Surface((h_width, h_height), pygame.SRCALPHA)
    pygame.draw.rect(y_hud_surf, (10, 20, 32, 170), (0, 0, h_width, h_height), border_radius=6)
    win.blit(y_hud_surf, (20, 20))
    pygame.draw.rect(win, NEON_BLUE, (20, 20, h_width, h_height), 1, border_radius=6)

    # Health Bar left
    lbl_left = HUD_LABEL_FONT.render("CYBER FIGHTER I", True, NEON_BLUE)
    win.blit(lbl_left, (32, 24))
    
    # Draw Health Bar
    pygame.draw.rect(win, (25, 25, 45), (32, 44, 150, 10), border_radius=3)
    health_bar_w = int(150 * (yellow_health / 10.0))
    if health_bar_w > 0:
        pygame.draw.rect(win, NEON_BLUE, (32, 44, health_bar_w, 10), border_radius=3)

    # Right Player (Red/Pink) HUD Panel
    r_hud_surf = pygame.Surface((h_width, h_height), pygame.SRCALPHA)
    pygame.draw.rect(r_hud_surf, (24, 10, 20, 170), (0, 0, h_width, h_height), border_radius=6)
    win.blit(r_hud_surf, (WIDTH - h_width - 20, 20))
    pygame.draw.rect(win, NEON_PINK, (WIDTH - h_width - 20, 20, h_width, h_height), 1, border_radius=6)

    # Health Bar right
    lbl_right = HUD_LABEL_FONT.render("CYBER FIGHTER II", True, NEON_PINK)
    win.blit(lbl_right, (WIDTH - h_width - 20 + 18, 24))
    
    pygame.draw.rect(win, (25, 25, 45), (WIDTH - h_width - 20 + 18, 44, 150, 10), border_radius=3)
    health_bar_r_w = int(150 * (red_health / 10.0))
    if health_bar_r_w > 0:
        pygame.draw.rect(win, NEON_PINK, (WIDTH - h_width - 20 + 18, 44, health_bar_r_w, 10), border_radius=3)


def draw_laser(surface, rect, color):
    # Draw glowing neon vector bar instead of solid block
    pygame.draw.rect(surface, (color[0]//4, color[1]//4, color[2]//4), rect, border_radius=2)
    pygame.draw.rect(surface, color, rect, 1, border_radius=2)
    # Inner bright white core
    pygame.draw.rect(surface, WHITE, (rect.x + 2, rect.y + 1, rect.width - 4, rect.height - 2), border_radius=1)


def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, thruster_particles, hit_sparks, level=1, obstacles=[]):
    # Background
    if HAS_ASSETS:
        WIN.blit(SPACE, (0, 0))
    else:
        WIN.fill(DARK_BG)
        # Draw ambient background stars
        random.seed(42)  # Static seed for star positions
        for _ in range(35):
            sx = random.randint(0, WIDTH)
            sy = random.randint(0, HEIGHT)
            pygame.draw.circle(WIN, (80, 80, 110), (sx, sy), 1)

    # Draw laser divider line (glowing fence)
    pygame.draw.rect(WIN, (BORDER_COLOR[0] // 5, BORDER_COLOR[1] // 5, BORDER_COLOR[2] // 5), BORDER)
    pygame.draw.rect(WIN, BORDER_COLOR, BORDER, 1)
    
    # Draw level HUD text
    level_txt = WINNER_FONT.render(f"STAGE {level}/20", True, (255, 255, 255))
    level_scale = pygame.transform.scale(level_txt, (level_txt.get_width() // 2, level_txt.get_height() // 2))
    WIN.blit(level_scale, (WIDTH // 2 - level_scale.get_width() // 2, 20))

    # Draw obstacles
    for obs in obstacles:
        pygame.draw.rect(WIN, NEON_GREEN, obs, border_radius=4)
        pygame.draw.rect(WIN, WHITE, (obs.x + 3, obs.y + 3, obs.width - 6, obs.height - 6), border_radius=2)

    # Draw thruster flame trails
    for p in thruster_particles:
        p.draw(WIN)

    # Draw hit sparks
    for p in hit_sparks:
        p.draw(WIN)

    # Draw spaceships
    if HAS_ASSETS:
        WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
        WIN.blit(RED_SPACESHIP, (red.x, red.y))
    else:
        # Fallback: Vector glowing triangles
        # Player 1 (Yellow / Cyan) facing right
        p1_pts = [(yellow.x, yellow.y), (yellow.x + SPACESHIP_WIDTH, yellow.y + SPACESHIP_HEIGHT//2), (yellow.x, yellow.y + SPACESHIP_HEIGHT)]
        pygame.draw.polygon(WIN, NEON_BLUE, p1_pts, 2)
        # Player 2 (Red / Pink) facing left
        p2_pts = [(red.x + SPACESHIP_WIDTH, red.y), (red.x, red.y + SPACESHIP_HEIGHT//2), (red.x + SPACESHIP_WIDTH, red.y + SPACESHIP_HEIGHT)]
        pygame.draw.polygon(WIN, NEON_PINK, p2_pts, 2)

    # Draw glowing lasers
    for bullet in red_bullets:
        draw_laser(WIN, bullet, NEON_PINK)

    for bullet in yellow_bullets:
        draw_laser(WIN, bullet, NEON_BLUE)

    # Draw HUD
    draw_hud(WIN, red_health, yellow_health)
    pygame.display.update()


def yellow_handle_movement(keys_pressed, yellow):
    move_left = keys_pressed[pygame.K_a] or keys_pressed[pygame.K_q]
    move_right = keys_pressed[pygame.K_d]
    move_up = keys_pressed[pygame.K_w] or keys_pressed[pygame.K_z]
    move_down = keys_pressed[pygame.K_s]

    if move_left and yellow.x - VEL > 0:
        yellow.x -= VEL
    if move_right and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if move_up and yellow.y - VEL > 0:
        yellow.y -= VEL
    if move_down and yellow.y + VEL + yellow.height < HEIGHT - 15:
        yellow.y += VEL


def handle_bullets(yellow_bullets, red_bullets, yellow, red, hit_sparks, state_bag, obstacles=[]):
    for bullet in yellow_bullets[:]:
        hit_obs = False
        for obs in obstacles:
            if bullet.colliderect(obs):
                hit_obs = True
                for _ in range(6):
                    hit_sparks.append(HitSpark(bullet.x, bullet.y, NEON_GREEN))
                break
        if hit_obs:
            yellow_bullets.remove(bullet)
            continue
            
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            for _ in range(12):
                hit_sparks.append(HitSpark(bullet.x, bullet.y, NEON_BLUE))
            state_bag["shake_duration"] = 10
            state_bag["shake_amount"] = 5
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        hit_obs = False
        for obs in obstacles:
            if bullet.colliderect(obs):
                hit_obs = True
                for _ in range(6):
                    hit_sparks.append(HitSpark(bullet.x, bullet.y, NEON_GREEN))
                break
        if hit_obs:
            red_bullets.remove(bullet)
            continue
            
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            for _ in range(12):
                hit_sparks.append(HitSpark(bullet.x, bullet.y, NEON_PINK))
            state_bag["shake_duration"] = 10
            state_bag["shake_amount"] = 5
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)


async def draw_winner(text, border_color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (5, 5, 12, 215), (0, 0, WIDTH, HEIGHT))
    WIN.blit(overlay, (0, 0))

    card_w, card_h = 560, 240
    card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
    
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (15, 15, 32, 230), (0, 0, card_w, card_h), border_radius=15)
    WIN.blit(card_surf, (card_x, card_y))
    pygame.draw.rect(WIN, border_color, (card_x, card_y, card_w, card_h), 3, border_radius=15)

    draw_text = WINNER_FONT.render(text, 1, border_color)
    restart_text = HEALTH_FONT.render("PRESS R TO RESTART COMBAT GRID", 1, WHITE)
    
    WIN.blit(draw_text, (WIDTH // 2 - draw_text.get_width() // 2, card_y + 50))
    WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, card_y + 140))
    pygame.display.update()


async def main():
    level = 1
    max_levels = 20
    score = 0
    score_submitted = False
    start_time = time.time()

    def get_obstacles(lvl):
        obs = []
        sp = []
        if lvl >= 6:
            num = min(4, 1 + lvl // 4)
            for i in range(num):
                rect = pygame.Rect(WIDTH // 2 - 12, 80 + i * 110, 24, 60)
                obs.append(rect)
                sp.append(1.5 + lvl * 0.08)
        return obs, sp

    while True:
        red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
        yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

        red_bullets = []
        yellow_bullets = []

        red_health = 10
        yellow_health = 10

        thruster_particles = []
        hit_sparks = []

        state_bag = {
            "shake_duration": 0,
            "shake_amount": 0
        }

        obstacles, obs_speeds = get_obstacles(level)
        clock = pygame.time.Clock()
        run = True
        level_won = False
        game_over = False
        
        while run:
            clock.tick(FPS)
            elapsed_time = int(time.time() - start_time)

            # Move obstacles
            for i in range(len(obstacles)):
                obstacles[i].y += obs_speeds[i]
                if obstacles[i].y < 40 or obstacles[i].y > HEIGHT - 90:
                    obs_speeds[i] *= -1

            for p in thruster_particles[:]:
                belongs_to_p1 = p.color == NEON_BLUE
                p.update(1 if belongs_to_p1 else -1)
                if p.life <= 0:
                    thruster_particles.remove(p)

            for p in hit_sparks[:]:
                p.update()
                if p.life <= 0:
                    hit_sparks.remove(p)

            # Keyboard P1 movement and shooting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                        bullet = pygame.Rect(
                            yellow.x + yellow.width, yellow.y + yellow.height // 2 - 2, 14, 4)
                        yellow_bullets.append(bullet)

                if event.type == RED_HIT:
                    red_health -= 1

                if event.type == YELLOW_HIT:
                    yellow_health -= 1

            # Check winner conditions
            if red_health <= 0:
                level_won = True
                run = False
                break
            elif yellow_health <= 0:
                game_over = True
                run = False
                break

            # CPU P2 AI Steering and fire controls
            cpu_speed = 1.6 + level * 0.2
            target_y = yellow.y
            if random.random() < 0.08:
                target_y += random.uniform(-30, 30)
            cpu_center = red.y + red.height // 2
            if cpu_center < target_y:
                red.y += min(cpu_speed, target_y - cpu_center)
            elif cpu_center > target_y:
                red.y -= min(cpu_speed, cpu_center - target_y)
            red.y = max(0, min(HEIGHT - red.height - 15, red.y))

            # CPU Fire laser
            shoot_prob = 0.015 + level * 0.003
            if random.random() < shoot_prob and len(red_bullets) < MAX_BULLETS:
                bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 14, 4)
                red_bullets.append(bullet)

            keys_pressed = pygame.key.get_pressed()
            yellow_handle_movement(keys_pressed, yellow)

            # Thruster flame P1 and CPU
            if random.random() < 0.6:
                thruster_particles.append(ThrusterParticle(yellow.x, yellow.y + SPACESHIP_HEIGHT // 2, NEON_BLUE))
            if random.random() < 0.6:
                thruster_particles.append(ThrusterParticle(red.x + SPACESHIP_WIDTH, red.y + SPACESHIP_HEIGHT // 2, NEON_PINK))

            handle_bullets(yellow_bullets, red_bullets, yellow, red, hit_sparks, state_bag, obstacles)

            if state_bag["shake_duration"] > 0:
                offset_x = random.randint(-state_bag["shake_amount"], state_bag["shake_amount"])
                offset_y = random.randint(-state_bag["shake_amount"], state_bag["shake_amount"])
                state_bag["shake_duration"] -= 1
            else:
                offset_x = 0
                offset_y = 0

            if offset_x != 0 or offset_y != 0:
                shaken_surface = pygame.Surface((WIDTH, HEIGHT))
                draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, thruster_particles, hit_sparks, level, obstacles)
                shaken_surface.blit(WIN, (0, 0))
                WIN.fill(BLACK)
                WIN.blit(shaken_surface, (offset_x, offset_y))
                pygame.display.update()
            else:
                draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, thruster_particles, hit_sparks, level, obstacles)

            await asyncio.sleep(0)

        # Draw level victory / game over
        if level_won:
            state_bag["shake_duration"] = 30
            state_bag["shake_amount"] = 12
            score += 1000 + max(0, 1000 - elapsed_time * 5)
            
            if level >= max_levels:
                # Game Victory!
                if not score_submitted:
                    score_submitted = True
                    if arcade_api:
                        arcade_api.submit_score("Galaxy Fight", score)
                await draw_winner(f"GRID CHAMPION! SCORE: {score}", NEON_GREEN)
            else:
                # Level transition banner
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(overlay, (5, 5, 12, 215), (0, 0, WIDTH, HEIGHT))
                WIN.blit(overlay, (0, 0))

                card_w, card_h = 560, 240
                card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
                pygame.draw.rect(WIN, NEON_GREEN, (card_x, card_y, card_w, card_h), 3, border_radius=15)
                draw_text = WINNER_FONT.render(f"STAGE {level} CLEARED!", 1, NEON_GREEN)
                sub_text = HEALTH_FONT.render("PROCEEDING TO NEXT VECTOR GRID...", 1, WHITE)
                WIN.blit(draw_text, (WIDTH // 2 - draw_text.get_width() // 2, card_y + 60))
                WIN.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, card_y + 130))
                pygame.display.update()
                await asyncio.sleep(2.5)
                level += 1
                continue
        elif game_over:
            if not score_submitted:
                score_submitted = True
                if arcade_api:
                    arcade_api.submit_score("Galaxy Fight", score)
            await draw_winner("SYSTEM DEFEAT", NEON_PINK)

        # Wait for keypress R to reboot
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        level = 1
                        score = 0
                        score_submitted = False
                        start_time = time.time()
                        waiting = False
            await asyncio.sleep(0.02)


if __name__ == "__main__":
    asyncio.run(main())
