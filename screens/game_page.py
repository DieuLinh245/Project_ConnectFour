import pygame
import random

from config import BG_COLOR, BLACK, PINK, WHITE, BLUE, YELLOW, BASE_WIDTH, BASE_HEIGHT
from core.board import create_board, is_valid_column, get_next_open_row, drop_piece, board_full, COLS, ROWS
from core.rule_checker import check_winner
from components.button import draw_filled_button
from core.AI import get_ai_move
class GamePage:
    def __init__(self, screen, difficulty="easy"):
        self.screen = screen
        self.difficulty = difficulty
        self.board = create_board()
        self.current_player = 1
        self.game_over = False
        self.winner_text = ""
        self.btn_exit = None

    def reset(self, difficulty=None):
        if difficulty is not None:
            self.difficulty = difficulty
        self.board = create_board()
        self.current_player = 1
        self.game_over = False
        self.winner_text = ""

    def sx(self, x):
        return int(x * self.screen.get_width() / BASE_WIDTH)

    def sy(self, y):
        return int(y * self.screen.get_height() / BASE_HEIGHT)

    def sf(self, size):
        scale_w = self.screen.get_width() / BASE_WIDTH
        scale_h = self.screen.get_height() / BASE_HEIGHT
        return max(16, int(size * min(scale_w, scale_h)))

    def draw_title(self):
        font = pygame.font.SysFont("timesnewroman", self.sf(60), bold=True)
        text = font.render("CONNECT 4", True, BLACK)
        rect = text.get_rect(center=(self.screen.get_width() // 2, self.sy(70)))
        self.screen.blit(text, rect)

    def draw_status(self):
        font = pygame.font.SysFont("arial", self.sf(28), bold=True)

        if self.game_over:
            text = self.winner_text
        else:
            text = "YOUR TURN" if self.current_player == 1 else "AI TURN"

        label = font.render(text, True, BLACK)
        rect = label.get_rect(center=(self.screen.get_width() // 2, self.sy(140)))
        self.screen.blit(label, rect)

    def draw_exit_button(self):
        self.btn_exit = draw_filled_button(
            self.screen,
            self.sx(70),
            self.sy(70),
            self.sx(180),
            self.sy(70),
            "EXIT",
            self.sf(30)
        )

    def draw_board(self):
        board_x = self.sx(380)
        board_y = self.sy(220)
        board_w = self.sx(680)
        board_h = self.sy(580)

        pygame.draw.rect(
            self.screen,
            PINK,
            (board_x, board_y, board_w, board_h),
            border_radius=max(20, board_w // 16)
        )

        cell_w = board_w / COLS
        cell_h = board_h / ROWS
        radius = max(12, min(board_w // 22, board_h // 16))

        for r in range(ROWS):
            for c in range(COLS):
                cx = int(board_x + c * cell_w + cell_w / 2)
                cy = int(board_y + r * cell_h + cell_h / 2)

                pygame.draw.circle(self.screen, WHITE, (cx, cy), radius)

                if self.board[r][c] == 1:
                    pygame.draw.circle(self.screen, BLUE, (cx, cy), radius)
                elif self.board[r][c] == 2:
                    pygame.draw.circle(self.screen, YELLOW, (cx, cy), radius)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_title()
        self.draw_status()
        self.draw_exit_button()
        self.draw_board()

    def get_clicked_column(self, mouse_pos):
        x, y = mouse_pos

        board_x = self.sx(380)
        board_y = self.sy(220)
        board_w = self.sx(680)
        board_h = self.sy(580)

        if not (board_x <= x <= board_x + board_w and board_y <= y <= board_y + board_h):
            return None

        cell_w = board_w / COLS
        col = int((x - board_x) // cell_w)
        return col

    def make_ai_move(self):
        if self.game_over:
            return

        col = get_ai_move(self.board, self.difficulty)
        if col is None:
            return

        if is_valid_column(self.board, col):
            row = get_next_open_row(self.board, col)
            if row is not None:
                drop_piece(self.board, row, col, 2)

                if check_winner(self.board, 2):
                    self.game_over = True
                    self.winner_text = "AI WIN!"
                elif board_full(self.board):
                    self.game_over = True
                    self.winner_text = "DRAW!"
                else:
                    self.current_player = 1

    def handle_click(self, mouse_pos):
        if self.btn_exit and self.btn_exit.collidepoint(mouse_pos):
            return "home"

        if self.game_over:
            return None

        if self.current_player != 1:
            return None

        col = self.get_clicked_column(mouse_pos)
        if col is None:
            return None

        if is_valid_column(self.board, col):
            row = get_next_open_row(self.board, col)
            if row is not None:
                drop_piece(self.board, row, col, 1)

                if check_winner(self.board, 1):
                    self.game_over = True
                    self.winner_text = "YOU WIN!"
                elif board_full(self.board):
                    self.game_over = True
                    self.winner_text = "DRAW!"
                else:
                    self.current_player = 2
                    self.make_ai_move()

        return None