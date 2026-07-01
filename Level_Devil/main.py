import pygame
import asyncio
import sys
import random
import math
import time

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
pygame.display.set_caption("Level Devil - Neon Troll Edition")
FPS = 60

# Neon Colors
DARK_BG = (8, 8, 16)
GRID_LINE = (18, 18, 32)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
NEON_PURPLE = (180, 0, 255)
NEON_ORANGE = (255, 120, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
GRAY = (100, 100, 120)

# Fonts
try:
    FONT_HUD = pygame.font.SysFont("Outfit", 20, bold=True)
    FONT_HUD_VAL = pygame.font.SysFont("Outfit", 24, bold=True)
    FONT_LARGE = pygame.font.SysFont("Outfit", 55, bold=True)
    FONT_SUB = pygame.font.SysFont("Outfit", 22, bold=True)
except:
    try:
        FONT_HUD = pygame.font.SysFont("Segoe UI", 20, bold=True)
        FONT_HUD_VAL = pygame.font.SysFont("Segoe UI", 24, bold=True)
        FONT_LARGE = pygame.font.SysFont("Segoe UI", 55, bold=True)
        FONT_SUB = pygame.font.SysFont("Segoe UI", 22, bold=True)
    except:
        FONT_HUD = pygame.font.Font(None, 20)
        FONT_HUD_VAL = pygame.font.Font(None, 24)
        FONT_LARGE = pygame.font.Font(None, 55)
        FONT_SUB = pygame.font.Font(None, 22)


class TrailParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.life = random.randint(15, 25)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        size = int((self.life / self.max_life) * 5) + 1
        # draw neon glowing circle
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
        surface.blit(s, (int(self.x - size), int(self.y - size)))


class ShockwaveParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 2
        self.max_radius = 45
        self.life = 20
        self.max_life = self.life
        self.color = color

    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.15
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0: return
        alpha = int((self.life / self.max_life) * 200)
        thickness = max(1, int((self.life / self.max_life) * 4))
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.radius, self.radius), int(self.radius), thickness)
        surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.x_vel = 0
        self.y_vel = 0
        self.on_ground = False
        self.alive = True
        self.scale = 1.0 # for tiny mode
        self.deaths = 0

    def get_rect(self):
        w = int(self.width * self.scale)
        h = int(self.height * self.scale)
        return pygame.Rect(self.x, self.y, w, h)

    def update(self, blocks, gravity_dir=1):
        # Apply gravity
        self.y_vel += 0.5 * gravity_dir
        if abs(self.y_vel) > 12:
            self.y_vel = 12 * (1 if self.y_vel > 0 else -1)

        # Move X
        self.x += self.x_vel
        self.x_vel *= 0.82 # Friction
        if abs(self.x_vel) < 0.1:
            self.x_vel = 0

        # Collision X
        player_rect = self.get_rect()
        for block in blocks:
            if player_rect.colliderect(block.rect) and block.solid:
                if self.x_vel > 0:
                    self.x = block.rect.left - player_rect.width
                elif self.x_vel < 0:
                    self.x = block.rect.right
                self.x_vel = 0
                player_rect = self.get_rect()

        # Move Y
        self.y += self.y_vel

        # Collision Y
        self.on_ground = False
        player_rect = self.get_rect()
        for block in blocks:
            if player_rect.colliderect(block.rect) and block.solid:
                if gravity_dir == 1:
                    if self.y_vel > 0:
                        self.y = block.rect.top - player_rect.height
                        self.on_ground = True
                        self.y_vel = 0
                    elif self.y_vel < 0:
                        self.y = block.rect.bottom
                        self.y_vel = 0
                else: # Inverted gravity
                    if self.y_vel < 0:
                        self.y = block.rect.bottom
                        self.on_ground = True
                        self.y_vel = 0
                    elif self.y_vel > 0:
                        self.y = block.rect.top - player_rect.height
                        self.y_vel = 0
                player_rect = self.get_rect()

    def draw(self, surface, gravity_dir=1):
        if not self.alive: return
        rect = self.get_rect()
        
        # Glow outer rect
        glow_color = NEON_BLUE
        for offset in range(1, 4):
            pygame.draw.rect(surface, (max(0, glow_color[0]-60), max(0, glow_color[1]-60), max(0, glow_color[2]-60)),
                             (rect.x - offset, rect.y - offset, rect.width + offset*2, rect.height + offset*2), 1, border_radius=4)
        
        # Base body
        pygame.draw.rect(surface, NEON_BLUE, rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, (rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4), border_radius=2)
        
        # Eyes based on gravity direction
        eye_y = rect.y + 6 if gravity_dir == 1 else rect.y + rect.height - 12
        pygame.draw.rect(surface, DARK_BG, (rect.x + 6, eye_y, 4, 6), border_radius=1)
        pygame.draw.rect(surface, DARK_BG, (rect.x + rect.width - 10, eye_y, 4, 6), border_radius=1)


class Block:
    def __init__(self, x, y, w, h, solid=True, color=NEON_PURPLE, is_lava=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.solid = solid
        self.color = color
        self.is_lava = is_lava
        self.orig_y = y
        self.orig_x = x
        self.vy = 0
        self.vx = 0
        self.falling = False
        self.vanishing = False
        self.vanish_timer = 0
        self.visible = True

    def update(self):
        if self.falling:
            self.vy += 0.4
            self.rect.y += int(self.vy)
        if self.vanishing and self.visible:
            self.vanish_timer -= 1
            if self.vanish_timer <= 0:
                self.visible = False
                self.solid = False

    def draw(self, surface):
        if not self.visible: return
        
        if self.is_lava:
            # Lava wave pulse
            t = pygame.time.get_ticks() * 0.005
            glow = int(180 + 75 * math.sin(t))
            color = (glow, 20, 0)
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, NEON_PINK, self.rect, 2)
        else:
            # Draw standard glowing grid platform
            pygame.draw.rect(surface, (self.color[0]//5, self.color[1]//5, self.color[2]//5), self.rect, border_radius=2)
            pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=2)


class Spike:
    def __init__(self, x, y, w=30, h=30, dir="up", color=NEON_PINK):
        self.rect = pygame.Rect(x, y, w, h)
        self.dir = dir
        self.color = color
        self.orig_x = x
        self.orig_y = y
        self.vy = 0
        self.vx = 0
        self.active = False

    def update(self):
        if self.active:
            self.rect.x += int(self.vx)
            self.rect.y += int(self.vy)

    def draw(self, surface):
        x, y, w, h = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        if self.dir == "up":
            points = [(x + w//2, y), (x, y + h), (x + w, y + h)]
        elif self.dir == "down":
            points = [(x + w//2, y + h), (x, y), (x + w, y)]
        elif self.dir == "left":
            points = [(x, y + h//2), (x + w, y), (x + w, y + h)]
        else: # right
            points = [(x + w, y + h//2), (x, y), (x, y + h)]

        # Spike glow
        pygame.draw.polygon(surface, (self.color[0]//4, self.color[1]//4, self.color[2]//4), points)
        pygame.draw.polygon(surface, self.color, points, 2)


class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = NEON_GREEN
        self.pulse = 0
        self.is_fake = False
        self.moving = False
        self.orig_x = x
        self.orig_y = y

    def draw(self, surface):
        self.pulse = (self.pulse + 0.1) % (math.pi * 2)
        offset = math.sin(self.pulse) * 4
        
        px, py, pw, ph = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        
        # Neon green oval ring
        glow_surf = pygame.Surface((pw + 16, ph + 16), pygame.SRCALPHA)
        col = (self.color[0], self.color[1], self.color[2], int(100 + 40 * math.sin(self.pulse)))
        pygame.draw.ellipse(glow_surf, col, (8 - offset//2, 8 - offset//2, pw + offset, ph + offset), 3)
        surface.blit(glow_surf, (px - 8, py - 8))
        
        # Center core
        pygame.draw.ellipse(surface, WHITE if not self.is_fake else NEON_PINK, (px + 4, py + 4, pw - 8, ph - 8))
        pygame.draw.ellipse(surface, self.color, (px + 4, py + 4, pw - 8, ph - 8), 2)


class Key:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 15)
        self.color = GOLD
        self.orig_x = x
        self.orig_y = y
        self.active = False
        self.vx = 0
        self.vy = 0

    def update(self):
        if self.active:
            self.rect.x += int(self.vx)
            self.rect.y += int(self.vy)

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        # Glowing circle head
        pygame.draw.circle(surface, self.color, (x + 8, y + 7), 6, 2)
        # Key shaft
        pygame.draw.line(surface, self.color, (x + 14, y + 7), (x + 24, y + 7), 2)
        # Teeth
        pygame.draw.line(surface, self.color, (x + 20, y + 7), (x + 20, y + 12), 2)
        pygame.draw.line(surface, self.color, (x + 24, y + 7), (x + 24, y + 12), 2)


class DevilBoss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 120, 100)
        self.health = 3
        self.max_health = 3
        self.color = NEON_PINK
        self.shoot_timer = 0
        self.nodes_destroyed = 0

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        # Draw floating neon face
        t = pygame.time.get_ticks() * 0.004
        dy = int(math.sin(t) * 10)
        
        # Face body
        pygame.draw.rect(surface, (50, 0, 30), (x, y + dy, 120, 100), border_radius=10)
        pygame.draw.rect(surface, self.color, (x, y + dy, 120, 100), 3, border_radius=10)
        
        # Devil horns
        pygame.draw.polygon(surface, self.color, [(x + 10, y + dy), (x - 15, y - 20 + dy), (x + 35, y + dy)])
        pygame.draw.polygon(surface, self.color, [(x + 110, y + dy), (x + 135, y - 20 + dy), (x + 85, y + dy)])
        
        # Angry glowing eyes
        eye_color = NEON_PINK if self.health > 1 else WHITE
        pygame.draw.polygon(surface, eye_color, [(x + 25, y + 30 + dy), (x + 45, y + 40 + dy), (x + 20, y + 42 + dy)])
        pygame.draw.polygon(surface, eye_color, [(x + 95, y + 30 + dy), (x + 75, y + 40 + dy), (x + 100, y + 42 + dy)])
        
        # Devil grin
        pygame.draw.polygon(surface, self.color, [(x + 40, y + 70 + dy), (x + 80, y + 70 + dy), (x + 60, y + 90 + dy)], 2)
        
        # Health bar
        if self.health > 0:
            pygame.draw.rect(surface, GRAY, (x, y - 20 + dy, 120, 6))
            pygame.draw.rect(surface, NEON_PINK, (x, y - 20 + dy, int(120 * (self.health / self.max_health)), 6))


# -----------------------------------------------------------------------------
# LEVEL BUILDER
# -----------------------------------------------------------------------------
def load_level(level_num):
    blocks = []
    spikes = []
    portal = None
    key = None
    boss = None
    spawn_pos = (50, 480)
    gravity_dir = 1
    
    # Default Level layouts
    if level_num == 1:
        # Floor
        blocks.append(Block(0, 520, 800, 80))
        # Portal at right
        portal = Portal(700, 460)
        # Trap: A pillar of spikes rises in front of portal
        sp = Spike(600, 520, 40, 40, "up")
        sp.vy = -1.2 # rises up
        spikes.append(sp)

    elif level_num == 2:
        # Collapsing floor
        blocks.append(Block(0, 520, 250, 80))
        # Bridge blocks
        for i in range(5):
            b = Block(250 + i * 60, 520, 60, 20, color=NEON_BLUE)
            blocks.append(b)
        blocks.append(Block(550, 520, 250, 80))
        
        portal = Portal(700, 460)
        # Spikes in the pit below bridge
        for x in range(250, 550, 30):
            spikes.append(Spike(x, 560, 30, 40, "up"))

    elif level_num == 3:
        # Ceiling drop spikes
        blocks.append(Block(0, 520, 800, 80))
        # Archway/platform above
        blocks.append(Block(300, 380, 200, 30))
        
        portal = Portal(720, 460)
        # Hidden spikes hanging under the archway
        spikes.append(Spike(350, 300, 30, 30, "down"))
        spikes.append(Spike(420, 300, 30, 30, "down"))

    elif level_num == 4:
        # Shifting portal
        blocks.append(Block(0, 520, 800, 80))
        portal = Portal(700, 460)
        portal.moving = True

    elif level_num == 5:
        # locked portal, runaway key
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(200, 400, 100, 30))
        spikes.append(Spike(500, 490, 30, 30, "up"))
        
        portal = Portal(700, 460)
        key = Key(240, 360)

    elif level_num == 6:
        # Decaying platforms
        blocks.append(Block(0, 520, 150, 80))
        for i in range(4):
            b = Block(200 + i * 110, 420 - i * 30, 70, 20, color=NEON_BLUE)
            b.vanishing = True
            b.vanish_timer = 20
            blocks.append(b)
        blocks.append(Block(650, 220, 150, 380))
        portal = Portal(720, 160)
        
        for x in range(150, 650, 40):
            spikes.append(Spike(x, 570, 40, 30, "up"))

    elif level_num == 7:
        # Boulder roll
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(400, 350, 400, 30, color=NEON_ORANGE))
        
        portal = Portal(720, 460)
        boulder = Spike(750, 280, 50, 50, "up", color=NEON_PINK)
        boulder.vx = -4.5
        boulder.vy = 2
        spikes.append(boulder)

    elif level_num == 8:
        # Control Glitch (Inverted controls)
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(300, 400, 120, 30))
        blocks.append(Block(520, 400, 120, 30))
        portal = Portal(700, 460)
        for x in range(100, 700, 35):
            if x < 280 or x > 640 or (x > 420 and x < 520):
                spikes.append(Spike(x, 490, 30, 30, "up"))

    elif level_num == 9:
        # Gravity Inversion
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(0, 0, 800, 50))
        blocks.append(Block(380, 280, 40, 240))
        
        portal = Portal(700, 460)
        for x in range(100, 700, 40):
            spikes.append(Spike(x, 50, 30, 30, "down"))

    elif level_num == 10:
        # Spring bait
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(650, 300, 150, 30))
        portal = Portal(700, 240)
        
        spring = Block(350, 490, 40, 30, color=NEON_GREEN)
        blocks.append(spring)
        for x in range(300, 450, 30):
            spikes.append(Spike(x, 150, 30, 30, "down"))

    elif level_num == 11:
        # Spike rain
        blocks.append(Block(0, 520, 800, 80))
        portal = Portal(720, 460)
        for i in range(5):
            sp = Spike(250 + i * 90, -50, 30, 40, "down")
            sp.vy = 6.5
            spikes.append(sp)

    elif level_num == 12:
        # Floating portal, high key
        blocks.append(Block(0, 520, 200, 80))
        blocks.append(Block(600, 520, 200, 80))
        blocks.append(Block(350, 250, 100, 20, color=NEON_BLUE))
        key = Key(390, 210)
        
        spring = Block(150, 490, 40, 30, color=NEON_GREEN)
        blocks.append(spring)
        
        portal = Portal(700, 460)
        for x in range(200, 600, 40):
            spikes.append(Spike(x, 570, 40, 30, "up"))

    elif level_num == 13:
        # Double fakeout
        blocks.append(Block(0, 520, 800, 80))
        portal = Portal(700, 460)
        portal.is_fake = True
        
        blocks.append(Block(300, 430, 60, 90))
        spikes.append(Spike(300, 400, 30, 30, "up"))

    elif level_num == 14:
        # Scale shift
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(300, 350, 200, 140))
        blocks.append(Block(300, 0, 200, 310))
        portal = Portal(700, 460)

    elif level_num == 15:
        # Spike wall chase
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(200, 420, 80, 100))
        blocks.append(Block(380, 420, 80, 100))
        blocks.append(Block(560, 420, 80, 100))
        portal = Portal(720, 460)
        
        chaser = Spike(-100, 100, 80, 420, "right", color=NEON_PINK)
        chaser.vx = 2.4
        spikes.append(chaser)

    elif level_num == 16:
        # Shifting platforms
        blocks.append(Block(0, 520, 150, 80))
        mp1 = Block(250, 420, 80, 20, color=NEON_BLUE)
        mp1.vy = -1.5
        blocks.append(mp1)
        
        mp2 = Block(450, 250, 80, 20, color=NEON_BLUE)
        mp2.vx = -1.5
        blocks.append(mp2)
        
        blocks.append(Block(650, 520, 150, 80))
        portal = Portal(700, 460)
        
        for x in range(150, 650, 40):
            spikes.append(Spike(x, 570, 40, 30, "up"))

    elif level_num == 17:
        # Invisible ceiling barrier
        blocks.append(Block(0, 520, 800, 80))
        for x in range(250, 550, 30):
            spikes.append(Spike(x, 490, 30, 30, "up"))
            
        inv_block = Block(350, 320, 60, 30, color=DARK_BG, solid=False)
        blocks.append(inv_block)
        
        portal = Portal(700, 460)

    elif level_num == 18:
        # Rising lava
        blocks.append(Block(0, 520, 150, 80))
        blocks.append(Block(220, 420, 60, 20))
        blocks.append(Block(380, 320, 60, 20))
        blocks.append(Block(540, 220, 60, 20))
        blocks.append(Block(680, 160, 120, 440))
        
        portal = Portal(720, 100)
        lava = Block(0, 580, 800, 400, solid=False, is_lava=True)
        blocks.append(lava)

    elif level_num == 19:
        # Sliding patrol hazards
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(250, 380, 300, 20))
        
        portal = Portal(700, 460)
        s1 = Spike(300, 350, 30, 30, "up")
        s1.vx = 2.0
        spikes.append(s1)
        
        s2 = Spike(150, 490, 30, 30, "up")
        s2.vx = -1.5
        spikes.append(s2)

    elif level_num == 20:
        # The Final Boss
        blocks.append(Block(0, 520, 800, 80))
        blocks.append(Block(150, 380, 80, 20, color=NEON_BLUE))
        blocks.append(Block(360, 300, 80, 20, color=NEON_BLUE))
        blocks.append(Block(570, 380, 80, 20, color=NEON_BLUE))
        
        boss = DevilBoss(340, 80)
        
        btn1 = Block(185, 360, 10, 20, color=NEON_GREEN)
        btn2 = Block(395, 280, 10, 20, color=NEON_GREEN)
        btn3 = Block(605, 360, 10, 20, color=NEON_GREEN)
        blocks.append(btn1)
        blocks.append(btn2)
        blocks.append(btn3)
        
        portal = Portal(700, 460)
        portal.color = GRAY
        
    return blocks, spikes, portal, key, boss, spawn_pos, gravity_dir


def draw_neon_grid(surface):
    surface.fill(DARK_BG)
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, GRID_LINE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, GRID_LINE, (0, y), (WIDTH, y))


def draw_game_overlay(surface, title, subtitle, color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
    surface.blit(overlay, (0, 0))

    card_w, card_h = 550, 220
    card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (15, 15, 30, 230), (0, 0, card_w, card_h), border_radius=15)
    surface.blit(card_surf, (card_x, card_y))
    pygame.draw.rect(surface, color, (card_x, card_y, card_w, card_h), 3, border_radius=15)

    title_surf = FONT_LARGE.render(title, True, color)
    sub_surf = FONT_HUD.render(subtitle, True, WHITE)

    surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, card_y + 45))
    surface.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, card_y + 130))


async def main():
    run = True
    clock = pygame.time.Clock()

    level = 1
    max_levels = 20
    deaths = 0
    start_time = time.time()

    player = Player(50, 480)
    blocks, spikes, portal, key, boss, spawn_pos, gravity_dir = load_level(level)
    player.x, player.y = spawn_pos

    particles = []
    shake_duration = 0
    shake_amount = 0

    game_won = False
    score_submitted = False
    
    trap_triggered = False

    while run:
        clock.tick(FPS)
        
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        if shake_duration > 0:
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
            shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        game_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_neon_grid(game_surf)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if game_won or not player.alive:
                    if event.key == pygame.K_r:
                        if game_won:
                            level = 1
                            deaths = 0
                            start_time = time.time()
                            game_won = False
                            score_submitted = False
                        player.alive = True
                        blocks, spikes, portal, key, boss, spawn_pos, gravity_dir = load_level(level)
                        player.x, player.y = spawn_pos
                        player.x_vel = 0
                        player.y_vel = 0
                        player.scale = 1.0
                        trap_triggered = False
                        particles.clear()

        keys = pygame.key.get_pressed()
        if player.alive and not game_won:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.x_vel = -4.5 * player.scale
                if random.random() < 0.2:
                    particles.append(TrailParticle(player.x + player.width//2, player.y + player.height, NEON_BLUE))
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.x_vel = 4.5 * player.scale
                if random.random() < 0.2:
                    particles.append(TrailParticle(player.x + player.width//2, player.y + player.height, NEON_BLUE))
            
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and player.on_ground:
                player.y_vel = -10.5 * gravity_dir
                player.on_ground = False
                for _ in range(8):
                    particles.append(TrailParticle(player.x + player.width//2, player.y + (player.height if gravity_dir==1 else 0), WHITE))

        if player.alive and not game_won:
            player.update(blocks, gravity_dir)

            for block in blocks:
                block.update()
            for spike in spikes:
                spike.update()

            if player.y > HEIGHT + 100 or player.y < -100:
                player.alive = False
                deaths += 1
                shake_duration = 20
                shake_amount = 8
                for _ in range(20):
                    particles.append(TrailParticle(player.x + 15, player.y + 15, NEON_PINK))

            if level == 1:
                if player.x > 450 and not trap_triggered:
                    trap_triggered = True
                    for spike in spikes:
                        spike.active = True
                        spike.vy = -6.5

            elif level == 2:
                for block in blocks:
                    if block.color == NEON_BLUE:
                        player_rect = player.get_rect()
                        if player_rect.colliderect(pygame.Rect(block.rect.x, block.rect.y - 4, block.rect.width, 6)):
                            block.falling = True

            elif level == 3:
                if player.x > 300 and not trap_triggered:
                    trap_triggered = True
                    for spike in spikes:
                        if spike.dir == "down":
                            spike.active = True
                            spike.vy = 8.5

            elif level == 4:
                if player.x > 500 and not trap_triggered:
                    trap_triggered = True
                    portal.rect.x -= 220
                    for _ in range(12):
                        particles.append(TrailParticle(portal.orig_x + 20, portal.orig_y + 30, NEON_PINK))
                        particles.append(TrailParticle(portal.rect.x + 20, portal.rect.y + 30, NEON_GREEN))

            elif level == 5:
                if key and math.hypot(player.x - key.rect.x, player.y - key.rect.y) < 140:
                    key.active = True
                    key.vx = 4.8
                    key.vy = -1.5 if key.rect.y > 300 else 0
                if key and key.rect.x > 750:
                    key.vx = 0
                    key.rect.x = 750

            elif level == 6:
                for block in blocks:
                    if block.vanishing and not block.falling:
                        player_rect = player.get_rect()
                        if player_rect.colliderect(pygame.Rect(block.rect.x, block.rect.y - 4, block.rect.width, 6)):
                            block.vanishing = True
                            if block.vanish_timer == 20:
                                block.vanish_timer = 18

            elif level == 7:
                if player.x > 300 and not trap_triggered:
                    trap_triggered = True
                    for spike in spikes:
                        spike.active = True

            elif level == 8:
                if player.x > 260 and player.x < 600:
                    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        player.x_vel = 4.5
                    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        player.x_vel = -4.5
                else:
                    gravity_dir = 1

            elif level == 9:
                if player.x > 320 and player.x < 440:
                    if gravity_dir == 1:
                        gravity_dir = -1
                        player.y_vel = -3
                        particles.append(ShockwaveParticle(player.x + 15, player.y + 15, NEON_PURPLE))
                elif player.x > 480:
                    gravity_dir = 1

            elif level == 10:
                for block in blocks:
                    if block.color == NEON_GREEN:
                        player_rect = player.get_rect()
                        if player_rect.colliderect(pygame.Rect(block.rect.x, block.rect.y - 4, block.rect.width, 6)):
                            player.y_vel = -18
                            shake_duration = 15
                            shake_amount = 5
                            particles.append(ShockwaveParticle(block.rect.centerx, block.rect.y, NEON_GREEN))

            elif level == 11:
                if player.x > 180 and not trap_triggered:
                    trap_triggered = True
                    for i, spike in enumerate(spikes):
                        spike.active = True
                        spike.vy = 6.0 + i * 0.8

            elif level == 12:
                for block in blocks:
                    if block.color == NEON_GREEN:
                        player_rect = player.get_rect()
                        if player_rect.colliderect(pygame.Rect(block.rect.x, block.rect.y - 4, block.rect.width, 6)):
                            player.y_vel = -16
                            particles.append(ShockwaveParticle(block.rect.centerx, block.rect.y, NEON_GREEN))

            elif level == 13:
                if player.x > 620 and not trap_triggered:
                    trap_triggered = True
                    portal.color = NEON_PINK
                    sp = Spike(portal.rect.x + 5, portal.rect.y + 20, 30, 40, "up")
                    spikes.append(sp)
                    portal.rect.x = 40
                    portal.orig_x = 40
                    portal.is_fake = False
                    portal.color = NEON_GREEN

            elif level == 14:
                if player.x > 250 and player.x < 550:
                    player.scale = 0.35
                    player.x_vel -= 0.25
                else:
                    player.scale = 1.0

            elif level == 15:
                if player.x > 80:
                    for spike in spikes:
                        spike.active = True

            elif level == 16:
                for block in blocks:
                    if block.color == NEON_BLUE:
                        if block.rect.y < 200 or block.rect.y > 480:
                            block.vy *= -1
                        if block.rect.x < 200 or block.rect.x > 500:
                            block.vx *= -1
                        player_rect = player.get_rect()
                        if player_rect.colliderect(pygame.Rect(block.rect.x, block.rect.y - 5, block.rect.width, 7)):
                            player.x += int(block.vx)
                            player.y += int(block.vy)

            elif level == 17:
                for block in blocks:
                    if block.color == DARK_BG:
                        if player.y_vel < 0 and abs(player.x - block.rect.x) < 50:
                            block.solid = True
                            block.color = NEON_PINK
                            block.visible = True
                            particles.append(ShockwaveParticle(block.rect.centerx, block.rect.centery, NEON_PINK))

            elif level == 18:
                if key and not key.active and player.get_rect().colliderect(key.rect):
                    key.active = True
                
                for block in blocks:
                    if block.is_lava:
                        if player.x > 140:
                            block.rect.y -= 1
                            block.rect.height += 1
                        if player.get_rect().colliderect(block.rect):
                            player.alive = False
                            deaths += 1
                            shake_duration = 20
                            shake_amount = 8

            elif level == 19:
                for spike in spikes:
                    spike.active = True
                    if spike.orig_x == 300:
                        if spike.rect.x < 260 or spike.rect.x > 510:
                            spike.vx *= -1
                    else:
                        if spike.rect.x < 50 or spike.rect.x > 720:
                            spike.vx *= -1

            elif level == 20:
                if boss:
                    boss.shoot_timer += 1
                    if boss.shoot_timer % 90 == 0:
                        sp = Spike(random.randint(100, 700), 50, 20, 30, "down")
                        sp.vy = 5.0
                        sp.active = True
                        spikes.append(sp)

                    for block in blocks:
                        if block.color == NEON_GREEN and block.solid:
                            if player.get_rect().colliderect(block.rect):
                                block.solid = False
                                block.color = GRAY
                                boss.health -= 1
                                boss.nodes_destroyed += 1
                                particles.append(ShockwaveParticle(block.rect.centerx, block.rect.centery, NEON_GREEN))
                                shake_duration = 15
                                shake_amount = 6
                                
                                proj = Spike(block.rect.x, block.rect.y, 15, 15, "up", color=NEON_GREEN)
                                proj.vy = -8.0
                                proj.active = True
                                spikes.append(proj)
                                
                    if boss.health <= 0:
                        portal.color = NEON_GREEN
                        for _ in range(40):
                            particles.append(TrailParticle(boss.rect.centerx, boss.rect.centery, NEON_PINK))
                        boss = None

            player_rect = player.get_rect()
            for spike in spikes:
                if player_rect.colliderect(spike.rect):
                    if boss and spike.vy < 0 and spike.rect.colliderect(boss.rect):
                        continue
                    player.alive = False
                    deaths += 1
                    shake_duration = 20
                    shake_amount = 8
                    for _ in range(25):
                        particles.append(TrailParticle(player.x + 15, player.y + 15, NEON_PINK))
                    break

            if key and not key.active and player_rect.colliderect(key.rect):
                key = None
                portal.color = NEON_GREEN

            if portal and portal.color == NEON_GREEN and player_rect.colliderect(portal.rect):
                level += 1
                if level > max_levels:
                    game_won = True
                else:
                    blocks, spikes, portal, key, boss, spawn_pos, gravity_dir = load_level(level)
                    player.x, player.y = spawn_pos
                    player.x_vel = 0
                    player.y_vel = 0
                    player.scale = 1.0
                    trap_triggered = False
                    particles.clear()
                    shake_duration = 15
                    shake_amount = 6

        for block in blocks:
            block.draw(game_surf)
        for spike in spikes:
            spike.draw(game_surf)
        if portal:
            portal.draw(game_surf)
        if key:
            key.draw(game_surf)
        if boss:
            boss.draw(game_surf)
        player.draw(game_surf, gravity_dir)

        for p in particles:
            p.draw(game_surf)

        hud_surf = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (10, 10, 24, 180), (0, 0, WIDTH, 80))
        game_surf.blit(hud_surf, (0, 0))
        pygame.draw.line(game_surf, NEON_BLUE, (0, 80), (WIDTH, 80), 2)

        lbl_lvl = FONT_HUD.render("CORE STAGE", True, NEON_GREEN)
        lbl_lvl_val = FONT_HUD_VAL.render(f"{level}/{max_levels}" if level <= max_levels else "COMPLETE", True, WHITE)
        game_surf.blit(lbl_lvl, (25, 15))
        game_surf.blit(lbl_lvl_val, (25, 40))

        lbl_deaths = FONT_HUD.render("CORE FAILS (DEATHS)", True, NEON_PINK)
        lbl_deaths_val = FONT_HUD_VAL.render(f"{deaths}", True, WHITE)
        game_surf.blit(lbl_deaths, (WIDTH // 2 - 100, 15))
        game_surf.blit(lbl_deaths_val, (WIDTH // 2 - 100, 40))

        elapsed = int(time.time() - start_time) if not game_won else int(time.time() - start_time)
        lbl_time = FONT_HUD.render("SESSION ELAPSED", True, GOLD)
        lbl_time_val = FONT_HUD_VAL.render(f"{elapsed}s", True, WHITE)
        game_surf.blit(lbl_time, (WIDTH - 180, 15))
        game_surf.blit(lbl_time_val, (WIDTH - 180, 40))

        if not player.alive:
            draw_game_overlay(game_surf, "CORE TERMINATED", "SYSTEM TROULED. PRESS 'R' TO REBOOT CORE.", NEON_PINK)
        elif game_won:
            if not score_submitted:
                score_submitted = True
                final_score = max(100, 10000 - deaths * 250 - elapsed * 5)
                if arcade_api:
                    arcade_api.submit_score("Level Devil", final_score)
            draw_game_overlay(game_surf, "ARCADE CHAMPION", f"DEVIL DEFEATED! FINAL SCORE: {final_score}. PRESS 'R' TO REPLAY.", NEON_GREEN)

        WIN.fill((0, 0, 0))
        WIN.blit(game_surf, (offset_x, offset_y))
        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
