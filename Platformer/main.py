import os
import sys
import random
import math
import pygame
import asyncio
import time
from os import listdir
from os.path import isfile, join

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

pygame.display.set_caption("Cyber Platformer - Arcade Edition")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors (Arcade Cyberpunk Palette)
DARK_BG = (8, 8, 16)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)

# Fonts
try:
    FONT_HUD = pygame.font.SysFont("Outfit", 20, bold=True)
    FONT_HUD_VAL = pygame.font.SysFont("Outfit", 24, bold=True)
    FONT_OVERLAY = pygame.font.SysFont("Outfit", 55, bold=True)
    FONT_OVERLAY_SUB = pygame.font.SysFont("Outfit", 22, bold=True)
except:
    try:
        FONT_HUD = pygame.font.SysFont("Segoe UI", 20, bold=True)
        FONT_HUD_VAL = pygame.font.SysFont("Segoe UI", 24, bold=True)
        FONT_OVERLAY = pygame.font.SysFont("Segoe UI", 55, bold=True)
        FONT_OVERLAY_SUB = pygame.font.SysFont("Segoe UI", 22, bold=True)
    except:
        FONT_HUD = pygame.font.Font(None, 20)
        FONT_HUD_VAL = pygame.font.Font(None, 24)
        FONT_OVERLAY = pygame.font.Font(None, 55)
        FONT_OVERLAY_SUB = pygame.font.Font(None, 22)


# Particle Classes
class DustParticle:
    def __init__(self, x, y, color=(200, 220, 255, 150)):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-0.8, -0.2)
        self.life = random.randint(10, 20)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface, offset_x):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x - offset_x), int(self.y)), radius)


class EmberParticle:
    def __init__(self, x, y, color=(255, 100, 0)):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-1.5, -0.5)
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface, offset_x):
        radius = int((self.life / self.max_life) * 3) + 1
        pygame.draw.circle(surface, self.color, (int(self.x - offset_x), int(self.y)), radius)


class ExplosionParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5.0, 5.0)
        self.vy = random.uniform(-6.0, 2.0)
        self.life = random.randint(18, 32)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12  # Gravity drag
        self.life -= 1

    def draw(self, surface, offset_x):
        radius = int((self.life / self.max_life) * 5) + 1
        pygame.draw.circle(surface, self.color, (int(self.x - offset_x), int(self.y)), radius)


# Core utility functions
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, character="MaskDude"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.character = character
        self.SPRITES = load_sprite_sheets("MainCharacters", character, 32, 32, True)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.lives = 3

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self, state_bag, explosion_particles):
        if not self.hit:
            self.hit = True
            self.lives -= 1
            
            # Hit feedback: spawn massive debris sparks!
            for _ in range(18):
                explosion_particles.append(ExplosionParticle(self.rect.centerx, self.rect.centery, NEON_PINK))
            for _ in range(12):
                explosion_particles.append(ExplosionParticle(self.rect.centerx, self.rect.centery, GOLD))

            # Shake screen!
            state_bag["shake_duration"] = 25
            state_bag["shake_amount"] = 12

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 1.5:  # Reduced invincibility duration slightly for better arcade urgency
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        # Draw flashing effect if hit (invincible state)
        if self.hit and (self.hit_count // 4) % 2 == 0:
            return
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Portal(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "portal")
        self.pulse_dir = 1
        self.pulse_val = 0
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.mask = pygame.mask.from_surface(self.image)

    def loop(self):
        # Pulsing concentric ring effects
        self.pulse_val += self.pulse_dir * 0.05
        if self.pulse_val > 1.0:
            self.pulse_val = 1.0
            self.pulse_dir = -1
        elif self.pulse_val < 0.0:
            self.pulse_val = 0.0
            self.pulse_dir = 1

        self.image.fill((0, 0, 0, 0))
        glow = int(140 + 100 * self.pulse_val)
        
        # Outer ring
        pygame.draw.ellipse(self.image, (0, 200, 255, glow), (0, 0, self.width, self.height), 4)
        # Middle ring
        pygame.draw.ellipse(self.image, (0, 255, 180, int(glow * 0.6)), (8, 8, self.width - 16, self.height - 16), 3)
        # Inner core
        pygame.draw.ellipse(self.image, (255, 255, 255, int(glow * 0.8)), (16, 16, self.width - 32, self.height - 32))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw_hud(window, player, start_time, current_level):
    # Sleek glassmorphic HUD bar at top-left
    hud_w, hud_h = 360, 90
    hud_x, hud_y = 25, 25
    
    hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
    pygame.draw.rect(hud_surf, (12, 16, 32, 190), (0, 0, hud_w, hud_h), border_radius=8)
    window.blit(hud_surf, (hud_x, hud_y))
    pygame.draw.rect(window, NEON_BLUE, (hud_x, hud_y, hud_w, hud_h), 2, border_radius=8)

    # 1. Lives indicator (Draw hearts or neon-pink text)
    lives_lbl = FONT_HUD.render("CORE STATUS", True, NEON_PINK)
    lives_val = FONT_HUD_VAL.render("HP " * player.lives if player.lives > 0 else "OFFLINE", True, WHITE)
    window.blit(lives_lbl, (hud_x + 15, hud_y + 10))
    window.blit(lives_val, (hud_x + 15, hud_y + 30))

    # 2. Timer indicator
    elapsed = int(time.time() - start_time) if player.lives > 0 else 0
    time_lbl = FONT_HUD.render("RUNTIME", True, GOLD)
    time_val = FONT_HUD_VAL.render(f"{elapsed}s", True, WHITE)
    window.blit(time_lbl, (hud_x + 150, hud_y + 10))
    window.blit(time_val, (hud_x + 150, hud_y + 30))

    # 3. Level indicator
    lvl_lbl = FONT_HUD.render("STAGELINE", True, NEON_GREEN)
    lvl_val = FONT_HUD_VAL.render(f"STAGE {current_level}/3", True, WHITE)
    window.blit(lvl_lbl, (hud_x + 250, hud_y + 10))
    window.blit(lvl_val, (hud_x + 250, hud_y + 30))


def draw(window, background, bg_image, player, objects, offset_x, dust_particles, ember_particles, explosion_particles, start_time, current_level):
    # Draw tiled background
    for tile in background:
        window.blit(bg_image, tile)

    # Draw particles behind player/foreground
    for dp in dust_particles:
        dp.draw(window, offset_x)

    for ep in ember_particles:
        ep.draw(window, offset_x)

    for xp in explosion_particles:
        xp.draw(window, offset_x)

    # Draw terrain and traps
    for obj in objects:
        obj.draw(window, offset_x)

    # Draw player character
    player.draw(window, offset_x)

    # Draw HUD
    draw_hud(window, player, start_time, current_level)

    pygame.display.update()


def draw_game_overlay(win, title_text, sub_text, border_color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
    win.blit(overlay, (0, 0))

    # Glow card
    card_w, card_h = 600, 240
    card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
    
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (15, 15, 30, 220), (0, 0, card_w, card_h), border_radius=15)
    win.blit(card_surf, (card_x, card_y))
    pygame.draw.rect(win, border_color, (card_x, card_y, card_w, card_h), 3, border_radius=15)

    title = FONT_OVERLAY.render(title_text, 1, border_color)
    sub = FONT_OVERLAY_SUB.render(sub_text, 1, WHITE)

    win.blit(title, (WIDTH // 2 - title.get_width() // 2, card_y + 50))
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, card_y + 140))
    pygame.display.update()


def load_character_idles():
    idles = {
        "MaskDude": load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)["idle_right"],
        "NinjaForg": load_sprite_sheets("MainCharacters", "NinjaForg", 32, 32, True)["idle_right"],
        "PinkMan": load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)["idle_right"],
        "VirtualGuy": load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)["idle_right"]
    }
    return idles


async def character_selection(window, clock):
    idles = load_character_idles()
    characters = ["MaskDude", "NinjaForg", "PinkMan", "VirtualGuy"]
    display_names = {
        "MaskDude": "MASK DUDE",
        "NinjaForg": "NINJA FROG",
        "PinkMan": "PINK MAN",
        "VirtualGuy": "VIRTUAL GUY"
    }
    selected_idx = 0
    animation_count = 0
    ANIMATION_DELAY = 4
    
    background, bg_image = get_background("Blue.png")
    
    selecting = True
    while selecting:
        clock.tick(FPS)
        animation_count += 1
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    selected_idx = (selected_idx - 1) % len(characters)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    selected_idx = (selected_idx + 1) % len(characters)
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    selecting = False
                    break
        
        # Draw background
        for tile in background:
            window.blit(bg_image, tile)
            
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (8, 8, 16, 205), (0, 0, WIDTH, HEIGHT))
        window.blit(overlay, (0, 0))
        
        # Title
        title_text = FONT_OVERLAY.render("SELECT YOUR CYBER HUNTER", True, NEON_BLUE)
        window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Draw character cards
        card_w, card_h = 190, 260
        gap = 30
        start_x = (WIDTH - (card_w * 4 + gap * 3)) // 2
        
        for i, char in enumerate(characters):
            x = start_x + i * (card_w + gap)
            y = 260
            
            # Animate sprite
            sprites = idles[char]
            sprite_idx = (animation_count // ANIMATION_DELAY) % len(sprites)
            sprite = sprites[sprite_idx]
            # Scale up to 110x110
            scaled_sprite = pygame.transform.scale(sprite, (110, 110))
            
            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if i == selected_idx:
                # Active selection glowing card
                pygame.draw.rect(card_surf, (20, 25, 60, 230), (0, 0, card_w, card_h), border_radius=12)
                window.blit(card_surf, (x, y))
                pygame.draw.rect(window, NEON_BLUE, (x, y, card_w, card_h), 4, border_radius=12)
                # Pulse outline glow
                glow_val = int(140 + 100 * math.sin(time.time() * 8))
                pygame.draw.rect(window, (0, 200, 255, max(0, min(255, glow_val))), (x - 2, y - 2, card_w + 4, card_h + 4), 1, border_radius=14)
            else:
                # Inactive card
                pygame.draw.rect(card_surf, (12, 12, 24, 180), (0, 0, card_w, card_h), border_radius=12)
                window.blit(card_surf, (x, y))
                pygame.draw.rect(window, (255, 255, 255, 30), (x, y, card_w, card_h), 2, border_radius=12)
                
            # Draw animated sprite
            window.blit(scaled_sprite, (x + (card_w - 110) // 2, y + 40))
            
            # Draw name
            color = WHITE if i == selected_idx else (150, 150, 150)
            name_text = FONT_HUD_VAL.render(display_names[char], True, color)
            window.blit(name_text, (x + (card_w - name_text.get_width()) // 2, y + 185))
            
        # Footer text
        footer_text = FONT_OVERLAY_SUB.render("PRESS A/D OR ARROWS TO NAVIGATE | SPACE OR ENTER TO CHOOSE", True, GOLD)
        window.blit(footer_text, (WIDTH // 2 - footer_text.get_width() // 2, 600))
        
        pygame.display.update()
        await asyncio.sleep(0)
        
    return characters[selected_idx]


def load_level(level_num, block_size):
    if level_num == 1:
        # Level 1 Floor
        floor = [Block(i * block_size, HEIGHT - block_size, block_size)
                 for i in range(-5, 35)]
        
        # Level 1 Traps & Blocks
        fire1 = Fire(block_size * 8, HEIGHT - block_size - 64, 16, 32)
        fire1.on()
        fire2 = Fire(block_size * 16, HEIGHT - block_size - 64, 16, 32)
        fire2.on()
        
        objects = [
            *floor,
            Block(block_size * 3, HEIGHT - block_size * 2, block_size),
            Block(block_size * 4, HEIGHT - block_size * 2, block_size),
            Block(block_size * 7, HEIGHT - block_size * 3, block_size),
            Block(block_size * 12, HEIGHT - block_size * 2, block_size),
            Block(block_size * 13, HEIGHT - block_size * 3, block_size),
            fire1,
            fire2,
            Portal(block_size * 24, HEIGHT - block_size - 96, 64, 96)
        ]
        
    elif level_num == 2:
        # Level 2 Floor (Longer floor, more hazards)
        floor = [Block(i * block_size, HEIGHT - block_size, block_size)
                 for i in range(-5, 38)]
        
        # Trap rows
        fire1 = Fire(block_size * 5, HEIGHT - block_size - 64, 16, 32)
        fire1.on()
        fire2 = Fire(block_size * 6, HEIGHT - block_size - 64, 16, 32)
        fire2.on()
        fire3 = Fire(block_size * 12, HEIGHT - block_size - 64, 16, 32)
        fire3.on()
        fire4 = Fire(block_size * 13, HEIGHT - block_size - 64, 16, 32)
        fire4.on()
        fire5 = Fire(block_size * 14, HEIGHT - block_size - 64, 16, 32)
        fire5.on()
        
        objects = [
            *floor,
            # Block bridges over fire traps
            Block(block_size * 5, HEIGHT - block_size * 3, block_size),
            Block(block_size * 13, HEIGHT - block_size * 3, block_size),
            # General navigation
            Block(block_size * 2, HEIGHT - block_size * 2, block_size),
            Block(block_size * 9, HEIGHT - block_size * 2, block_size),
            Block(block_size * 18, HEIGHT - block_size * 2, block_size),
            Block(block_size * 20, HEIGHT - block_size * 4, block_size),
            Block(block_size * 22, HEIGHT - block_size * 2, block_size),
            fire1, fire2, fire3, fire4, fire5,
            Portal(block_size * 27, HEIGHT - block_size - 96, 64, 96)
        ]
        
    elif level_num == 3:
        # Level 3 Floor (Chasms and high-altitude floating platforms)
        # solid segment 1
        floor1 = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-5, 7)]
        # solid segment 2
        floor2 = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(12, 17)]
        # solid segment 3
        floor3 = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(22, 32)]
        
        # Traps on solid floors
        fire1 = Fire(block_size * 3, HEIGHT - block_size - 64, 16, 32)
        fire1.on()
        fire2 = Fire(block_size * 14, HEIGHT - block_size - 64, 16, 32)
        fire2.on()
        fire3 = Fire(block_size * 25, HEIGHT - block_size - 64, 16, 32)
        fire3.on()
        
        objects = [
            *floor1,
            *floor2,
            *floor3,
            # Floating stepping stones in first chasm (x=7 to 11)
            Block(block_size * 8, HEIGHT - block_size * 2, block_size),
            Block(block_size * 10, HEIGHT - block_size * 3, block_size),
            
            # Floating stepping stones in second chasm (x=17 to 21)
            Block(block_size * 18, HEIGHT - block_size * 3, block_size),
            Block(block_size * 20, HEIGHT - block_size * 2, block_size),
            
            # Additional vertical hazards
            Block(block_size * 14, HEIGHT - block_size * 3, block_size),
            Block(block_size * 24, HEIGHT - block_size * 3, block_size),
            fire1, fire2, fire3,
            Portal(block_size * 29, HEIGHT - block_size - 96, 64, 96)
        ]
        
    return objects


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects, state_bag, explosion_particles):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit(state_bag, explosion_particles)


async def main(window):
    clock = pygame.time.Clock()
    
    # 1. Run Character Selection Screen
    selected_char = await character_selection(window, clock)
    
    background, bg_image = get_background("Blue.png")
    block_size = 96

    # Instantiate selected character player
    player = Player(100, 100, 50, 50, selected_char)
    
    current_level = 1
    max_levels = 3
    objects = load_level(current_level, block_size)

    offset_x = 0
    scroll_area_width = 200

    # Particle registers
    dust_particles = []
    ember_particles = []
    explosion_particles = []

    # Game State variables
    state_bag = {
        "shake_duration": 0,
        "shake_amount": 0
    }
    
    start_time = time.time()
    score_submitted = False
    final_score = 0
    game_won = False
    run = True
    
    prev_y_vel = 0

    while run:
        clock.tick(FPS)

        # Update dust particles
        for p in dust_particles[:]:
            p.update()
            if p.life <= 0:
                dust_particles.remove(p)

        # Update embers (floating sparks from active fire traps)
        for p in ember_particles[:]:
            p.update()
            if p.life <= 0:
                ember_particles.remove(p)

        # Update explosion debris sparks
        for p in explosion_particles[:]:
            p.update()
            if p.life <= 0:
                explosion_particles.remove(p)

        # Loop active trap animations and portals
        for obj in objects:
            if hasattr(obj, "loop"):
                obj.loop()
            
            # Spawn glowing embers from active fire traps periodically
            if obj.name == "fire" and random.random() < 0.12:
                ember_particles.append(EmberParticle(obj.rect.centerx + random.uniform(-8, 8), obj.rect.centery + 10))

        # Keyboard event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if player.lives <= 0 or game_won:
                    if event.key == pygame.K_r:
                        # Reset game and select character again!
                        selected_char = await character_selection(window, clock)
                        player = Player(100, 100, 50, 50, selected_char)
                        current_level = 1
                        game_won = False
                        objects = load_level(current_level, block_size)
                        offset_x = 0
                        start_time = time.time()
                        score_submitted = False
                        dust_particles.clear()
                        ember_particles.clear()
                        explosion_particles.clear()
                else:
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w) and player.jump_count < 2:
                        player.jump()
                        # Jump puff particles!
                        for _ in range(8):
                            dust_particles.append(DustParticle(player.rect.centerx, player.rect.bottom))
                        
                        # Custom double-jump shockwave effect
                        if player.jump_count == 2:
                            state_bag["shake_duration"] = 5
                            state_bag["shake_amount"] = 3
                            for _ in range(12):
                                dust_particles.append(DustParticle(player.rect.centerx, player.rect.centery, NEON_BLUE))

        if player.lives > 0 and not game_won:
            # Running dust trail emitter
            if player.x_vel != 0 and player.y_vel == 0:
                if random.random() < 0.35:
                    dust_particles.append(DustParticle(player.rect.centerx, player.rect.bottom))

            # Landing detection (high y velocity down to 0)
            if prev_y_vel > 3 and player.y_vel == 0:
                # Landed puff particles!
                state_bag["shake_duration"] = 6
                state_bag["shake_amount"] = 3
                for _ in range(10):
                    dust_particles.append(DustParticle(player.rect.centerx, player.rect.bottom))

            # Death by falling in chasm (Level 3 specific death zone)
            if player.rect.top > HEIGHT + 100:
                player.lives = 0  # Core crash!
                # Spawn explosion particles from where the player fell
                for _ in range(25):
                    explosion_particles.append(ExplosionParticle(player.rect.centerx, HEIGHT - 20, NEON_PINK))

            prev_y_vel = player.y_vel

            player.loop(FPS)
            handle_move(player, objects, state_bag, explosion_particles)

            # Camera scroll
            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                    (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel
            
            # Check portal collision (Level clear transition)
            for obj in objects:
                if obj.name == "portal" and pygame.sprite.collide_mask(player, obj):
                    # Spawn level-clear confetti sparks!
                    for _ in range(30):
                        explosion_particles.append(ExplosionParticle(player.rect.centerx, player.rect.centery, NEON_GREEN))
                    
                    current_level += 1
                    if current_level > max_levels:
                        # Grand prix champion!
                        game_won = True
                    else:
                        # Load next stage!
                        objects = load_level(current_level, block_size)
                        player.rect.x = 100
                        player.rect.y = 100
                        player.x_vel = 0
                        player.y_vel = 0
                        offset_x = 0
                        dust_particles.clear()
                        ember_particles.clear()
                        explosion_particles.clear()
                        state_bag["shake_duration"] = 15
                        state_bag["shake_amount"] = 8
                    break
        
        # Render scene
        if player.lives <= 0:
            # Game Over screen
            if not score_submitted:
                score_submitted = True
                final_score = int(time.time() - start_time)
                if arcade_api:
                    arcade_api.submit_score("Platformer", final_score)
            draw_game_overlay(window, "SYSTEM OFFLINE", f"CORE CRASH. SURVIVED {final_score}s. PRESS 'R' TO REBOOT.", NEON_PINK)
        elif game_won:
            # Victory screen!
            if not score_submitted:
                score_submitted = True
                # Victory high score: time elapsed + 5000 GP bonus!
                final_score = int(time.time() - start_time) + 5000
                if arcade_api:
                    arcade_api.submit_score("Platformer", final_score)
            draw_game_overlay(window, "GRID CHAMPION", f"ALL SECTORS CLEARED! GRAND PRIX SCORE: {final_score}. PRESS 'R' TO REPLAY.", NEON_GREEN)
        else:
            # Handle screen shake
            if state_bag["shake_duration"] > 0:
                offset_sx = random.randint(-state_bag["shake_amount"], state_bag["shake_amount"])
                offset_sy = random.randint(-state_bag["shake_amount"], state_bag["shake_amount"])
                state_bag["shake_duration"] -= 1
            else:
                offset_sx = 0
                offset_sy = 0

            if offset_sx != 0 or offset_sy != 0:
                shaken_surface = pygame.Surface((WIDTH, HEIGHT))
                draw(shaken_surface, background, bg_image, player, objects, offset_x, dust_particles, ember_particles, explosion_particles, start_time, current_level)
                window.fill(DARK_BG)
                window.blit(shaken_surface, (offset_sx, offset_sy))
                pygame.display.update()
            else:
                draw(window, background, bg_image, player, objects, offset_x, dust_particles, ember_particles, explosion_particles, start_time, current_level)

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main(window))