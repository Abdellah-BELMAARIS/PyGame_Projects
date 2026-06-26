import pygame
import time
import math
import asyncio
import random
import os
import sys
from utils import scale_image, blit_rotate_center

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

# Load images
GRASS = scale_image(pygame.image.load("imgs/grass.png"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Velocity - Arcade Racing")

# Colors (Arcade Cyberpunk Palette)
DARK_BG = (8, 8, 16)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
NEON_GREEN = (0, 255, 100)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)

# Fonts
try:
    MAIN_FONT = pygame.font.SysFont("Outfit", 20, bold=True)
    HUD_VAL_FONT = pygame.font.SysFont("Outfit", 22, bold=True)
    HEADER_FONT = pygame.font.SysFont("Outfit", 45, bold=True)
    MESSAGE_FONT = pygame.font.SysFont("Outfit", 28, bold=True)
except:
    try:
        MAIN_FONT = pygame.font.SysFont("Segoe UI", 20, bold=True)
        HUD_VAL_FONT = pygame.font.SysFont("Segoe UI", 22, bold=True)
        HEADER_FONT = pygame.font.SysFont("Segoe UI", 45, bold=True)
        MESSAGE_FONT = pygame.font.SysFont("Segoe UI", 28, bold=True)
    except:
        MAIN_FONT = pygame.font.Font(None, 20)
        HUD_VAL_FONT = pygame.font.Font(None, 22)
        HEADER_FONT = pygame.font.Font(None, 45)
        MESSAGE_FONT = pygame.font.Font(None, 28)

FPS = 60
PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]


# Particle Classes
class SmokeParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-0.6, 0.6)
        self.life = random.randint(12, 22)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 5) + 1
        # Draw soft glowing smoke
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class SparkParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3.5, 3.5)
        self.vy = random.uniform(-3.5, 3.5)
        self.life = random.randint(15, 25)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity drag
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 3) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class GameInfo:
    LEVELS = 5  # Adjusted to match a neat cabinet session length

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.score = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0
        self.score = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.12

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

    def emit_trail(self, particles, color):
        # Calculate rear tire position of the car based on dimensions and rotation
        radians = math.radians(self.angle)
        center_x = self.x + self.img.get_width() / 2
        center_y = self.y + self.img.get_height() / 2
        
        # Shift back along heading angle to reach rear of the car
        rear_x = center_x + math.sin(radians) * 16
        rear_y = center_y + math.cos(radians) * 16
        
        # Add slight randomness
        particles.append(SmokeParticle(rear_x + random.uniform(-2, 2), rear_y + random.uniform(-2, 2), color))


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 1.5, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel * 0.6
        self.move()


class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw(self, win):
        super().draw(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.25
        self.current_point = 0


def draw_hud(win, player_car, game_info):
    # Modern Glassmorphic HUD Card at top-left
    hud_w, hud_h = 220, 150
    hud_x, hud_y = 20, 20
    
    hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
    pygame.draw.rect(hud_surf, (10, 12, 30, 190), (0, 0, hud_w, hud_h), border_radius=10)
    win.blit(hud_surf, (hud_x, hud_y))
    pygame.draw.rect(win, NEON_BLUE, (hud_x, hud_y, hud_w, hud_h), 2, border_radius=10)

    # 1. Level label
    lvl_lbl = MAIN_FONT.render("ARCADE LEVEL", True, NEON_PINK)
    lvl_val = HUD_VAL_FONT.render(str(game_info.level), True, WHITE)
    win.blit(lvl_lbl, (hud_x + 15, hud_y + 12))
    win.blit(lvl_val, (hud_x + 160, hud_y + 10))

    # 2. Time label
    time_lbl = MAIN_FONT.render("LAP TIME", True, GOLD)
    time_val = HUD_VAL_FONT.render(f"{game_info.get_level_time()}s", True, WHITE)
    win.blit(time_lbl, (hud_x + 15, hud_y + 44))
    win.blit(time_val, (hud_x + 160, hud_y + 42))

    # 3. Speed label (Multiplied velocity for arcade scale feel)
    speed_lbl = MAIN_FONT.render("VELOCITY", True, NEON_GREEN)
    speed_val = HUD_VAL_FONT.render(f"{int(player_car.vel * 45)} KM/H", True, WHITE)
    win.blit(speed_lbl, (hud_x + 15, hud_y + 76))
    win.blit(speed_val, (hud_x + 130, hud_y + 74))

    # 4. Score label
    score_lbl = MAIN_FONT.render("ARCADE SCORE", True, NEON_BLUE)
    score_val = HUD_VAL_FONT.render(str(game_info.score), True, WHITE)
    win.blit(score_lbl, (hud_x + 15, hud_y + 108))
    win.blit(score_val, (hud_x + 130, hud_y + 106))


def draw(win, images, player_car, computer_car, game_info, smoke_particles, spark_particles):
    # Base background blit
    for img, pos in images:
        win.blit(img, pos)

    # Draw Smoke trails
    for p in smoke_particles:
        p.draw(win)

    # Draw Sparks
    for p in spark_particles:
        p.draw(win)

    # Draw Cars
    player_car.draw(win)
    computer_car.draw(win)

    # Draw HUD
    draw_hud(win, player_car, game_info)
    pygame.display.update()


def draw_game_overlay(win, title_text, sub_text, border_color):
    # Full overlay dim
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (5, 5, 12, 210), (0, 0, WIDTH, HEIGHT))
    win.blit(overlay, (0, 0))
    
    # Glowing glass card
    card_w, card_h = 520, 240
    card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
    
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (15, 17, 34, 230), (0, 0, card_w, card_h), border_radius=15)
    win.blit(card_surf, (card_x, card_y))
    pygame.draw.rect(win, border_color, (card_x, card_y, card_w, card_h), 3, border_radius=15)

    # Draw text with glows/shadows
    title = HEADER_FONT.render(title_text, 1, border_color)
    sub = MESSAGE_FONT.render(sub_text, 1, WHITE)
    
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, card_y + 50))
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, card_y + 135))
    
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()


async def handle_collision(player_car, computer_car, game_info, spark_particles, state_bag):
    # Border collision check
    border_poi = player_car.collide(TRACK_BORDER_MASK)
    if border_poi is not None:
        # Spawn scraping spark particles at impact point
        col_x = player_car.x + border_poi[0]
        col_y = player_car.y + border_poi[1]
        for _ in range(12):
            spark_particles.append(SparkParticle(col_x, col_y, (255, 120, 0))) # Orange sparks
        
        # Shake screen!
        state_bag["shake_duration"] = 10
        state_bag["shake_amount"] = 5
        
        player_car.bounce()

    # Opponent vehicle collision check
    car_rect_player = pygame.Rect(player_car.x, player_car.y, player_car.img.get_width(), player_car.img.get_height())
    car_rect_comp = pygame.Rect(computer_car.x, computer_car.y, computer_car.img.get_width(), computer_car.img.get_height())
    if car_rect_player.colliderect(car_rect_comp):
        # Sparks at middle boundary
        for _ in range(8):
            spark_particles.append(SparkParticle((player_car.x + computer_car.x)//2 + 20, (player_car.y + computer_car.y)//2 + 20, GOLD))
        state_bag["shake_duration"] = 12
        state_bag["shake_amount"] = 6
        player_car.bounce()
        computer_car.reset()
        computer_car.current_point = 0

    # Computer vehicle cross finish line
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide is not None:
        state_bag["shake_duration"] = 25
        state_bag["shake_amount"] = 10
        
        if game_info.score > 0 and arcade_api:
            arcade_api.submit_score("Car Racing", game_info.score)
            
        draw_game_overlay(WIN, "LAP FAILED", f"COMPUTER WON. FINAL SCORE: {game_info.score}. RESETTING...", NEON_PINK)
        await asyncio.sleep(4)
        
        game_info.reset()
        player_car.reset()
        computer_car.reset()
        computer_car.current_point = 0

    # Player vehicle cross finish line
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide is not None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            state_bag["shake_duration"] = 20
            state_bag["shake_amount"] = 8
            
            # Calculate lap score
            time_taken = time.time() - game_info.level_start_time
            time_bonus = max(0, 1000 - int(time_taken) * 15)
            lap_score = 1000 + time_bonus
            game_info.score += lap_score
            
            if game_info.level == game_info.LEVELS:
                # Victory bonus
                game_info.score += 5000
                if arcade_api:
                    arcade_api.submit_score("Car Racing", game_info.score)
                draw_game_overlay(WIN, "GRAND PRIX CHAMPION", f"YOU WON THE CUP! FINAL SCORE: {game_info.score}", GOLD)
                await asyncio.sleep(5)
                game_info.reset()
            else:
                draw_game_overlay(WIN, "LAP COMPLETE!", f"LAP SCORE: +{lap_score} | LEVEL {game_info.level} CLEARED...", NEON_GREEN)
                await asyncio.sleep(3)
                game_info.next_level()
                
            player_car.reset()
            computer_car.next_level(game_info.level)


async def main():
    run = True
    clock = pygame.time.Clock()
    images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
    player_car = PlayerCar(4.5, 4.2)
    computer_car = ComputerCar(2.4, 4.2, PATH)
    game_info = GameInfo()

    # Particle registers
    smoke_particles = []
    spark_particles = []

    # Dictionary to share mutable screen shake state across async functions
    state_bag = {
        "shake_duration": 0,
        "shake_amount": 0
    }

    # Game Loop
    while run:
        clock.tick(FPS)

        # Update smoke particles
        for p in smoke_particles[:]:
            p.update()
            if p.life <= 0:
                smoke_particles.remove(p)

        # Update spark particles
        for p in spark_particles[:]:
            p.update()
            if p.life <= 0:
                spark_particles.remove(p)

        # Draw default scene to monitor
        draw(WIN, images, player_car, computer_car, game_info, smoke_particles, spark_particles)

        # Ready state before lap start
        while not game_info.started:
            # Draw track and cars under card
            draw(WIN, images, player_car, computer_car, game_info, smoke_particles, spark_particles)
            draw_game_overlay(WIN, f"LEVEL {game_info.level} READY", "PRESS ANY KEY TO ACCELERATE AND START!", NEON_BLUE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    game_info.start_level()
            await asyncio.sleep(0)

        # Active playing state events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # Move cars
        move_player(player_car)
        computer_car.move()

        # Emit rear smoke trails
        if abs(player_car.vel) > 0.5:
            player_car.emit_trail(smoke_particles, (150, 150, 160, 140))
        if abs(computer_car.vel) > 0.5:
            computer_car.emit_trail(smoke_particles, (100, 180, 120, 140))

        # Check collisions
        await handle_collision(player_car, computer_car, game_info, spark_particles, state_bag)

        # Handle screen shake rendering
        if state_bag["shake_duration"] > 0:
            offset_x = random.randint(-state_bag["shake_amount"], state_bag["shake_amount"])
            offset_y = random.randint(-state_bag["shake_amount"], state_bag["shake_amount"])
            state_bag["shake_duration"] -= 1
        else:
            offset_x = 0
            offset_y = 0

        # Apply screen shake offset
        if offset_x != 0 or offset_y != 0:
            shaken_surface = pygame.Surface((WIDTH, HEIGHT))
            # Re-draw scene on offset surface
            draw(shaken_surface, images, player_car, computer_car, game_info, smoke_particles, spark_particles)
            WIN.fill((0, 0, 0))
            WIN.blit(shaken_surface, (offset_x, offset_y))
            pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())