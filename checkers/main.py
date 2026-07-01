import pygame
import asyncio
import random
import sys
from constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE, GOLD, ROWS, COLS
from game import Game

try:
    import arcade_api
except ImportError:
    sys.path.append("..")
    try:
        import arcade_api
    except:
        arcade_api = None

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Neon Checkers - Arcade Edition')

# Fonts
try:
    FONT_OVERLAY = pygame.font.SysFont("Outfit", 45, bold=True)
    FONT_OVERLAY_SUB = pygame.font.SysFont("Outfit", 22, bold=True)
except:
    try:
        FONT_OVERLAY = pygame.font.SysFont("Segoe UI", 45, bold=True)
        FONT_OVERLAY_SUB = pygame.font.SysFont("Segoe UI", 22, bold=True)
    except:
        FONT_OVERLAY = pygame.font.Font(None, 45)
        FONT_OVERLAY_SUB = pygame.font.Font(None, 22)

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_victory_overlay(win, winner_color, game_won=False, level=1, score=0):
    # Dim background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (5, 5, 12, 215), (0, 0, WIDTH, HEIGHT))
    win.blit(overlay, (0, 0))

    # Glow card
    card_w, card_h = 560, 240
    card_x, card_y = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
    
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (15, 15, 32, 230), (0, 0, card_w, card_h), border_radius=15)
    win.blit(card_surf, (card_x, card_y))
    
    if winner_color == RED:
        pygame.draw.rect(win, RED, (card_x, card_y, card_w, card_h), 3, border_radius=15)
        if game_won:
            title = FONT_OVERLAY.render(f"GRID CHAMPION! SCORE: {score}", 1, GOLD)
            sub = FONT_OVERLAY_SUB.render("PRESS R TO REBOOT COMBAT GRID", 1, (255, 255, 255))
        else:
            title = FONT_OVERLAY.render(f"STAGE {level} CLEARED!", 1, RED)
            sub = FONT_OVERLAY_SUB.render("PREPARING NEXT GRID SECTOR...", 1, (255, 255, 255))
    else:
        pygame.draw.rect(win, WHITE, (card_x, card_y, card_w, card_h), 3, border_radius=15)
        title = FONT_OVERLAY.render("SYSTEM DEFEAT", 1, WHITE)
        sub = FONT_OVERLAY_SUB.render("PRESS R TO REBOOT MATRIX", 1, (255, 255, 255))

    win.blit(title, (WIDTH // 2 - title.get_width() // 2, card_y + 55))
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, card_y + 140))
    pygame.display.update()

async def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)
    
    level = 1
    max_levels = 20
    score = 0
    score_submitted = False
    
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
            if winner == RED: # Player won
                score += 1000 + game.board.red_left * 100
                if level >= max_levels:
                    # Grand Victory!
                    if not score_submitted:
                        score_submitted = True
                        if arcade_api:
                            arcade_api.submit_score("Checkers", score)
                    draw_victory_overlay(WIN, RED, game_won=True, level=level, score=score)
                    
                    # Wait for restart key
                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                run = False
                                waiting = False
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                                level = 1
                                score = 0
                                score_submitted = False
                                game.reset()
                                waiting = False
                        await asyncio.sleep(0.02)
                    continue
                else:
                    # Level transition
                    draw_victory_overlay(WIN, RED, game_won=False, level=level)
                    await asyncio.sleep(2.5)
                    level += 1
                    game.reset()
                    continue
            else: # CPU won
                if not score_submitted:
                    score_submitted = True
                    if arcade_api:
                        arcade_api.submit_score("Checkers", score)
                draw_victory_overlay(WIN, WHITE, level=level)
                
                # Wait for restart key
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                            waiting = False
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            level = 1
                            score = 0
                            score_submitted = False
                            game.reset()
                            waiting = False
                    await asyncio.sleep(0.02)
                continue

        # CPU Turn Logic
        if game.turn == WHITE and not winner:
            await asyncio.sleep(0.7) # natural CPU delay
            
            # Find all available white moves
            all_moves = []
            capture_moves = []
            
            for row in range(ROWS):
                for col in range(COLS):
                    piece = game.board.get_piece(row, col)
                    if piece != 0 and piece.color == WHITE:
                        valid = game.board.get_valid_moves(piece)
                        for move, skipped in valid.items():
                            move_data = (piece, move[0], move[1], skipped)
                            all_moves.append(move_data)
                            if skipped:
                                capture_moves.append(move_data)
                                
            available_moves = capture_moves if capture_moves else all_moves
            
            if available_moves:
                # CPU difficulty / strategy scales with level
                # At higher levels, CPU always makes optimal choices
                ai_optimal = random.random() < (0.2 + level * 0.04)
                
                if ai_optimal:
                    def score_move(mv):
                        piece, r, c, skipped = mv
                        sc = len(skipped) * 25
                        if r == ROWS - 1 and not piece.king:
                            sc += 8
                        if 2 <= c <= 5:
                            sc += 2
                        return sc
                    available_moves.sort(key=score_move, reverse=True)
                    best_score = score_move(available_moves[0])
                    best_choices = [m for m in available_moves if score_move(m) == best_score]
                    selected = random.choice(best_choices)
                else:
                    selected = random.choice(available_moves)
                    
                # Perform AI move
                piece, r, c, skipped = selected
                game.selected = piece
                game.valid_moves = game.board.get_valid_moves(piece)
                game._move(r, c)
                game.selected = None
                game.valid_moves = {}
            else:
                # No moves left for WHITE, player RED wins!
                # Wait next frame to let winner check pick it up (handled by self.board.winner checks or forced RED victory)
                # Force RED victory
                game.board.white_left = 0
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and game.turn == RED:
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
            game.board.draw(shaken_surface)
            game.draw_valid_moves(game.valid_moves)
            if game.selected:
                import math
                t = pygame.time.get_ticks()
                pulse = 12 + int(math.sin(t * 0.015) * 3)
                pygame.draw.circle(shaken_surface, (180, 0, 255), (game.selected.x, game.selected.y), SQUARE_SIZE // 2 - pulse, width=3)
            for p in game.particles:
                p.draw(shaken_surface)
                
            # Draw HUD overlay
            level_lbl = FONT_OVERLAY_SUB.render(f"STAGE {level}/20", True, GOLD)
            score_lbl = FONT_OVERLAY_SUB.render(f"SCORE {score}", True, WHITE)
            shaken_surface.blit(level_lbl, (15, 15))
            shaken_surface.blit(score_lbl, (WIDTH - score_lbl.get_width() - 15, 15))

            WIN.fill((8, 8, 16))
            WIN.blit(shaken_surface, (offset_x, offset_y))
            pygame.display.update()
        else:
            # Standard draw with HUD overlay
            game.board.draw(WIN)
            if game.selected:
                import math
                t = pygame.time.get_ticks()
                pulse = 12 + int(math.sin(t * 0.015) * 3)
                pygame.draw.circle(WIN, (180, 0, 255), (game.selected.x, game.selected.y), SQUARE_SIZE // 2 - pulse, width=3)
            game.draw_valid_moves(game.valid_moves)
            for p in game.particles:
                p.draw(WIN)
                
            # Draw HUD overlay
            level_lbl = FONT_OVERLAY_SUB.render(f"STAGE {level}/20", True, GOLD)
            score_lbl = FONT_OVERLAY_SUB.render(f"SCORE {score}", True, WHITE)
            WIN.blit(level_lbl, (15, 15))
            WIN.blit(score_lbl, (WIDTH - score_lbl.get_width() - 15, 15))
            pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
