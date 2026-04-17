import pygame
from config import (
    BG_COLOR, BLACK, BASE_WIDTH, BASE_HEIGHT,
    TITLE_FONT_SIZE, TEAM_FONT_SIZE
)
from components.button import draw_filled_button
from components.board_view import draw_home_board
from components.setting_icon import draw_gear_icon

class HomePage:
    def __init__(self, screen):
        self.screen = screen
        self.btn_1player = None
        self.btn_2players = None
        self.btn_rules = None
        self.btn_quit = None

    def sx(self, x):
        return int(x * self.screen.get_width() / BASE_WIDTH)

    def sy(self, y):
        return int(y * self.screen.get_height() / BASE_HEIGHT)

    def sf(self, size):
        scale_w = self.screen.get_width() / BASE_WIDTH
        scale_h = self.screen.get_height() / BASE_HEIGHT
        return max(16, int(size * min(scale_w, scale_h)))

    def draw_title(self):
        font = pygame.font.SysFont("timesnewroman", self.sf(TITLE_FONT_SIZE), bold=True)
        title = font.render("CONNECT 4", True, BLACK)
        self.screen.blit(title, (self.sx(500), self.sy(40)))

    def draw_buttons(self):
        self.btn_1player = draw_filled_button(
            self.screen, self.sx(123), self.sy(270), self.sx(343), self.sy(103), "1 PLAYER", self.sf(42)
        )
        self.btn_2players = draw_filled_button(
            self.screen, self.sx(123), self.sy(408), self.sx(343), self.sy(103), "2 PLAYERS", self.sf(42)
        )
        self.btn_rules = draw_filled_button(
            self.screen, self.sx(123), self.sy(565), self.sx(343), self.sy(103), "RULES", self.sf(42)
        )
        self.btn_quit = draw_filled_button(
            self.screen, self.sx(123), self.sy(715), self.sx(343), self.sy(103), "QUIT", self.sf(42)
        )

    def draw_team_name(self):
        font = pygame.font.SysFont("timesnewroman", self.sf(TEAM_FONT_SIZE), bold=True)
        team_text = font.render("TEAM 5", True, BLACK)
        self.screen.blit(team_text, (self.sx(1160), self.sy(930)))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_title()
        self.draw_buttons()
        draw_home_board(self.screen, self.sx, self.sy)
        draw_gear_icon(self.screen, self.sx(98), self.sy(929), max(28, self.sx(58)), max(12, self.sx(24)))
        self.draw_team_name()

    def handle_click(self, mouse_pos):
        if self.btn_1player and self.btn_1player.collidepoint(mouse_pos):
            return "mode_select"
        if self.btn_2players and self.btn_2players.collidepoint(mouse_pos):
            return "2players"
        if self.btn_rules and self.btn_rules.collidepoint(mouse_pos):
            return "rules"
        if self.btn_quit and self.btn_quit.collidepoint(mouse_pos):
            return "quit"
        return None