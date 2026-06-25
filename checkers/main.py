import pygame
import asyncio
import random
from constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE, GOLD
from game import Game

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Neon Checkers - Arcade Edition')

# Fonts
try:
    FONT_OVERLAY = pygame.font.SysFont("Outfit", 55, bold=True)
    FONT_OVERLAY_SUB = pygame.font.SysFont("Outfit", 22, bold=True)
except:
    try:
        FONT_OVERLAY = pygame.font.SysFont("Segoe UI", 55, bold=True)
        FONT_OVERLAY_SUB = pygame.font.SysFont("Segoe UI", 22, bold=True)
    except:
        FONT_OVERLAY = pygame.font.Font(None, 55)
        FONT_OVERLAY_SUB = pygame.font.Font(None, 22)

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_victory_overlay(win, winner_color):
    # Dim background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (5, 5, 12, 215), (0, 0, WIDTH, HEIGHT))
    win.blit(overlay, (0, 0))

    # Glow card
    card_w, card_h = 520, 240
    card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
    
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (15, 15, 32, 230), (0, 0, card_w, card_h), border_radius=15)
    win.blit(card_surf, (card_x, card_y))
    pygame.draw.rect(win, winner_color, (card_x, card_y, card_w, card_h), 3, border_radius=15)

    winner_name = "PINK PLAYER" if winner_color == RED else "CYAN PLAYER"
    title_text = f"{winner_name} WINS!"
    
    title = FONT_OVERLAY.render(title_text, 1, winner_color)
    sub = FONT_OVERLAY_SUB.render("REBOOTING COMBAT GRID...", 1, (255, 255, 255))

    win.blit(title, (WIDTH // 2 - title.get_width() // 2, card_y + 55))
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, card_y + 140))
    pygame.display.update()

async def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        # Update particles
        for p in game.particles[:]:
            p.update()
            if p.life <= 0:
                game.particles.remove(p)

        # Check Winner
        winner = game.winner()
        if winner is not None:
            # Trigger final victory overlay and restart
            draw_victory_overlay(WIN, winner)
            await asyncio.sleep(4.5)
            game.reset()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        # Render Game with Screen Shake Offset
        if game.shake_duration > 0:
            offset_x = random.randint(-game.shake_amount, game.shake_amount)
            offset_y = random.randint(-game.shake_amount, game.shake_amount)
            game.shake_duration -= 1
        else:
            offset_x = 0
            offset_y = 0

        if offset_x != 0 or offset_y != 0:
            shaken_surface = pygame.Surface((WIDTH, HEIGHT))
            # Draw game state onto shaken surface
            game.board.draw(shaken_surface)
            game.draw_valid_moves(game.valid_moves)
            # Pulsing Highlight on selected piece
            if game.selected:
                import math
                t = pygame.time.get_ticks()
                pulse = 12 + int(math.sin(t * 0.015) * 3)
                pygame.draw.circle(shaken_surface, (180, 0, 255), (game.selected.x, game.selected.y), SQUARE_SIZE // 2 - pulse, width=3)
            
            # Draw particles
            for p in game.particles:
                p.draw(shaken_surface)
                
            WIN.fill((8, 8, 16))
            WIN.blit(shaken_surface, (offset_x, offset_y))
            pygame.display.update()
        else:
            game.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
