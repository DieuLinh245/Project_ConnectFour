from __future__ import annotations

from dataclasses import dataclass

import pygame

from core.AI import AI_DIFFICULTY_SETTINGS, get_ai_move
from core.board import COLS, ROWS, board_full, create_board, drop_piece, get_next_open_row, is_valid_column


REFERENCE_SCREEN_WIDTH = 734
REFERENCE_SCREEN_HEIGHT = 680
REFERENCE_CELL_SIZE = 74
REFERENCE_BOARD_PADDING = 16
REFERENCE_SIDE_GUTTER = 92
REFERENCE_TOP_PANEL_HEIGHT = 92
REFERENCE_BOTTOM_PANEL_HEIGHT = 112

HUMAN_PLAYER = 1
AI_PLAYER = 2
EMPTY = 0

AI_THINK_DELAY_MS = 300
TURN_TIME_SECONDS = 120

BACKGROUND = (249, 249, 247)
PANEL = (255, 255, 255)
TEXT = (30, 31, 36)
SUBTEXT = (108, 114, 132)
BOARD_COLOR = (191, 53, 141)
BOARD_SHADOW = (227, 197, 216)
HOLE_COLOR = (250, 249, 246)
HUMAN_COLOR = (163, 188, 238)
AI_COLOR = (250, 234, 108)
ACCENT = (38, 42, 59)
BUTTON_LIGHT = (232, 238, 255)
WARNING = (200, 93, 93)
SUCCESS = (64, 148, 97)
WIN_HIGHLIGHT = (255, 255, 255)
TIMER_BG = (13, 13, 15)
TIMER_TEXT = (255, 255, 255)
FRAME_BORDER = (70, 95, 140)
DIALOG_OVERLAY = (16, 18, 24, 138)
DIALOG_BG = (255, 255, 255)
DIALOG_SHADOW = (214, 220, 231)
CANCEL_FILL = (244, 245, 248)


@dataclass(frozen=True)
class DifficultyConfig:
    label: str
    depth: int
    description: str


DIFFICULTIES = {
    "easy": DifficultyConfig("Easy", AI_DIFFICULTY_SETTINGS["easy"]["depth"], "Depth 2 + thinh thoang random"),
    "medium": DifficultyConfig("Medium", AI_DIFFICULTY_SETTINGS["medium"]["depth"], "Depth 4 + random it hon"),
    "hard": DifficultyConfig("Hard", AI_DIFFICULTY_SETTINGS["hard"]["depth"], "Depth 5 + khong random"),
}


class GamePage:
    def __init__(self, screen, difficulty="easy"):
        self.screen = screen
        self.difficulty = difficulty
        self.game_mode = "ai"
        self.btn_exit = None
        self.btn_restart = None
        self.reset(difficulty)

    def reset(self, difficulty=None, game_mode=None):
        if difficulty is not None:
            self.difficulty = difficulty
        if game_mode is not None:
            self.game_mode = game_mode

        self.board = create_board()
        self.current_player = HUMAN_PLAYER
        self.game_over = False
        self.winner = EMPTY
        self.winner_text = ""
        self.winning_line = None
        self.end_reason = "active"
        self.ai_turn_started_at = None
        self.human_time_left = float(TURN_TIME_SECONDS)
        self.ai_time_left = float(TURN_TIME_SECONDS)
        self.last_tick_ms = pygame.time.get_ticks()
        self.show_reset_confirmation = False

    def draw(self):
        self._update_runtime_state()

        layout = self._compute_layout()
        mouse_pos = pygame.mouse.get_pos()
        hovered_column = self._get_hovered_column(mouse_pos, layout)

        self.screen.fill(BACKGROUND)
        self._draw_background(layout)
        self._draw_top_buttons(layout, mouse_pos)
        self._draw_side_panels(layout)
        self._draw_preview_disc(layout, hovered_column)
        self._draw_board(layout)
        self._draw_turn_panel(layout)
        if self.show_reset_confirmation:
            self._draw_reset_confirmation(layout, mouse_pos)

    def handle_click(self, mouse_pos):
        layout = self._compute_layout()

        if self.show_reset_confirmation:
            dialog_rects = self._get_reset_dialog_rects(layout)
            if dialog_rects["confirm_button"].collidepoint(mouse_pos):
                self.reset()
            elif dialog_rects["cancel_button"].collidepoint(mouse_pos):
                self._close_reset_confirmation()
            return None

        if layout["home_button"].collidepoint(mouse_pos):
            self.ai_turn_started_at = None
            return "home"

        if layout["restart_button"].collidepoint(mouse_pos):
            self._open_reset_confirmation()
            return None

        if self.game_over or self._is_ai_turn():
            return None

        column = self._get_hovered_column(mouse_pos, layout)
        if column is not None:
            self._apply_move(column, self.current_player)

        return None

    def _update_runtime_state(self):
        now = pygame.time.get_ticks()
        elapsed = (now - self.last_tick_ms) / 1000 if self.last_tick_ms is not None else 0
        self.last_tick_ms = now

        if self.show_reset_confirmation:
            return

        if self.game_over:
            return

        if self.current_player == HUMAN_PLAYER:
            self.human_time_left = max(0.0, self.human_time_left - elapsed)
            if self.human_time_left == 0:
                self.game_over = True
                self.winner = self._other_player(HUMAN_PLAYER)
                self.winner_text = "TIME OUT"
                self.end_reason = "timeout"
                return
        else:
            self.ai_time_left = max(0.0, self.ai_time_left - elapsed)
            if self.ai_time_left == 0:
                self.game_over = True
                self.winner = self._other_player(AI_PLAYER)
                self.winner_text = "TIME OUT"
                self.end_reason = "timeout"
                return

        if not self._is_ai_turn():
            return

        if self.ai_turn_started_at is None:
            self.ai_turn_started_at = now
            return

        if now - self.ai_turn_started_at < AI_THINK_DELAY_MS:
            return

        column = get_ai_move(self.board, self.difficulty)
        if column is not None:
            self._apply_move(column, AI_PLAYER)
        self.ai_turn_started_at = None

    def _open_reset_confirmation(self):
        self.show_reset_confirmation = True
        if self._is_ai_turn():
            self.ai_turn_started_at = pygame.time.get_ticks()

    def _close_reset_confirmation(self):
        self.show_reset_confirmation = False
        self.last_tick_ms = pygame.time.get_ticks()
        if self._is_ai_turn():
            self.ai_turn_started_at = self.last_tick_ms

    def _apply_move(self, column, piece):
        if not is_valid_column(self.board, column):
            return

        row = get_next_open_row(self.board, column)
        if row is None:
            return

        drop_piece(self.board, row, column, piece)

        winning_line = self._find_winning_line(piece)
        if winning_line:
            self.game_over = True
            self.winning_line = winning_line
            self.winner = piece
            self.end_reason = "connect4"
            self.winner_text = self._winner_text_for(piece)
            return

        if board_full(self.board):
            self.game_over = True
            self.winner = EMPTY
            self.winning_line = None
            self.end_reason = "draw"
            self.winner_text = "DRAW!"
            return

        self.current_player = self._other_player(piece)
        if self._is_ai_turn():
            self.ai_turn_started_at = pygame.time.get_ticks()
        else:
            self.ai_turn_started_at = None

    def _find_winning_line(self, player):
        for row in range(ROWS):
            for col in range(COLS - 3):
                coords = [(row, col + offset) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        for row in range(ROWS - 3):
            for col in range(COLS):
                coords = [(row + offset, col) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                coords = [(row + offset, col + offset) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        for row in range(3, ROWS):
            for col in range(COLS - 3):
                coords = [(row - offset, col + offset) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        return None

    def _compute_layout(self):
        screen_width, screen_height = self.screen.get_size()
        scale = min(
            (screen_width - 24) / REFERENCE_SCREEN_WIDTH,
            (screen_height - 24) / REFERENCE_SCREEN_HEIGHT,
        )
        scale = max(0.68, min(scale, 1.55))

        cell_size = max(52, int(REFERENCE_CELL_SIZE * scale))
        board_padding = max(10, int(REFERENCE_BOARD_PADDING * scale))
        side_gutter = max(70, int(REFERENCE_SIDE_GUTTER * scale))
        top_panel_height = max(72, int(REFERENCE_TOP_PANEL_HEIGHT * scale))
        bottom_panel_height = max(86, int(REFERENCE_BOTTOM_PANEL_HEIGHT * scale))
        icon_size = max(36, int(40 * scale))
        icon_gap = max(8, int(8 * scale))

        board_width = COLS * cell_size
        board_height = ROWS * cell_size
        board_frame_width = board_width + (board_padding * 2)
        board_frame_height = board_height + (board_padding * 2)

        total_content_height = top_panel_height + board_frame_height + bottom_panel_height
        content_top = max(0, (screen_height - total_content_height) // 2)
        board_x = max(20, (screen_width - board_frame_width) // 2)
        board_y = content_top + top_panel_height
        board_frame = pygame.Rect(board_x, board_y, board_frame_width, board_frame_height)

        icon_y = content_top + max(6, int(18 * scale))
        home_button = pygame.Rect(
            (screen_width // 2) - icon_size - (icon_gap // 2),
            icon_y,
            icon_size,
            icon_size,
        )
        restart_button = pygame.Rect(
            (screen_width // 2) + (icon_gap // 2),
            icon_y,
            icon_size,
            icon_size,
        )

        marker_y = board_frame.centery - max(18, int(40 * scale))
        marker_offset = max(28, side_gutter // 2)
        human_marker_center = (board_frame.left - marker_offset, marker_y)
        ai_marker_center = (board_frame.right + marker_offset, marker_y)

        timer_width = max(84, int(88 * scale))
        timer_height = max(40, int(48 * scale))
        timer_y = min(
            screen_height - timer_height - max(10, int(12 * scale)),
            board_frame.bottom - timer_height + max(14, int(18 * scale)),
        )
        human_timer = pygame.Rect(
            human_marker_center[0] - (timer_width // 2),
            timer_y,
            timer_width,
            timer_height,
        )
        ai_timer = pygame.Rect(
            ai_marker_center[0] - (timer_width // 2),
            timer_y,
            timer_width,
            timer_height,
        )

        turn_panel_width = max(180, int(188 * scale))
        turn_panel_height = max(46, int(52 * scale))
        turn_panel = pygame.Rect(
            (screen_width - turn_panel_width) // 2,
            board_frame.bottom + max(18, int(18 * scale)),
            turn_panel_width,
            turn_panel_height,
        )

        preview_y = board_frame.top - max(18, int(22 * scale))
        margin = max(6, int(10 * scale))
        outer_frame = pygame.Rect(
            margin,
            margin,
            screen_width - (margin * 2),
            screen_height - (margin * 2),
        )

        return {
            "scale": scale,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "cell_size": cell_size,
            "board_padding": board_padding,
            "board_frame": board_frame,
            "cell_origin": (board_frame.left + board_padding, board_frame.top + board_padding),
            "home_button": home_button,
            "restart_button": restart_button,
            "human_marker_center": human_marker_center,
            "ai_marker_center": ai_marker_center,
            "human_timer": human_timer,
            "ai_timer": ai_timer,
            "turn_panel": turn_panel,
            "preview_y": preview_y,
            "outer_frame": outer_frame,
        }

    def _get_hovered_column(self, mouse_pos, layout):
        origin_x, origin_y = layout["cell_origin"]
        x, y = mouse_pos
        board_width = COLS * layout["cell_size"]
        board_height = ROWS * layout["cell_size"]

        if not (origin_x <= x <= origin_x + board_width):
            return None
        if not (layout["preview_y"] - layout["cell_size"] <= y <= origin_y + board_height):
            return None

        column = (x - origin_x) // layout["cell_size"]
        if not is_valid_column(self.board, column):
            return None
        return column

    def _draw_background(self, layout):
        pygame.draw.rect(self.screen, PANEL, layout["outer_frame"], border_radius=max(16, int(12 * layout["scale"])))
        pygame.draw.rect(
            self.screen,
            FRAME_BORDER,
            layout["outer_frame"],
            width=max(2, int(2 * layout["scale"])),
            border_radius=max(16, int(12 * layout["scale"])),
        )

    def _draw_top_buttons(self, layout, mouse_pos):
        self.btn_exit = layout["home_button"]
        self.btn_restart = layout["restart_button"]

        self._draw_icon_button(layout["home_button"], mouse_pos, "home")
        self._draw_icon_button(layout["restart_button"], mouse_pos, "restart")

    def _draw_icon_button(self, rect, mouse_pos, icon_name):
        hovered = rect.collidepoint(mouse_pos)
        fill = (244, 244, 240) if hovered else PANEL
        pygame.draw.ellipse(self.screen, fill, rect.inflate(10, 10))
        pygame.draw.ellipse(self.screen, ACCENT, rect.inflate(10, 10), 2)

        if icon_name == "home":
            self._draw_home_icon(rect.center, rect.width)
        else:
            self._draw_restart_icon(rect.center, rect.width)

    def _draw_home_icon(self, center, icon_size):
        cx, cy = center
        roof_offset = max(8, icon_size // 3)
        body_width = max(14, icon_size // 2)
        body_height = max(12, icon_size // 2)
        door_width = max(4, icon_size // 8)
        door_height = max(7, icon_size // 5)

        roof = [(cx - roof_offset, cy + 2), (cx, cy - roof_offset), (cx + roof_offset, cy + 2)]
        base = pygame.Rect(cx - (body_width // 2), cy + 2, body_width, body_height)
        door = pygame.Rect(cx - (door_width // 2), cy + body_height // 4, door_width, door_height)

        pygame.draw.lines(self.screen, TEXT, False, roof, 3)
        pygame.draw.rect(self.screen, TEXT, base, 3)
        pygame.draw.rect(self.screen, TEXT, door, 2)

    def _draw_restart_icon(self, center, icon_size):
        cx, cy = center
        radius = max(9, icon_size // 3)
        width = max(2, icon_size // 11)
        pygame.draw.arc(
            self.screen,
            TEXT,
            (cx - radius, cy - radius, radius * 2, radius * 2),
            0.8,
            5.5,
            width,
        )
        arrow = [
            (cx + radius - 2, cy - radius + 2),
            (cx + radius + max(4, icon_size // 8), cy - radius + 4),
            (cx + radius - 1, cy - radius + max(8, icon_size // 5)),
        ]
        pygame.draw.polygon(self.screen, TEXT, arrow)

    def _draw_side_panels(self, layout):
        active_human = self.current_player == HUMAN_PLAYER and not self.game_over
        active_ai = self.current_player == AI_PLAYER and not self.game_over

        self._draw_player_marker(layout["human_marker_center"], HUMAN_COLOR, active_human, layout["scale"])
        self._draw_player_marker(layout["ai_marker_center"], AI_COLOR, active_ai, layout["scale"])
        self._draw_side_label(layout["human_marker_center"], self._left_player_label(), layout["scale"])
        self._draw_side_label(layout["ai_marker_center"], self._right_player_label(), layout["scale"])
        self._draw_timer_box(layout["human_timer"], self.human_time_left)
        self._draw_timer_box(layout["ai_timer"], self.ai_time_left)

    def _draw_player_marker(self, center, fill, active, scale):
        radius = max(28, int(34 * scale))
        outline = ACCENT if active else PANEL
        width = 4 if active else 2
        pygame.draw.circle(self.screen, fill, center, radius)
        pygame.draw.circle(self.screen, outline, center, radius, width)

    def _draw_side_label(self, center, label, scale):
        font = pygame.font.SysFont("consolas", max(13, int(16 * scale)), bold=True)
        text_surface = font.render(label, True, SUBTEXT)
        text_rect = text_surface.get_rect(center=(center[0], center[1] + max(48, int(50 * scale))))
        self.screen.blit(text_surface, text_rect)

    def _draw_timer_box(self, rect, seconds_left):
        pygame.draw.rect(self.screen, TIMER_BG, rect, border_radius=10)
        font = pygame.font.SysFont("consolas", max(18, int(rect.height * 0.45)), bold=True)
        time_surface = font.render(self._format_time(seconds_left), True, TIMER_TEXT)
        self.screen.blit(time_surface, time_surface.get_rect(center=rect.center))

    def _draw_preview_disc(self, layout, hovered_column):
        if self.game_over or hovered_column is None or self._is_ai_turn():
            return

        origin_x, _ = layout["cell_origin"]
        center_x = origin_x + (hovered_column * layout["cell_size"]) + (layout["cell_size"] // 2)
        radius = max(16, (layout["cell_size"] // 2) - max(8, int(10 * layout["scale"])))
        center = (center_x, layout["preview_y"])
        pygame.draw.circle(self.screen, self._color_for_player(self.current_player), center, radius)
        pygame.draw.circle(self.screen, ACCENT, center, radius, 2)

    def _draw_board(self, layout):
        shadow_rect = layout["board_frame"].move(0, max(4, int(6 * layout["scale"])))
        pygame.draw.rect(self.screen, BOARD_SHADOW, shadow_rect, border_radius=max(18, int(26 * layout["scale"])))
        pygame.draw.rect(self.screen, BOARD_COLOR, layout["board_frame"], border_radius=max(18, int(26 * layout["scale"])))

        highlighted = set(self.winning_line or [])
        radius = max(16, (layout["cell_size"] // 2) - max(8, int(10 * layout["scale"])))

        for row in range(ROWS):
            for col in range(COLS):
                center = self._get_cell_center(row, col, layout)
                piece = self.board[row][col]

                color = HOLE_COLOR
                if piece == HUMAN_PLAYER:
                    color = HUMAN_COLOR
                elif piece == AI_PLAYER:
                    color = AI_COLOR

                pygame.draw.circle(self.screen, color, center, radius)

                if (row, col) in highlighted:
                    pygame.draw.circle(self.screen, WIN_HIGHLIGHT, center, radius, 5)
                elif piece != EMPTY:
                    pygame.draw.circle(self.screen, ACCENT, center, radius, 2)

    def _draw_turn_panel(self, layout):
        difficulty = DIFFICULTIES.get(self.difficulty, DIFFICULTIES["medium"])

        turn_font = pygame.font.SysFont("georgia", max(16, int(18 * layout["scale"])), bold=True)
        small_font = pygame.font.SysFont("consolas", max(12, int(15 * layout["scale"])), bold=True)

        glow_color = self._get_turn_glow_color()
        panel_fill = self._get_turn_panel_fill_color()
        self._draw_panel_glow(layout["turn_panel"], glow_color, layout["scale"])

        pygame.draw.rect(self.screen, panel_fill, layout["turn_panel"], border_radius=10)
        pygame.draw.rect(
            self.screen,
            glow_color,
            layout["turn_panel"],
            width=max(2, int(2 * layout["scale"])),
            border_radius=10,
        )

        if self.game_over:
            if self.winner == HUMAN_PLAYER:
                label = "BLUE WINS"
            elif self.winner == AI_PLAYER:
                label = "YELLOW WINS"
            else:
                label = "DRAW"
        elif self.current_player == HUMAN_PLAYER:
            label = "BLUE'S TURN"
        else:
            label = "YELLOW'S TURN"

        label_surface = turn_font.render(label, True, TEXT)
        self.screen.blit(label_surface, label_surface.get_rect(center=layout["turn_panel"].center))

        if self.end_reason == "timeout":
            footer_label = "TIME OUT"
            footer_color = WARNING
        elif self.end_reason == "connect4":
            footer_label = "CONNECT 4"
            footer_color = SUCCESS if self.winner == HUMAN_PLAYER else WARNING
        elif self.end_reason == "draw":
            footer_label = "DRAW"
            footer_color = SUBTEXT
        elif self.game_mode == "pvp":
            footer_label = "2 PLAYERS"
            footer_color = SUBTEXT
        else:
            footer_label = f"DEPTH {difficulty.depth}"
            footer_color = SUBTEXT

        footer_surface = small_font.render(footer_label, True, footer_color)
        footer_y = min(
            layout["screen_height"] - max(18, int(24 * layout["scale"])),
            layout["turn_panel"].bottom + max(18, int(24 * layout["scale"])),
        )
        self.screen.blit(
            footer_surface,
            footer_surface.get_rect(center=(layout["screen_width"] // 2, footer_y)),
        )

    def _get_reset_dialog_rects(self, layout):
        dialog_width = max(300, int(340 * layout["scale"]))
        dialog_height = max(170, int(190 * layout["scale"]))
        dialog = pygame.Rect(
            (layout["screen_width"] - dialog_width) // 2,
            (layout["screen_height"] - dialog_height) // 2,
            dialog_width,
            dialog_height,
        )

        button_width = max(108, int(122 * layout["scale"]))
        button_height = max(42, int(46 * layout["scale"]))
        gap = max(10, int(14 * layout["scale"]))
        button_y = dialog.bottom - button_height - max(18, int(22 * layout["scale"]))
        cancel_button = pygame.Rect(
            dialog.centerx - gap - button_width,
            button_y,
            button_width,
            button_height,
        )
        confirm_button = pygame.Rect(
            dialog.centerx + gap,
            button_y,
            button_width,
            button_height,
        )

        return {
            "dialog": dialog,
            "cancel_button": cancel_button,
            "confirm_button": confirm_button,
        }

    def _draw_reset_confirmation(self, layout, mouse_pos):
        overlay = pygame.Surface((layout["screen_width"], layout["screen_height"]), pygame.SRCALPHA)
        overlay.fill(DIALOG_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        rects = self._get_reset_dialog_rects(layout)
        dialog = rects["dialog"]
        shadow = dialog.move(0, max(6, int(8 * layout["scale"])))

        pygame.draw.rect(self.screen, DIALOG_SHADOW, shadow, border_radius=18)
        pygame.draw.rect(self.screen, DIALOG_BG, dialog, border_radius=18)
        pygame.draw.rect(self.screen, FRAME_BORDER, dialog, width=2, border_radius=18)

        title_font = pygame.font.SysFont("georgia", max(20, int(24 * layout["scale"])), bold=True)
        body_font = pygame.font.SysFont("segoeui", max(15, int(17 * layout["scale"])))
        button_font = pygame.font.SysFont("segoeui", max(15, int(17 * layout["scale"])), bold=True)

        title_surface = title_font.render("Reset current match?", True, TEXT)
        body_surface = body_font.render("The current board will be cleared and timers restart.", True, SUBTEXT)
        self.screen.blit(title_surface, title_surface.get_rect(center=(dialog.centerx, dialog.top + max(34, int(40 * layout["scale"])))))
        self.screen.blit(body_surface, body_surface.get_rect(center=(dialog.centerx, dialog.top + max(74, int(84 * layout["scale"])))))

        self._draw_dialog_button(
            rects["cancel_button"],
            "Keep playing",
            mouse_pos,
            CANCEL_FILL,
            TEXT,
            layout["scale"],
            button_font,
        )
        self._draw_dialog_button(
            rects["confirm_button"],
            "Reset",
            mouse_pos,
            WARNING,
            PANEL,
            layout["scale"],
            button_font,
        )

    def _draw_dialog_button(self, rect, label, mouse_pos, fill, text_color, scale, font):
        hovered = rect.collidepoint(mouse_pos)
        draw_fill = self._tint_color(fill, 18) if hovered else fill
        pygame.draw.rect(self.screen, draw_fill, rect, border_radius=12)
        pygame.draw.rect(self.screen, ACCENT, rect, width=max(2, int(2 * scale)), border_radius=12)

        label_surface = font.render(label, True, text_color)
        self.screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    def _get_cell_center(self, row, col, layout):
        origin_x, origin_y = layout["cell_origin"]
        center_x = origin_x + (col * layout["cell_size"]) + (layout["cell_size"] // 2)
        center_y = origin_y + (row * layout["cell_size"]) + (layout["cell_size"] // 2)
        return center_x, center_y

    def _format_time(self, seconds_left):
        total_seconds = max(0, int(seconds_left))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def _get_turn_glow_color(self):
        if self.game_over:
            if self.winner == HUMAN_PLAYER:
                return HUMAN_COLOR
            if self.winner == AI_PLAYER:
                return AI_COLOR
            return SUBTEXT

        return self._color_for_player(self.current_player)

    def _get_turn_panel_fill_color(self):
        return self._get_turn_glow_color()

    def _draw_panel_glow(self, rect, color, scale):
        glow_size = max(12, int(18 * scale))
        glow_surface = pygame.Surface(
            (rect.width + glow_size * 2, rect.height + glow_size * 2),
            pygame.SRCALPHA,
        )

        layers = [
            (glow_size, 34),
            (max(8, int(glow_size * 0.72)), 54),
            (max(4, int(glow_size * 0.42)), 84),
        ]

        for inflate, alpha in layers:
            glow_rect = pygame.Rect(
                glow_size - inflate,
                glow_size - inflate,
                rect.width + inflate * 2,
                rect.height + inflate * 2,
            )
            pygame.draw.rect(
                glow_surface,
                (*color, alpha),
                glow_rect,
                border_radius=max(12, rect.height // 2),
            )

        self.screen.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))

    def _tint_color(self, color, amount):
        return tuple(min(255, channel + amount) for channel in color)

    def _other_player(self, player):
        return AI_PLAYER if player == HUMAN_PLAYER else HUMAN_PLAYER

    def _is_ai_turn(self):
        return self.game_mode == "ai" and self.current_player == AI_PLAYER and not self.game_over

    def _color_for_player(self, player):
        return HUMAN_COLOR if player == HUMAN_PLAYER else AI_COLOR

    def _left_player_label(self):
        return "YOU" if self.game_mode == "ai" else "P1"

    def _right_player_label(self):
        return "AI" if self.game_mode == "ai" else "P2"

    def _winner_text_for(self, player):
        if self.game_mode == "pvp":
            return "PLAYER 1 WINS!" if player == HUMAN_PLAYER else "PLAYER 2 WINS!"
        return "YOU WIN!" if player == HUMAN_PLAYER else "AI WIN!"
