from constants import RED, WHITE, SQUARE_SIZE, GREY, CROWN
import pygame

class Piece:
    PADDING = 15
    OUTLINE = 3

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        
        # 1. Outer breathing glow ring (Semi-transparent)
        glow_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 45), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), radius + 6)
        win.blit(glow_surf, (self.x - SQUARE_SIZE // 2, self.y - SQUARE_SIZE // 2))

        # 2. Main rim outline
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        
        # 3. Solid piece core
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        
        # 4. Glossy center highlight circle
        highlight_color = (min(255, self.color[0] + 70), min(255, self.color[1] + 70), min(255, self.color[2] + 70))
        pygame.draw.circle(win, highlight_color, (self.x, self.y), radius - 6, 2)
        pygame.draw.circle(win, (255, 255, 255), (self.x - 6, self.y - 6), 3) # glare spot

        # 5. King emblem
        if self.king:
            if CROWN:
                win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))
            else:
                # Fallback: Pulsing gold crown emblem
                pygame.draw.circle(win, (255, 215, 0), (self.x, self.y), radius // 2)
                pygame.draw.circle(win, (255, 255, 255), (self.x, self.y), radius // 4)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)
