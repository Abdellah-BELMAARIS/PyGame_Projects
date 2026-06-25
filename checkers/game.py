import pygame
import random
from constants import RED, WHITE, BLUE, SQUARE_SIZE, GOLD
from board import Board

class CaptureSpark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4.0, 4.0)
        self.vy = random.uniform(-4.0, 4.0)
        self.life = random.randint(15, 26)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # Gravity drag
        self.life -= 1

    def draw(self, surface):
        radius = int((self.life / self.max_life) * 4) + 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def update(self):
        # 1. Draw Board and Pieces
        self.board.draw(self.win)
        
        # 2. Pulsing Highlight on selected piece
        if self.selected:
            # Generate breathing pulse value
            t = pygame.time.get_ticks()
            pulse = 12 + int(math.sin(t * 0.015) * 3)
            # Pulse ring
            pygame.draw.circle(self.win, (180, 0, 255), (self.selected.x, self.selected.y), SQUARE_SIZE // 2 - pulse, width=3)

        # 3. Draw glowing valid move indicator targets
        self.draw_valid_moves(self.valid_moves)

        # 4. Draw Capture particles
        for p in self.particles:
            p.draw(self.win)

        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        
        # visual effects registers
        self.particles = []
        self.shake_duration = 0
        self.shake_amount = 0

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            # Move the piece, check if it was crowned king
            crowned = self.board.move(self.selected, row, col)
            
            # Check for captures (skipped pieces)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
                
                # Emit capture particles at the positions of all captured pieces
                for captured_piece in skipped:
                    center_x = SQUARE_SIZE * captured_piece.col + SQUARE_SIZE // 2
                    center_y = SQUARE_SIZE * captured_piece.row + SQUARE_SIZE // 2
                    
                    # Spawn colorful explosion sparks matching the captured piece's team color
                    for _ in range(15):
                        self.particles.append(CaptureSpark(center_x, center_y, captured_piece.color))
                
                # Trigger screen shake on capture!
                self.shake_duration = 10
                self.shake_amount = 6
            elif crowned:
                # Crowning king effects!
                center_x = SQUARE_SIZE * col + SQUARE_SIZE // 2
                center_y = SQUARE_SIZE * row + SQUARE_SIZE // 2
                for _ in range(18):
                    self.particles.append(CaptureSpark(center_x, center_y, GOLD))
                self.shake_duration = 12
                self.shake_amount = 7
            else:
                # Subtle shake on a standard move slide
                self.shake_duration = 4
                self.shake_amount = 2

            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            # Glowing mint-green rings for moves
            pygame.draw.circle(self.win, BLUE, (center_x, center_y), 10, width=2)
            # Center soft core
            pygame.draw.circle(self.win, (BLUE[0], BLUE[1], BLUE[2]), (center_x, center_y), 4)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

# Helper import inside game.py for pulse math
import math
