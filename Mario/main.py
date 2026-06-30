import os
import sys
import random
import math
import pygame
import asyncio
import time

# Import Arcade API
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
WIDTH, HEIGHT = 950, 680
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Mario Bros - Arcade Edition")
FPS = 60

# Colors (Neon Retro Arcade Palette)
DARK_BG = (6, 8, 20)
GRID_COLOR = (15, 20, 45)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
NEON_BLUE = (0, 204, 255)
NEON_PINK = (255, 0, 119)
NEON_GREEN = (0, 255, 102)
NEON_PURPLE = (180, 0, 255)
NEON_ORANGE = (255, 120, 0)
LAVA_RED = (255, 30, 0)

# Fonts
try:
    FONT_HUD = pygame.font.SysFont("Outfit", 20, bold=True)
    FONT_HUD_VAL = pygame.font.SysFont("Outfit", 24, bold=True)
    FONT_OVERLAY = pygame.font.SysFont("Outfit", 50, bold=True)
    FONT_OVERLAY_SUB = pygame.font.SysFont("Outfit", 20, bold=True)
except:
    try:
        FONT_HUD = pygame.font.SysFont("Segoe UI", 20, bold=True)
        FONT_HUD_VAL = pygame.font.SysFont("Segoe UI", 24, bold=True)
        FONT_OVERLAY = pygame.font.SysFont("Segoe UI", 50, bold=True)
        FONT_OVERLAY_SUB = pygame.font.SysFont("Segoe UI", 20, bold=True)
    except:
        FONT_HUD = pygame.font.Font(None, 20)
        FONT_HUD_VAL = pygame.font.Font(None, 24)
        FONT_OVERLAY = pygame.font.Font(None, 50)
        FONT_OVERLAY_SUB = pygame.font.Font(None, 20)

# -----------------------------------------------------------------------------
# Sprite Generation & Pixel Art Matrices
# -----------------------------------------------------------------------------
def create_pixel_art(matrix, scale=2.5):
    h = len(matrix)
    w = len(matrix[0])
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    
    color_map = {
        '.': None,
        'R': (255, 0, 100),      # Neon Red/Pink
        'B': (0, 150, 255),      # Neon Blue
        'S': (255, 195, 150),     # Skin
        'W': (255, 255, 255),     # White
        'K': (15, 15, 28),        # Dark Navy/Black
        'O': (255, 120, 0),       # Neon Orange
        'Y': (255, 215, 0),       # Gold/Yellow
        'G': (0, 255, 100),       # Neon Green
        'P': (180, 0, 255),       # Neon Purple
        'M': (130, 60, 10),       # Brown
        'D': (60, 60, 80),        # Gray
        'L': (180, 180, 200),     # Light Gray
    }
    
    for r in range(h):
        for c in range(w):
            char = matrix[r][c]
            color = color_map.get(char)
            if color:
                pygame.draw.rect(surf, color, (c * scale, r * scale, scale, scale))
                
    return surf

def recolor_surface(surf, color_changes):
    new_surf = surf.copy()
    for x in range(new_surf.get_width()):
        for y in range(new_surf.get_height()):
            color = new_surf.get_at((x, y))
            if color.a > 0:
                rgb = (color.r, color.g, color.b)
                if rgb in color_changes:
                    new_c = color_changes[rgb]
                    new_surf.set_at((x, y), pygame.Color(new_c[0], new_c[1], new_c[2], color.a))
    return new_surf

# Small Mario Matrices (13x16)
MARIO_S_IDLE = [
    "....RRRRR....",
    "...RRRRRRRRR.",
    "...MMMSSKSS..",
    "..MMSMSMSSSS.",
    "..MMSMMSKSSS.",
    "..MMSKSSSS...",
    "....SSSSSS...",
    "...RRBBRRBR..",
    "..RRRBRRBRRR.",
    ".RRRRBBBBRRRR",
    ".SSBBYBBYBSS.",
    ".SSSBBBBBBB..",
    "..SSBBBBBBB..",
    "...BBB...BBB.",
    "..MMM.....MMM",
    ".MMMM.....MMMM"
]

MARIO_S_WALK = [
    "....RRRRR....",
    "...RRRRRRRRR.",
    "...MMMSSKSS..",
    "..MMSMSMSSSS.",
    "..MMSMMSKSSS.",
    "..MMSKSSSS...",
    "....SSSSSS...",
    "...RBBBRRBR..",
    "..RRBBRRBRRR.",
    ".RRRRBBBBRRR.",
    ".SSBBYBBYBSS.",
    ".SSSBBBBBBB..",
    "..SSBBBBBBB..",
    "...BBBBBBBB..",
    "...MMM..MMM..",
    "..MMM....MMM."
]

MARIO_S_JUMP = [
    "....RRRRR....",
    "...RRRRRRRRR.",
    "...MMMSSKSS..",
    "..MMSMSMSSSS.",
    "..MMSMMSKSSS.",
    "..MMSKSSSS...",
    "....SSSSSS...",
    "...RRBBRRBR..",
    "..RRRBRRBRRR.",
    ".RRRRBBBBRRRR",
    ".SSBBYBBYBSS.",
    ".SSSBBBBBBB..",
    "..SSBBBBBBB..",
    "..BBBB...BBB.",
    ".MMM......MMM",
    "MMMM......MMMM"
]

# Big Mario Matrices (15x32)
MARIO_B_IDLE = [
    ".....RRRRRR.....",
    "....RRRRRRRRRR..",
    "....MMMSSKSS....",
    "...MMSMSMSSSS...",
    "...MMSMMSKSSS...",
    "...MMSKSSSSSS...",
    ".....SSSSSSS....",
    "....RRRBBBRRR...",
    "...RRRRBBBRRRR..",
    "..RRRRRBBBRRRRR.",
    "..SSBBYBBYBBYSS.",
    "..SSSBBBBBBBBSS.",
    "..SSSBBBBBBBBSS.",
    "...SSBBBBBBBB...",
    "....BBBBBBBBBB..",
    "....BBBB..BBBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "...BBBB....BBBB.",
    "...BBBB....BBBB.",
    "...BBBB....BBBB.",
    "..MMMMM....MMMMM",
    ".MMMMMM....MMMMMM",
    ".MMMMMM....MMMMMM",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................"
]

MARIO_B_WALK = [
    ".....RRRRRR.....",
    "....RRRRRRRRRR..",
    "....MMMSSKSS....",
    "...MMSMSMSSSS...",
    "...MMSMMSKSSS...",
    "...MMSKSSSSSS...",
    ".....SSSSSSS....",
    "....RRRBBBRRR...",
    "...RRRBBRRBRRR..",
    "..RRRRBBBBRRRR..",
    "..SSBBYBBYBBYSS.",
    "..SSSBBBBBBBBSS.",
    "..SSSBBBBBBBBSS.",
    "...SSBBBBBBBB...",
    "....BBBBBBBBBB..",
    "....BBBB..BBBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "...BBBB....BBBB.",
    "...BBBB....BBBB.",
    "...BBBB....BBBB.",
    "..MMMMM....MMMMM",
    ".MMMMMM....MMMMMM",
    ".MMMMMM....MMMMMM",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................"
]

MARIO_B_JUMP = [
    ".....RRRRRR.....",
    "....RRRRRRRRRR..",
    "....MMMSSKSS....",
    "...MMSMSMSSSS...",
    "...MMSMMSKSSS...",
    "...MMSKSSSSSS...",
    ".....SSSSSSS....",
    "....RRRBBBRRR...",
    "...RRRRBBBRRRR..",
    "..RRRRRBBBRRRRR.",
    "..SSBBYBBYBBYSS.",
    "..SSSBBBBBBBBSS.",
    "..SSSBBBBBBBBSS.",
    "...SSBBBBBBBB...",
    "....BBBBBBBBBB..",
    "....BBBB..BBBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "...BBBB....BBBB.",
    "..MMMMM....MMMMM",
    ".MMMMMM....MMMMMM",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................"
]

GOOMBA_MAT = [
    "......MMMM......",
    "....MMMMMMMM....",
    "...MMMMMMMMMM...",
    "..MMKKMMMMKKMM..",
    "..MKKKKMMKKKKM..",
    ".MMKKKKMMKKKKMM.",
    ".MMSKSSMMSMSSMM.",
    "MMSSSSSSSSSSSSMM",
    "MMSMMSMMSMMSMMSS",
    "MMMMMMMMMMMMMMMM",
    "....DDDDDDDD....",
    "...DDDDDDDDDD...",
    "..DDD......DDD..",
    "..DD........DD..",
    ".DDD........DDD.",
    ".DD..........DD."
]

KOOPA_MAT = [
    ".....GGGGGG.....",
    "....GGGGGGGG....",
    "...GGGGGGGGGG...",
    "..GGYYGGGGYYGG..",
    "..GYYYYGGYYYYG..",
    ".GGYYYYGGYYYYGG.",
    "..GGYSYGGYSYGG..",
    "GGYYYYYYYYYYYYGG",
    "GGYGGYGGYGGYGGYY",
    "GGGGGGGGGGGGGGGG",
    "....YYYYYYYY....",
    "...YYYYYYYYYY...",
    "..YYY......YYY..",
    "..YY........YY..",
    ".YYY........YYY.",
    ".YY..........YY.",
    "..YY........YY..",
    "...YY......YY...",
    "....YYYYYYYY....",
    ".....YYYYYY.....",
    "......YYYY......"
]

MUSHROOM_MAT = [
    "....RRRRRRRR....",
    "..RRRWRRRRWRRR..",
    ".RRRWRRRRWRRRRR.",
    ".RRRRRRRRRRRRRR.",
    "RRRWRRRRWRRRWRRR",
    "RRRWRRRRWRRRWRRR",
    "RRRRRRRRRRRRRRRR",
    "RRRRRRRRRRRRRRRR",
    "....WWWWWWWW....",
    "...WWKWWWWKWW...",
    "...WWKWWWWKWW...",
    "...WWWWWWWWWW...",
    "....WWWWWWWW....",
    ".....WWWWWW....."
]

FLOWER_MAT = [
    "....YYYYYYYY....",
    "..YYYYRRYYYYYY..",
    ".YYYYRRRRYYYYYY.",
    ".YYYRRWWRRYYYYY.",
    "YYYRRWWWWWRRYYYY",
    "YYYRRWWWWWRRYYYY",
    ".YYYRRWWRRYYYYY.",
    ".YYYYRRRRYYYYYY.",
    "..YYYYRRYYYYYY..",
    "....YYYYYYYY....",
    "......GGGG......",
    "....GGGGGGGG....",
    "......GGGG......",
    "......GGGG......"
]

BOWSER_MAT = [
    "........GGGGGGGGGGGG........",
    "......GGGGGGGGGGGGGGGG......",
    "....GGGGGGWWGGGGWWGGGGGG....",
    "...GGGGGGWWWWGGWWWWGGGGGG...",
    "..GGGGGGWWWWWWWWWWWWGGGGGG..",
    "..GGGGGGWKKWWWWWWKKWGGGGGG..",
    ".GGGGGGGWKKWWWWWWKKWGGGGGGGG.",
    ".GGGGGGWWWWWWWWWWWWWWGGGGGGG.",
    "GGGGGGWWYYYYYYYYYYYYWWGGGGGGG",
    "GGGGGWWYYYYYYYYYYYYYYWWGGGGGG",
    "GGGGWWYYYYKKYYYYKKYYYYWWGGGGG",
    "GGGWWYYYYYKKYYYYKKYYYYYWWGGGG",
    "GGWWYYYYYYYYYYYYYYYYYYYYWWGGG",
    "GWWYYYYYYYYYYYYYYYYYYYYYYWWGG",
    "GWWYYYYYYYYYYYYYYYYYYYYYYWWGG",
    "WWYYYYYYYYYYYYYYYYYYYYYYYYWWG",
    "WWYYYYYKKKKKKKKKKKKKKYYYYYWWG",
    "WYYYYYYKRRRRRRRRRRRRKYYYYYYWG",
    "WYYYYYYKRRRRRRRRRRRRKYYYYYYWG",
    "WYYYYYYKRRRRRRRRRRRRKYYYYYYWG",
    "WYYYYYYKKKKKKKKKKKKKKYYYYYYWG",
    ".WYYYYYYYYYYYYYYYYYYYYYYYYW.",
    "..WYYYYYYYYYYYYYYYYYYYYYYW..",
    "...WWYYYYYYYYYYYYYYYYYYWW...",
    "....WWWYYYYYYYYYYYYYYWWW....",
    "......WWWWYYYYYYYYWWWW......",
    "........WWWWWWWWWWWW........"
]

# Cache Sprites
SPRITES = {}

def init_sprites():
    # Small Mario
    s_idle = create_pixel_art(MARIO_S_IDLE)
    s_walk = create_pixel_art(MARIO_S_WALK)
    s_jump = create_pixel_art(MARIO_S_JUMP)
    
    SPRITES['mario_s_idle_r'] = s_idle
    SPRITES['mario_s_idle_l'] = pygame.transform.flip(s_idle, True, False)
    SPRITES['mario_s_walk_r'] = s_walk
    SPRITES['mario_s_walk_l'] = pygame.transform.flip(s_walk, True, False)
    SPRITES['mario_s_jump_r'] = s_jump
    SPRITES['mario_s_jump_l'] = pygame.transform.flip(s_jump, True, False)
    
    # Big Mario
    b_idle = create_pixel_art(MARIO_B_IDLE)
    b_walk = create_pixel_art(MARIO_B_WALK)
    b_jump = create_pixel_art(MARIO_B_JUMP)
    
    SPRITES['mario_b_idle_r'] = b_idle
    SPRITES['mario_b_idle_l'] = pygame.transform.flip(b_idle, True, False)
    SPRITES['mario_b_walk_r'] = b_walk
    SPRITES['mario_b_walk_l'] = pygame.transform.flip(b_walk, True, False)
    SPRITES['mario_b_jump_r'] = b_jump
    SPRITES['mario_b_jump_l'] = pygame.transform.flip(b_jump, True, False)
    
    # Fire Mario (Recolor Big Mario: Red -> White, Blue -> Red)
    fire_recolors = {
        (255, 0, 100): (255, 255, 255),  # Red to White
        (0, 150, 255): (255, 0, 100)     # Blue to Red
    }
    f_idle = recolor_surface(b_idle, fire_recolors)
    f_walk = recolor_surface(b_walk, fire_recolors)
    f_jump = recolor_surface(b_jump, fire_recolors)
    
    SPRITES['mario_f_idle_r'] = f_idle
    SPRITES['mario_f_idle_l'] = pygame.transform.flip(f_idle, True, False)
    SPRITES['mario_f_walk_r'] = f_walk
    SPRITES['mario_f_walk_l'] = pygame.transform.flip(f_walk, True, False)
    SPRITES['mario_f_jump_r'] = f_jump
    SPRITES['mario_f_jump_l'] = pygame.transform.flip(f_jump, True, False)
    
    # Enemies & Powerups
    SPRITES['goomba'] = create_pixel_art(GOOMBA_WALK1 if 'GOOMBA_WALK1' in globals() else GOOMBA_MAT)
    SPRITES['koopa'] = create_pixel_art(KOOPA_MAT)
    SPRITES['mushroom'] = create_pixel_art(MUSHROOM_MAT)
    SPRITES['flower'] = create_pixel_art(FLOWER_MAT)
    
    # Bowser
    bowser = create_pixel_art(BOWSER_MAT, scale=3.5)
    SPRITES['bowser_l'] = bowser
    SPRITES['bowser_r'] = pygame.transform.flip(bowser, True, False)

# -----------------------------------------------------------------------------
# Particle Classes
# -----------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25  # Gravity
        self.life -= 1

    def draw(self, surf, offset_x):
        if self.life <= 0: return
        alpha = int((self.life / self.max_life) * 255)
        # Create a tiny surface for alpha blending
        p_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(p_surf, (self.x - offset_x - self.size, self.y - self.size))

class TextParticle:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.vy = -1.5
        self.life = 45

    def update(self):
        self.y += self.vy
        self.life -= 1

    def draw(self, surf, offset_x):
        if self.life <= 0: return
        # Simple text rendering
        txt_surf = FONT_HUD.render(self.text, True, self.color)
        surf.blit(txt_surf, (self.x - offset_x - txt_surf.get_width() // 2, self.y))

# -----------------------------------------------------------------------------
# Game Entities
# -----------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.x = 150
        self.y = 500
        self.vx = 0
        self.vy = 0
        self.width = 30
        self.height = 40
        self.state = "small"  # "small", "big", "fire"
        self.on_ground = False
        self.facing_right = True
        self.is_walking = False
        self.walk_frame = 0
        
        self.invincibility_timer = 0
        self.death_timer = 0
        
        # Stats
        self.lives = 3
        self.coins = 0
        self.score = 0
        
    def get_rect(self):
        h = 40 if self.state == "small" else 72
        w = 30
        return pygame.Rect(self.x, self.y + (40 - h if self.state == "small" else 0), w, h)

    def jump(self):
        if self.on_ground:
            self.vy = -15
            self.on_ground = False

    def shoot_fireball(self, fireballs):
        if self.state == "fire":
            # Max 2 fireballs on screen
            if len(fireballs) < 3:
                fx = self.x + (30 if self.facing_right else -10)
                fy = self.y + (20 if self.state == "small" else 30)
                fvx = 8 if self.facing_right else -8
                fireballs.append(Fireball(fx, fy, fvx))

    def take_damage(self, particles):
        if self.invincibility_timer > 0:
            return
        
        if self.state == "fire":
            self.state = "big"
            self.invincibility_timer = 90
            # Burst of defense sparks
            for _ in range(15):
                particles.append(Particle(self.x + 15, self.y + 20, random.uniform(-4, 4), random.uniform(-4, 4), NEON_BLUE, 4, 30))
        elif self.state == "big":
            self.state = "small"
            self.invincibility_timer = 90
            # Burst of defense sparks
            for _ in range(15):
                particles.append(Particle(self.x + 15, self.y + 20, random.uniform(-4, 4), random.uniform(-4, 4), NEON_PINK, 4, 30))
        else:
            # Die
            self.die()

    def die(self):
        self.death_timer = 120
        self.vy = -10
        self.lives -= 1

    def update(self):
        if self.death_timer > 0:
            self.y += self.vy
            self.vy += 0.4  # Gravity
            self.death_timer -= 1
            return

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # Physics
        self.y += self.vy
        self.vy += 0.65  # Gravity
        
        self.x += self.vx
        self.vx *= 0.85  # Friction
        
        if abs(self.vx) < 0.2:
            self.vx = 0
            self.is_walking = False
        else:
            self.is_walking = True
            self.walk_frame += 1

    def draw(self, surf, offset_x):
        # Flicker if invincible
        if self.invincibility_timer > 0 and (self.invincibility_timer // 4) % 2 == 0:
            return
            
        rect = self.get_rect()
        m_type = 's' if self.state == 'small' else ('f' if self.state == 'fire' else 'b')
        
        # Decide action frame
        action = 'idle'
        if not self.on_ground:
            action = 'jump'
        elif self.is_walking:
            action = 'walk' if (self.walk_frame // 6) % 2 == 0 else 'idle'
            
        sprite_key = f"mario_{m_type}_{action}_{'r' if self.facing_right else 'l'}"
        sprite = SPRITES.get(sprite_key)
        
        if sprite:
            surf.blit(sprite, (rect.x - 2, rect.y))
        else:
            # Fallback
            color = NEON_PINK if self.state == "small" else (NEON_BLUE if self.state == "big" else NEON_GREEN)
            pygame.draw.rect(surf, color, (rect.x - offset_x, rect.y, rect.width, rect.height))

class Tile:
    def __init__(self, x, y, t_type, theme, height=80):
        self.x = x
        self.y = y
        self.type = t_type  # "ground", "brick", "question", "pipe", "bridge", "lava", "empty_block"
        self.theme = theme
        self.width = 40
        self.height = height if t_type == "pipe" else 40
        self.hit_offset_y = 0
        self.hit_cooldown = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def trigger_hit(self, player, powerups, particles):
        if self.hit_cooldown > 0: return
        
        if self.type == "brick":
            self.hit_offset_y = -10
            self.hit_cooldown = 10
            if player.state != "small":
                # Shatter brick!
                self.type = "shattered"
                # Spawn block particles
                for _ in range(8):
                    particles.append(Particle(self.x + 20, self.y + 20, random.uniform(-3, 3), random.uniform(-6, -2), NEON_PURPLE, 5, 25))
                player.score += 50
            else:
                # Small Mario just bumps it
                pass
                
        elif self.type == "question":
            self.hit_offset_y = -10
            self.hit_cooldown = 10
            self.type = "empty_block"
            
            # Spawn coin or powerup
            player.score += 100
            if random.random() < 0.6:
                # Spawn Coin floating up
                player.coins += 1
                particles.append(TextParticle(self.x + 20, self.y - 20, "+100", GOLD))
                for _ in range(6):
                    particles.append(Particle(self.x + 20, self.y - 20, random.uniform(-2, 2), random.uniform(-5, -2), GOLD, 3, 20))
            else:
                # Spawn Mushroom or Flower
                p_type = "mushroom" if player.state == "small" else "flower"
                powerups.append(PowerUp(self.x, self.y, p_type))
                particles.append(TextParticle(self.x + 20, self.y - 40, p_type.upper(), NEON_GREEN))

    def update(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
            if self.hit_cooldown == 5:
                self.hit_offset_y = 0

    def draw(self, surf, offset_x):
        if self.type == "shattered": return
        
        rect = self.get_rect()
        rx = rect.x - offset_x
        ry = rect.y + self.hit_offset_y
        
        # Glow styling based on theme
        neon_color = NEON_BLUE
        if self.theme == "cave": neon_color = NEON_PURPLE
        elif self.theme == "desert": neon_color = NEON_ORANGE
        elif self.theme == "ice": neon_color = WHITE
        elif self.theme == "castle": neon_color = LAVA_RED
        
        if self.type == "ground":
            pygame.draw.rect(surf, GRID_COLOR, (rx, ry, self.width, self.height))
            pygame.draw.rect(surf, neon_color, (rx, ry, self.width, self.height), 2)
            # Add a grid cross inside
            pygame.draw.line(surf, GRID_COLOR, (rx, ry), (rx + self.width, ry + self.height))
            
        elif self.type == "brick":
            pygame.draw.rect(surf, (35, 10, 45), (rx, ry, self.width, self.height))
            pygame.draw.rect(surf, NEON_PINK, (rx, ry, self.width, self.height), 2)
            # Brick pattern lines
            pygame.draw.line(surf, NEON_PINK, (rx, ry + 20), (rx + self.width, ry + 20), 1)
            pygame.draw.line(surf, NEON_PINK, (rx + 20, ry), (rx + 20, ry + 20), 1)
            pygame.draw.line(surf, NEON_PINK, (rx + 10, ry + 20), (rx + 10, ry + 40), 1)
            pygame.draw.line(surf, NEON_PINK, (rx + 30, ry + 20), (rx + 30, ry + 40), 1)
            
        elif self.type == "question":
            # Pulsing gold block
            pulse = int(abs(math.sin(time.time() * 5)) * 40)
            color = (200 + pulse, 160 + pulse // 2, 0)
            pygame.draw.rect(surf, color, (rx, ry, self.width, self.height))
            pygame.draw.rect(surf, GOLD, (rx, ry, self.width, self.height), 3)
            # Draw "?"
            q_txt = FONT_HUD_VAL.render("?", True, WHITE)
            surf.blit(q_txt, (rx + 20 - q_txt.get_width() // 2, ry + 20 - q_txt.get_height() // 2))
            
        elif self.type == "empty_block":
            pygame.draw.rect(surf, (20, 25, 35), (rx, ry, self.width, self.height))
            pygame.draw.rect(surf, (80, 80, 100), (rx, ry, self.width, self.height), 2)
            pygame.draw.circle(surf, (80, 80, 100), (rx + 8, ry + 8), 2)
            pygame.draw.circle(surf, (80, 80, 100), (rx + 32, ry + 8), 2)
            pygame.draw.circle(surf, (80, 80, 100), (rx + 8, ry + 32), 2)
            pygame.draw.circle(surf, (80, 80, 100), (rx + 32, ry + 32), 2)
            
        elif self.type == "pipe":
            # Vertical Pipe
            pygame.draw.rect(surf, (0, 40, 15), (rx, ry, self.width, self.height))
            pygame.draw.rect(surf, NEON_GREEN, (rx, ry, self.width, self.height), 2)
            # Flange cap
            pygame.draw.rect(surf, (0, 60, 20), (rx - 4, ry, self.width + 8, 25))
            pygame.draw.rect(surf, NEON_GREEN, (rx - 4, ry, self.width + 8, 25), 2)
            
        elif self.type == "bridge":
            # Castle bridge
            pygame.draw.rect(surf, (80, 50, 30), (rx, ry, self.width, 15))
            pygame.draw.rect(surf, GOLD, (rx, ry, self.width, 15), 2)
            pygame.draw.line(surf, GOLD, (rx + 20, ry + 15), (rx + 20, ry + 40), 2)
            
        elif self.type == "lava":
            # Bubbling Lava
            pulse = int(abs(math.sin(time.time() * 3 + rx * 0.05)) * 10)
            pygame.draw.rect(surf, (150 + pulse * 5, 20, 0), (rx, ry + pulse, self.width, self.height - pulse))
            pygame.draw.line(surf, LAVA_RED, (rx, ry + pulse), (rx + self.width, ry + pulse), 2)

class PowerUp:
    def __init__(self, x, y, p_type):
        self.x = x + 4
        self.y = y
        self.type = p_type  # "mushroom", "flower"
        self.vx = 2
        self.vy = -3  # Bounce out of block
        self.width = 32
        self.height = 32
        self.spawn_timer = 20  # Slowly rise up

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, tiles):
        if self.spawn_timer > 0:
            self.y -= 1.5
            self.spawn_timer -= 1
            return

        # Gravity & horizontal movement
        self.vy += 0.5
        self.y += self.vy
        
        # Check vertical collisions
        rect = self.get_rect()
        for tile in tiles:
            if tile.type == "shattered" or tile.type == "lava": continue
            t_rect = tile.get_rect()
            if rect.colliderect(t_rect):
                if self.vy > 0:
                    self.y = t_rect.top - self.height
                    self.vy = 0
                    
        self.x += self.vx
        
        # Check horizontal collisions
        rect = self.get_rect()
        for tile in tiles:
            if tile.type == "shattered" or tile.type == "lava": continue
            t_rect = tile.get_rect()
            if rect.colliderect(t_rect):
                self.vx *= -1
                if self.vx > 0:
                    self.x = t_rect.right
                else:
                    self.x = t_rect.left - self.width

    def draw(self, surf, offset_x):
        rect = self.get_rect()
        sprite = SPRITES.get(self.type)
        if sprite:
            surf.blit(sprite, (rect.x - offset_x, rect.y))
        else:
            color = GOLD if self.type == "mushroom" else NEON_GREEN
            pygame.draw.ellipse(surf, color, (rect.x - offset_x, rect.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, e_type):
        self.x = x
        self.y = y
        self.type = e_type  # "goomba", "koopa", "koopa_shell", "piranha"
        self.vx = -1.5
        self.vy = 0
        self.width = 32
        self.height = 32 if e_type != "koopa" else 48
        self.is_dead = False
        self.dead_timer = 0
        self.anim_timer = 0

    def get_rect(self):
        h = 32 if self.type in ["goomba", "koopa_shell"] else 48
        return pygame.Rect(self.x, self.y, self.width, h)

    def update(self, tiles):
        if self.is_dead:
            if self.type == "goomba":
                self.dead_timer -= 1
            else:
                # Falling dead shell/etc
                self.y += self.vy
                self.vy += 0.5
                self.dead_timer -= 1
            return

        self.anim_timer += 1

        # Piranha Plant behavior
        if self.type == "piranha":
            # Move up and down cyclically
            cycle = (self.anim_timer // 2) % 180
            if cycle < 40:
                self.y -= 1  # Rise
            elif cycle >= 90 and cycle < 130:
                self.y += 1  # Hide
            return

        # Gravity & horizontal movement
        self.vy += 0.5
        self.y += self.vy
        
        # Vertical collisions
        rect = self.get_rect()
        for tile in tiles:
            if tile.type in ["shattered", "lava", "bridge"]: continue
            t_rect = tile.get_rect()
            if rect.colliderect(t_rect):
                if self.vy > 0:
                    self.y = t_rect.top - rect.height
                    self.vy = 0

        self.x += self.vx
        
        # Horizontal collisions
        rect = self.get_rect()
        for tile in tiles:
            if tile.type in ["shattered", "lava", "bridge"]: continue
            t_rect = tile.get_rect()
            if rect.colliderect(t_rect):
                self.vx *= -1
                if self.vx > 0:
                    self.x = t_rect.right
                else:
                    self.x = t_rect.left - rect.width

    def stomped(self, player, particles):
        self.is_dead = True
        player.score += 200
        particles.append(TextParticle(self.x + 16, self.y, "+200", NEON_GREEN))
        
        if self.type == "goomba":
            self.dead_timer = 30  # Stay squished
            self.vx = 0
            self.vy = 0
        elif self.type == "koopa":
            # Turns into a shell
            self.type = "koopa_shell"
            self.height = 32
            self.is_dead = False
            self.vx = 0
        elif self.type == "koopa_shell":
            # Kick it
            self.is_dead = False
            self.vx = 8 if player.x < self.x else -8

    def draw(self, surf, offset_x):
        rect = self.get_rect()
        rx = rect.x - offset_x
        ry = rect.y
        
        if self.is_dead and self.type == "goomba":
            # Draw squished Goomba
            sq_goomba = pygame.transform.scale(SPRITES['goomba'], (32, 12))
            surf.blit(sq_goomba, (rx, ry + 20))
            return
            
        sprite = None
        if self.type == "goomba":
            sprite = SPRITES.get('goomba')
        elif self.type == "koopa":
            sprite = SPRITES.get('koopa')
            if self.vx > 0:
                sprite = pygame.transform.flip(sprite, True, False)
        elif self.type == "koopa_shell":
            # Drawn as scaled Koopa or shell
            shell_mat = [
                ".....GGGGGG.....",
                "....GGGGGGGG....",
                "...GGKKGGKKGG...",
                "..GGKKKKKKKKGG..",
                "..GKKKKKKKKKKG..",
                ".GGKKKKKKKKKKGG.",
                "GGKKKKKKKKKKKKGG",
                "GGGGGGGGGGGGGGGG",
                "....YYYYYYYY...."
            ]
            sprite = create_pixel_art(shell_mat, scale=2.2)
            
        if sprite:
            surf.blit(sprite, (rx, ry))
        else:
            # Fallback shapes
            color = NEON_ORANGE if self.type == "goomba" else NEON_GREEN
            pygame.draw.rect(surf, color, (rx, ry, rect.width, rect.height))

class PiranhaPlant(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "piranha")
        self.width = 24
        self.height = 32
        self.vx = 0

    def draw(self, surf, offset_x):
        rx = self.x - offset_x
        # Draw neon green stem, red head with white spots
        pygame.draw.rect(surf, NEON_GREEN, (rx + 8, self.y + 16, 8, 16))
        pygame.draw.ellipse(surf, NEON_PINK, (rx, self.y, 24, 18))
        pygame.draw.rect(surf, WHITE, (rx + 4, self.y + 6, 16, 4)) # teeth

class Fireball:
    def __init__(self, x, y, vx):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = 2
        self.width = 12
        self.height = 12
        self.life = 180

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, tiles):
        self.vy += 0.5  # Gravity
        self.y += self.vy
        
        # Bouncing physics
        rect = self.get_rect()
        for tile in tiles:
            if tile.type in ["shattered", "lava", "bridge"]: continue
            t_rect = tile.get_rect()
            if rect.colliderect(t_rect):
                if self.vy > 0:
                    self.y = t_rect.top - self.height
                    self.vy = -6  # Bounce up!
                    
        self.x += self.vx
        self.life -= 1
        
        # Check wall collision
        rect = self.get_rect()
        for tile in tiles:
            if tile.type in ["shattered", "lava", "bridge"]: continue
            t_rect = tile.get_rect()
            if rect.colliderect(t_rect):
                self.life = 0  # Explode

    def draw(self, surf, offset_x):
        rx = self.x - offset_x
        # Pulsing fireball
        pulse = int(abs(math.sin(time.time() * 10)) * 5)
        pygame.draw.circle(surf, (255, 100 + pulse * 10, 0), (int(rx + 6), int(self.y + 6)), 6)
        pygame.draw.circle(surf, GOLD, (int(rx + 6), int(self.y + 6)), 3)

class Bowser(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "bowser")
        self.width = 96
        self.height = 96
        self.vx = -1
        self.vy = 0
        self.hp = 5
        self.action_timer = 0

    def update(self, tiles, boss_fireballs):
        self.action_timer += 1
        
        # Gravity & movement
        self.vy += 0.5
        self.y += self.vy
        
        # Collide with ground
        rect = self.get_rect()
        for tile in tiles:
            if tile.type == "ground":
                t_rect = tile.get_rect()
                if rect.colliderect(t_rect):
                    if self.vy > 0:
                        self.y = t_rect.top - self.height
                        self.vy = 0

        self.x += self.vx
        
        # Keep within bridge boundaries
        if self.x < 950 * 20 - 580:
            self.vx = 1
        elif self.x > 950 * 20 - 350:
            self.vx = -1

        # Boss actions
        if self.action_timer % 120 == 0:
            # Jump
            if self.vy == 0:
                self.vy = -10
        if self.action_timer % 150 == 0:
            # Breathe fire
            boss_fireballs.append(BossFireball(self.x, self.y + 30, -5))

    def draw(self, surf, offset_x):
        rect = self.get_rect()
        rx = rect.x - offset_x
        
        sprite = SPRITES.get('bowser_l' if self.vx < 0 else 'bowser_r')
        if sprite:
            surf.blit(sprite, (rx, rect.y))
        else:
            pygame.draw.rect(surf, NEON_GREEN, (rx, rect.y, self.width, self.height))
            pygame.draw.rect(surf, LAVA_RED, (rx + 10, rect.y + 10, self.width - 20, self.height - 20))

class BossFireball:
    def __init__(self, x, y, vx):
        self.x = x
        self.y = y
        self.vx = vx
        self.width = 30
        self.height = 18
        self.life = 200

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x += self.vx
        self.life -= 1

    def draw(self, surf, offset_x):
        rx = self.x - offset_x
        pulse = int(abs(math.sin(time.time() * 8)) * 8)
        # Large oval fire
        pygame.draw.ellipse(surf, (255, 50, 0), (rx, self.y - pulse // 2, self.width, self.height + pulse))
        pygame.draw.ellipse(surf, GOLD, (rx + 6, self.y + 2, self.width - 12, self.height - 4))

class Flagpole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 400
        self.type = "flagpole"

    def update(self):
        pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf, offset_x):
        rx = self.x - offset_x
        # Draw neon flagpole
        pygame.draw.rect(surf, WHITE, (rx, self.y, self.width, self.height))
        pygame.draw.circle(surf, GOLD, (rx + 8, self.y), 12)
        # Draw a little green neon flag
        pulse = int(abs(math.sin(time.time() * 2)) * 5)
        pygame.draw.polygon(surf, NEON_GREEN, [
            (rx - 40, self.y + 40),
            (rx, self.y + 20),
            (rx, self.y + 60)
        ])

class Castle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 160
        self.type = "castle"

    def update(self):
        pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf, offset_x):
        rx = self.x - offset_x
        # Cyber Castle
        pygame.draw.rect(surf, (10, 12, 25), (rx, self.y, self.width, self.height))
        pygame.draw.rect(surf, NEON_BLUE, (rx, self.y, self.width, self.height), 3)
        # Crenellations
        for i in range(4):
            bx = rx + i * 30
            pygame.draw.rect(surf, (10, 12, 25), (bx, self.y - 20, 20, 20))
            pygame.draw.rect(surf, NEON_BLUE, (bx, self.y - 20, 20, 20), 2)
        # Door
        pygame.draw.rect(surf, DARK_BG, (rx + 45, self.y + 100, 30, 60))
        pygame.draw.rect(surf, NEON_PINK, (rx + 45, self.y + 100, 30, 60), 2)

class AxeButton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.triggered = False
        self.type = "axe_button"

    def update(self):
        pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf, offset_x):
        rx = self.x - offset_x
        # Draw glowing gold axe on a stand
        pygame.draw.line(surf, WHITE, (rx + 15, self.y), (rx + 15, self.y + 40), 2)
        pygame.draw.circle(surf, GOLD, (rx + 15, self.y + 10), 10)
        pygame.draw.polygon(surf, GOLD, [
            (rx + 5, self.y + 10),
            (rx + 15, self.y),
            (rx + 25, self.y + 10),
            (rx + 15, self.y + 20)
        ])

# -----------------------------------------------------------------------------
# Level Generation
# -----------------------------------------------------------------------------
def generate_level(level_num):
    random.seed(level_num * 54321)  # Seed for reproducible procedural levels
    
    level_width = 3000 + level_num * 400
    ground_y = 600
    
    tiles = []
    enemies = []
    
    # Themes
    theme = "grass"
    if level_num in [2, 7, 12, 17]:
        theme = "cave"
    elif level_num in [3, 8, 13, 18]:
        theme = "desert"
    elif level_num in [4, 9, 14, 19]:
        theme = "ice"
    elif level_num in [5, 10, 15]:
        theme = "sky"
    elif level_num in [6, 11, 16, 20]:
        theme = "castle"
        
    # Generate terrain
    x = 0
    while x < level_width - 400:
        if x < 400:
            # Safe start
            for tx in range(x, x + 80, 40):
                tiles.append(Tile(tx, ground_y, "ground", theme))
                tiles.append(Tile(tx, ground_y + 40, "ground", theme))
            x += 80
            continue
            
        # Pits / Gaps
        if random.random() < 0.18 and theme != "sky":
            gap_size = random.choice([80, 120])
            if theme == "castle":
                # Fill pit with bubbling lava
                for lx in range(x, x + gap_size, 40):
                    tiles.append(Tile(lx, ground_y + 10, "lava", theme))
            x += gap_size
            continue
            
        segment_width = random.choice([160, 240, 320, 400])
        
        # High structures/staircases
        if random.random() < 0.25:
            stair_height = random.choice([2, 3, 4])
            for i in range(stair_height):
                sh_x = x + i * 40
                for j in range(i + 1):
                    tiles.append(Tile(sh_x, ground_y - (j + 1) * 40, "ground", theme))
            x += stair_height * 40
            continue

        for tx in range(x, x + segment_width, 40):
            tiles.append(Tile(tx, ground_y, "ground", theme))
            tiles.append(Tile(tx, ground_y + 40, "ground", theme))
            
        # Pipes
        if random.random() < 0.2 and segment_width >= 240:
            pipe_h = random.choice([80, 120])
            px = x + 80
            tiles.append(Tile(px, ground_y - pipe_h, "pipe", theme, height=pipe_h))
            if random.random() < 0.6:
                enemies.append(PiranhaPlant(px + 8, ground_y - pipe_h))
                
        # Bricks and Question Blocks
        if random.random() < 0.5:
            block_y = ground_y - random.choice([160, 220])
            blocks_num = random.choice([3, 4, 5])
            for i in range(blocks_num):
                bx = x + 40 + i * 40
                b_type = "question" if (i == blocks_num // 2 or random.random() < 0.2) else "brick"
                tiles.append(Tile(bx, block_y, b_type, theme))
                
        # Enemies
        if random.random() < 0.45:
            num_e = random.choice([1, 2])
            for i in range(num_e):
                ex = x + 100 + i * 60
                e_type = "koopa" if random.random() < 0.3 else "goomba"
                enemies.append(Enemy(ex, ground_y - 48 if e_type == "koopa" else ground_y - 32, e_type))
                
        # Firebars in Castle levels
        if theme == "castle" and random.random() < 0.35:
            # We will render firebars dynamically
            pass
            
        x += segment_width

    # End flagpole / castle
    flag_x = level_width - 320
    tiles.append(Tile(flag_x, ground_y, "ground", theme))
    tiles.append(Flagpole(flag_x + 12, ground_y - 400))
    
    castle_x = level_width - 200
    for tx in range(castle_x, castle_x + 200, 40):
        tiles.append(Tile(tx, ground_y, "ground", theme))
    tiles.append(Castle(castle_x + 40, ground_y - 160))

    # Special Boss Arena for Level 20
    if level_num == 20:
        # Clear everything from level_width - 700 onwards
        tiles = [t for t in tiles if t.x < level_width - 700]
        enemies = [e for e in enemies if e.x < level_width - 700]
        
        # Build boss bridge
        bridge_start = level_width - 700
        bridge_end = level_width - 240
        
        # Platform before bridge
        for tx in range(bridge_start - 120, bridge_start, 40):
            tiles.append(Tile(tx, ground_y, "ground", "castle"))
            
        # Lava pit & bridge
        for tx in range(bridge_start, bridge_end, 40):
            tiles.append(Tile(tx, ground_y + 40, "lava", "castle"))
            tiles.append(Tile(tx, ground_y, "bridge", "castle"))
            
        # Throne room platform
        for tx in range(bridge_end, level_width, 40):
            tiles.append(Tile(tx, ground_y, "ground", "castle"))
            
        # Spawn Bowser Boss
        enemies.append(Bowser(bridge_end - 150, ground_y - 96))
        
        # Spawn Golden Axe button
        tiles.append(AxeButton(bridge_end + 60, ground_y - 40))

    return tiles, enemies, level_width, theme

# -----------------------------------------------------------------------------
# Main Game Draw Loop
# -----------------------------------------------------------------------------
def draw_scene(surf, player, tiles, powerups, enemies, fireballs, boss_fireballs, particles, offset_x, level_width, theme, level_num):
    # Dynamic background gradient based on theme
    if theme == "cave":
        surf.fill((5, 3, 10))
    elif theme == "desert":
        surf.fill((20, 10, 5))
    elif theme == "ice":
        surf.fill((5, 15, 20))
    elif theme == "castle":
        surf.fill((10, 3, 3))
    else:
        # Grassland night sky
        surf.fill(DARK_BG)
        
    # Draw Background Grid / Stars
    for i in range(0, WIDTH, 50):
        # Parallax grid scrolling
        bg_offset = (i - int(offset_x * 0.2)) % WIDTH
        pygame.draw.line(surf, GRID_COLOR, (bg_offset, 0), (bg_offset, HEIGHT))
        
    # Draw Hazards / Lava / Bridge / Tiles
    for tile in tiles:
        if tile.x - offset_x > -40 and tile.x - offset_x < WIDTH + 40:
            tile.draw(surf, offset_x)
            
    # Draw PowerUps
    for pu in powerups:
        pu.draw(surf, offset_x)
        
    # Draw Enemies
    for enemy in enemies:
        enemy.draw(surf, offset_x)
        
    # Draw Fireballs
    for fb in fireballs:
        fb.draw(surf, offset_x)
        
    # Draw Boss Fireballs
    for bfb in boss_fireballs:
        bfb.draw(surf, offset_x)
        
    # Draw Player (Mario)
    player.draw(surf, offset_x)
    
    # Draw Particles
    for p in particles:
        p.draw(surf, offset_x)
        
    # Draw HUD Overlay
    hud_y = 20
    # Level info
    lvl_txt = FONT_HUD.render(f"STAGE: {level_num} - {theme.upper()}", True, NEON_BLUE)
    surf.blit(lvl_txt, (30, hud_y))
    
    # Coins
    coin_txt = FONT_HUD.render(f"COINS: {player.coins:02d}", True, GOLD)
    surf.blit(coin_txt, (320, hud_y))
    
    # Score
    score_txt = FONT_HUD.render(f"SCORE: {player.score:06d}", True, NEON_GREEN)
    surf.blit(score_txt, (520, hud_y))
    
    # Lives
    lives_txt = FONT_HUD.render(f"LIVES: {player.lives}", True, NEON_PINK)
    surf.blit(lives_txt, (820, hud_y))

# -----------------------------------------------------------------------------
# Main Game Loop
# -----------------------------------------------------------------------------
async def main(window):
    init_sprites()
    
    clock = pygame.time.Clock()
    
    # Game states: "menu", "playing", "level_clear", "game_over", "game_complete"
    game_state = "menu"
    current_level = 1
    
    player = Player()
    tiles, enemies, level_width, theme = generate_level(current_level)
    powerups = []
    fireballs = []
    boss_fireballs = []
    particles = []
    
    offset_x = 0
    start_time = time.time()
    score_submitted = False
    
    # Boss variables
    bowser_active = False
    bridge_destruction_timer = 0
    bridge_destroy_x = 0
    
    run = True
    while run:
        clock.tick(FPS)
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if game_state == "menu":
                    # Choose level on Menu
                    if event.key == pygame.K_UP:
                        current_level = min(20, current_level + 1)
                    elif event.key == pygame.K_DOWN:
                        current_level = max(1, current_level - 1)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Start game
                        player = Player()
                        tiles, enemies, level_width, theme = generate_level(current_level)
                        powerups.clear()
                        fireballs.clear()
                        boss_fireballs.clear()
                        particles.clear()
                        offset_x = 0
                        start_time = time.time()
                        score_submitted = False
                        bowser_active = current_level == 20
                        bridge_destruction_timer = 0
                        game_state = "playing"
                        
                elif game_state in ["game_over", "game_complete"]:
                    if event.key == pygame.K_r:
                        game_state = "menu"
                        
                elif game_state == "playing":
                    if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                        player.jump()
                    elif event.key in [pygame.K_LSHIFT, pygame.K_c]:
                        player.shoot_fireball(fireballs)

        # 2. Game Logic Updates
        if game_state == "playing" and player.death_timer == 0:
            # Keyboard inputs
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.vx = -5
                player.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.vx = 5
                player.facing_right = True
                
            # Update Player
            player.update()
            
            # Update Tiles (block bumps)
            for tile in tiles:
                tile.update()
                
            # Update Powerups
            for pu in powerups[:]:
                pu.update(tiles)
                # Collision with Player
                if pu.get_rect().colliderect(player.get_rect()):
                    if pu.type == "mushroom":
                        if player.state == "small":
                            player.state = "big"
                        player.score += 1000
                    elif pu.type == "flower":
                        player.state = "fire"
                        player.score += 1000
                    powerups.remove(pu)
                    particles.append(TextParticle(player.x + 15, player.y - 20, "POWER UP!", NEON_GREEN))
                    for _ in range(10):
                        particles.append(Particle(player.x + 15, player.y + 10, random.uniform(-2, 2), random.uniform(-3, -1), GOLD, 3, 20))

            # Update Fireballs
            for fb in fireballs[:]:
                fb.update(tiles)
                if fb.life <= 0:
                    fireballs.remove(fb)
                    continue
                # Hit enemies
                fb_rect = fb.get_rect()
                for enemy in enemies[:]:
                    if enemy.is_dead: continue
                    if fb_rect.colliderect(enemy.get_rect()):
                        if enemy.type == "bowser":
                            # Bowser takes damage
                            bowser = enemy
                            bowser.hp -= 1
                            fireballs.remove(fb)
                            for _ in range(8):
                                particles.append(Particle(fb.x, fb.y, random.uniform(-3, 3), random.uniform(-3, 3), GOLD, 3, 15))
                            if bowser.hp <= 0:
                                # Trigger Boss defeat!
                                bowser.is_dead = True
                                bowser.vx = 0
                                bowser.vy = -8 # Fly up and fall down
                                player.score += 5000
                                particles.append(TextParticle(bowser.x + 48, bowser.y, "DEFEATED!", GOLD))
                        else:
                            enemy.is_dead = True
                            enemy.vy = -6
                            enemy.dead_timer = 60
                            fireballs.remove(fb)
                            break

            # Update Boss Fireballs
            for bfb in boss_fireballs[:]:
                bfb.update()
                if bfb.life <= 0:
                    boss_fireballs.remove(bfb)
                    continue
                if bfb.get_rect().colliderect(player.get_rect()):
                    player.take_damage(particles)
                    boss_fireballs.remove(bfb)

            # Update Enemies
            for enemy in enemies[:]:
                if enemy.type == "bowser":
                    enemy.update(tiles, boss_fireballs)
                else:
                    enemy.update(tiles)
                    
                if enemy.is_dead:
                    if enemy.dead_timer <= 0:
                        enemies.remove(enemy)
                    continue
                    
                # Collision with Player
                e_rect = enemy.get_rect()
                p_rect = player.get_rect()
                if e_rect.colliderect(p_rect):
                    if enemy.type == "piranha":
                        player.take_damage(particles)
                    elif enemy.type == "bowser":
                        player.take_damage(particles)
                    elif player.vy > 0 and player.y + player.height - 15 < enemy.y:
                        # Stomp enemy!
                        enemy.stomped(player, particles)
                        player.vy = -8  # Bounce jump
                    else:
                        if enemy.type == "koopa_shell" and enemy.vx == 0:
                            # Kick shell
                            enemy.stomped(player, particles)
                        else:
                            # Take damage
                            player.take_damage(particles)

            # Update Particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            # Vertical Collisions & Gravity for Player
            p_rect = player.get_rect()
            player.on_ground = False
            for tile in tiles:
                if tile.type == "shattered": continue
                t_rect = tile.get_rect()
                if p_rect.colliderect(t_rect):
                    if tile.type == "lava":
                        player.die()
                        break
                    if player.vy > 0 and player.y + (40 if player.state == "small" else 72) - 15 < t_rect.top:
                        player.y = t_rect.top - (40 if player.state == "small" else 72)
                        player.vy = 0
                        player.on_ground = True
                    elif player.vy < 0 and player.y > t_rect.bottom - 20:
                        player.y = t_rect.bottom
                        player.vy = 0
                        tile.trigger_hit(player, powerups, particles)

            # Horizontal Collisions for Player
            p_rect = player.get_rect()
            for tile in tiles:
                if tile.type in ["shattered", "lava", "bridge"]: continue
                t_rect = tile.get_rect()
                if p_rect.colliderect(t_rect):
                    # Flagpole check
                    if tile.type == "flagpole":
                        game_state = "level_clear"
                        player.vx = 0
                        player.vy = 2
                        start_time = time.time()
                        break
                    # Axe Button check
                    elif tile.type == "axe_button" and not tile.triggered:
                        tile.triggered = True
                        bridge_destruction_timer = 90
                        bridge_destroy_x = level_width - 700
                        # Kill Bowser if alive
                        for e in enemies:
                            if e.type == "bowser":
                                e.is_dead = True
                                e.vx = 0
                                e.vy = 4
                        break
                        
                    if player.vx > 0:
                        player.x = t_rect.left - player.width
                        player.vx = 0
                    elif player.vx < 0:
                        player.x = t_rect.right
                        player.vx = 0

            # Bowser Bridge Destruction Animation
            if bridge_destruction_timer > 0:
                bridge_destruction_timer -= 1
                if bridge_destruction_timer % 6 == 0:
                    # Remove bridge tile
                    tiles = [t for t in tiles if not (t.type == "bridge" and t.x == bridge_destroy_x)]
                    # Spawn lava splash particles
                    for _ in range(5):
                        particles.append(Particle(bridge_destroy_x + 20, ground_y + 40, random.uniform(-2, 2), random.uniform(-4, -1), LAVA_RED, 4, 20))
                    bridge_destroy_x += 40
                    
                if bridge_destruction_timer == 0:
                    # Bowser fell! Clear level
                    game_state = "level_clear"
                    start_time = time.time()

            # Screen scrolling
            if player.x - offset_x > WIDTH * 0.45:
                offset_x = player.x - WIDTH * 0.45
            if offset_x < 0:
                offset_x = 0
            if offset_x > level_width - WIDTH:
                offset_x = level_width - WIDTH

            # Boundary checks
            if player.y > HEIGHT:
                player.die()

            if player.lives <= 0:
                game_state = "game_over"

        # 3. Special States Handling
        elif game_state == "level_clear":
            # Slide down flagpole animation
            if player.y < ground_y - (40 if player.state == "small" else 72):
                player.y += 2
            else:
                # Walk into castle
                player.x += 2
                player.facing_right = True
                player.is_walking = True
                player.walk_frame += 1
                
            # Spawn celebratory fireworks
            if random.random() < 0.08:
                fx = random.randint(100, WIDTH - 100)
                fy = random.randint(100, 300)
                color = random.choice([NEON_BLUE, NEON_PINK, NEON_GREEN, GOLD])
                for _ in range(20):
                    particles.append(Particle(fx + offset_x, fy, random.uniform(-4, 4), random.uniform(-4, 4), color, 4, 35))
                    
            # Update particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            # Wait 4 seconds, then proceed
            if time.time() - start_time > 4.0:
                if current_level == 20:
                    game_state = "game_complete"
                else:
                    current_level += 1
                    player.x = 150
                    player.y = 500
                    player.vx = 0
                    player.vy = 0
                    tiles, enemies, level_width, theme = generate_level(current_level)
                    powerups.clear()
                    fireballs.clear()
                    boss_fireballs.clear()
                    particles.clear()
                    offset_x = 0
                    bowser_active = current_level == 20
                    bridge_destruction_timer = 0
                    game_state = "playing"

        elif game_state == "game_over":
            if not score_submitted:
                score_submitted = True
                if arcade_api:
                    arcade_api.submit_score("Neon Mario Bros", player.score)

        elif game_state == "game_complete":
            if not score_submitted:
                score_submitted = True
                # Grand victory bonus score!
                player.score += player.lives * 5000
                if arcade_api:
                    arcade_api.submit_score("Neon Mario Bros", player.score)
                    
            # Spawn massive fireworks show
            if random.random() < 0.15:
                fx = random.randint(100, WIDTH - 100)
                fy = random.randint(100, 350)
                color = random.choice([NEON_BLUE, NEON_PINK, NEON_GREEN, GOLD, NEON_PURPLE])
                for _ in range(30):
                    particles.append(Particle(fx + offset_x, fy, random.uniform(-5, 5), random.uniform(-5, 5), color, 4, 40))
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

        elif player.death_timer > 0:
            player.update()
            if player.death_timer == 1:
                # Respawn
                if player.lives > 0:
                    player.x = 150
                    player.y = 500
                    player.vx = 0
                    player.vy = 0
                    player.state = "small"
                    offset_x = 0
                    fireballs.clear()
                    boss_fireballs.clear()
                    # Rebuild current level
                    tiles, enemies, level_width, theme = generate_level(current_level)
                    powerups.clear()
                    game_state = "playing"
                else:
                    game_state = "game_over"

        # 4. Render
        if game_state == "menu":
            WIN.fill(DARK_BG)
            # Drawing neon cabinet title
            title_txt = FONT_OVERLAY.render("NEON MARIO BROS", True, NEON_BLUE)
            WIN.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 150))
            
            sub_txt = FONT_OVERLAY_SUB.render("SELECT STARTING SECTOR (STAGE 1-20)", True, WHITE)
            WIN.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, 260))
            
            # Level selector
            lvl_sel = FONT_OVERLAY.render(f"<  STAGE {current_level:02d}  >", True, GOLD)
            WIN.blit(lvl_sel, (WIDTH // 2 - lvl_sel.get_width() // 2, 330))
            
            controls_txt = FONT_OVERLAY_SUB.render("KEYS: ARROWS / WASD TO MOVE | SPACE / UP TO JUMP | C / SHIFT TO SHOOT", True, NEON_PINK)
            WIN.blit(controls_txt, (WIDTH // 2 - controls_txt.get_width() // 2, 470))
            
            start_txt = FONT_OVERLAY_SUB.render("PRESS ENTER OR SPACE TO INITIATE SEQUENCE", True, NEON_GREEN)
            WIN.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 530))
            
            pygame.display.update()
            
        elif game_state == "game_over":
            WIN.fill(DARK_BG)
            go_txt = FONT_OVERLAY.render("SYSTEM OFFLINE", True, NEON_PINK)
            WIN.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, 200))
            
            score_txt = FONT_OVERLAY_SUB.render(f"FINAL RECORDED SCORE: {player.score:06d}", True, GOLD)
            WIN.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 300))
            
            reboot_txt = FONT_OVERLAY_SUB.render("PRESS 'R' TO REBOOT CABINET", True, NEON_BLUE)
            WIN.blit(reboot_txt, (WIDTH // 2 - reboot_txt.get_width() // 2, 400))
            pygame.display.update()
            
        elif game_state == "game_complete":
            WIN.fill(DARK_BG)
            # Draw stars/particles behind
            for p in particles:
                p.draw(WIN, 0)
                
            vic_txt = FONT_OVERLAY.render("GRID CHAMPION", True, NEON_GREEN)
            WIN.blit(vic_txt, (WIDTH // 2 - vic_txt.get_width() // 2, 160))
            
            desc_txt = FONT_OVERLAY_SUB.render("BOWSER CONQUERED. PEACE RETURNED TO THE SYSTEM.", True, WHITE)
            WIN.blit(desc_txt, (WIDTH // 2 - desc_txt.get_width() // 2, 250))
            
            score_txt = FONT_OVERLAY_SUB.render(f"FINAL CHAMPION SCORE: {player.score:06d}", True, GOLD)
            WIN.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 320))
            
            reboot_txt = FONT_OVERLAY_SUB.render("PRESS 'R' TO RETURN TO CABINET SYSTEM", True, NEON_BLUE)
            WIN.blit(reboot_txt, (WIDTH // 2 - reboot_txt.get_width() // 2, 450))
            pygame.display.update()
            
        else:
            # Standard game draw
            draw_scene(WIN, player, tiles, powerups, enemies, fireballs, boss_fireballs, particles, offset_x, level_width, theme, current_level)
            pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main(WIN))
