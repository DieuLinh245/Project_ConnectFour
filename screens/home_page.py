import pygame

from config import BG_COLOR, BLACK, BASE_HEIGHT, BASE_WIDTH, TEAM_FONT_SIZE, TITLE_FONT_SIZE, WHITE
from components.board_view import draw_home_board
from components.button import draw_filled_button, draw_outline_button
from components.modal_elements import (
    draw_backdrop,
    draw_decorated_panel,
    draw_language_box,
    draw_panel_header,
    draw_qr_placeholder,
    draw_sound_state_icon,
    draw_toggle_switch,
    wrap_text,
)
from components.setting_icon import draw_gear_icon
from core.ui_fonts import get_ui_font


class HomePage:
    def __init__(self, screen, preferences):
        self.screen = screen
        self.preferences = preferences

        self.btn_1player = None
        self.btn_2players = None
        self.btn_rules = None
        self.btn_quit = None
        self.gear_rect = None

        self.modal_stack = []
        self.language_dropdown_open = False

        self.rules_exit_button = None
        self.settings_buttons = {}
        self.quit_buttons = {}
        self.about_exit_button = None
        self.donate_exit_button = None
        self.settings_draft_language = self.preferences.language
        self.settings_draft_volume = self.preferences.volume_on

    def sx(self, x):
        return int(x * self.screen.get_width() / BASE_WIDTH)

    def sy(self, y):
        return int(y * self.screen.get_height() / BASE_HEIGHT)

    def sf(self, size):
        scale_w = self.screen.get_width() / BASE_WIDTH
        scale_h = self.screen.get_height() / BASE_HEIGHT
        return max(16, int(size * min(scale_w, scale_h)))

    @property
    def current_modal(self):
        return self.modal_stack[-1] if self.modal_stack else None

    def open_modal(self, modal_name):
        if modal_name == "settings":
            self.settings_draft_language = self.preferences.language
            self.settings_draft_volume = self.preferences.volume_on
            self.language_dropdown_open = False
        self.modal_stack.append(modal_name)
        if modal_name != "settings":
            self.language_dropdown_open = False

    def close_modal(self):
        if self.modal_stack:
            self.modal_stack.pop()
        if self.current_modal != "settings":
            self.language_dropdown_open = False

    def make_centered_rect(self, width_ratio, height_ratio, top_ratio=None):
        width = int(self.screen.get_width() * width_ratio)
        height = int(self.screen.get_height() * height_ratio)
        x = (self.screen.get_width() - width) // 2
        y = (self.screen.get_height() - height) // 2 if top_ratio is None else int(self.screen.get_height() * top_ratio)
        return pygame.Rect(x, y, width, height)

    def reset_modal_rects(self):
        self.rules_exit_button = None
        self.settings_buttons = {}
        self.quit_buttons = {}
        self.about_exit_button = None
        self.donate_exit_button = None

    def draw_title(self):
        font = get_ui_font(self.sf(TITLE_FONT_SIZE), bold=True, serif=True)
        title = font.render("CONNECT 4", True, BLACK)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, self.sy(88)))
        self.screen.blit(title, title_rect)

    def draw_buttons(self):
        button_font_size = self.sf(36 if self.preferences.language == "vi" else 42)

        self.btn_1player = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(270),
            self.sx(343),
            self.sy(103),
            self.preferences.text("home_1player"),
            button_font_size,
        )
        self.btn_2players = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(408),
            self.sx(343),
            self.sy(103),
            self.preferences.text("home_2players"),
            button_font_size,
        )
        self.btn_rules = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(565),
            self.sx(343),
            self.sy(103),
            self.preferences.text("home_rules"),
            button_font_size,
        )
        self.btn_quit = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(715),
            self.sx(343),
            self.sy(103),
            self.preferences.text("home_quit"),
            button_font_size,
        )

    def draw_team_name(self):
        font = get_ui_font(self.sf(TEAM_FONT_SIZE), bold=True, serif=True)
        team_text = font.render(self.preferences.text("team_name"), True, BLACK)
        text_rect = team_text.get_rect(topright=(self.sx(1360), self.sy(900)))
        self.screen.blit(team_text, text_rect)

    def draw_gear_button(self):
        center_x = self.sx(98)
        center_y = self.sy(929)
        outer_r = max(28, self.sx(58))
        inner_r = max(12, self.sx(24))

        draw_gear_icon(self.screen, center_x, center_y, outer_r, inner_r)
        self.gear_rect = pygame.Rect(center_x - outer_r, center_y - outer_r, outer_r * 2, outer_r * 2)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_title()
        self.draw_buttons()
        draw_home_board(self.screen, self.sx, self.sy)
        self.draw_gear_button()
        self.draw_team_name()

        self.reset_modal_rects()

        for index, modal_name in enumerate(self.modal_stack):
            draw_backdrop(self.screen, 128 if index == 0 else 158)

            if modal_name == "rules":
                self.draw_rules_modal()
            elif modal_name == "settings":
                self.draw_settings_modal()
            elif modal_name == "about":
                self.draw_about_modal()
            elif modal_name == "donate":
                self.draw_donate_modal()
            elif modal_name == "quit_confirm":
                self.draw_quit_modal()

    def draw_rules_modal(self):
        title_font = get_ui_font(self.sf(34), bold=True)
        body_font = get_ui_font(self.sf(26), bold=True)
        button_font_size = self.sf(26)

        panel_width = min(int(self.screen.get_width() * 0.66), self.sx(700))
        text_width = int(panel_width * 0.78)
        wrapped_lines = []
        for paragraph in self.preferences.lines("rules_lines"):
            wrapped_lines.extend(wrap_text(body_font, paragraph, text_width))

        line_height = body_font.get_height() + self.sy(8)
        content_height = len(wrapped_lines) * line_height
        button_height = max(56, self.sy(76))
        header_space = self.sy(96)
        bottom_space = self.sy(42) + button_height + self.sy(28)
        panel_height = header_space + content_height + bottom_space
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(14, self.sx(18)),
            inner_width=max(2, self.sx(2)),
        )
        draw_panel_header(self.screen, panel_rect, self.preferences.text("home_rules"), title_font)

        text_y = panel_rect.top + self.sy(102)
        for line in wrapped_lines:
            label = body_font.render(line, True, BLACK)
            label_rect = label.get_rect(center=(panel_rect.centerx, text_y + label.get_height() // 2))
            self.screen.blit(label, label_rect)
            text_y += line_height

        button_width = max(140, panel_rect.w // 4)
        button_x = panel_rect.centerx - button_width // 2
        button_y = panel_rect.bottom - button_height - self.sy(28)
        self.rules_exit_button = draw_outline_button(
            self.screen,
            button_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            button_font_size,
        )

    def draw_settings_modal(self):
        panel_rect = self.make_centered_rect(0.60, 0.78, 0.08)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )
        header_font = get_ui_font(self.sf(42), bold=True)
        draw_panel_header(self.screen, panel_rect, self.preferences.text("settings_title"), header_font)

        icon_center = (panel_rect.left + int(panel_rect.w * 0.18), panel_rect.top + int(panel_rect.h * 0.35))
        draw_sound_state_icon(self.screen, icon_center, max(40, panel_rect.w // 11), self.settings_draft_volume)

        volume_rect = pygame.Rect(
            panel_rect.left + int(panel_rect.w * 0.29),
            panel_rect.top + int(panel_rect.h * 0.305),
            int(panel_rect.w * 0.20),
            int(panel_rect.h * 0.085),
        )
        draw_toggle_switch(self.screen, volume_rect, self.settings_draft_volume)
        self.settings_buttons["volume"] = volume_rect

        language_rect = pygame.Rect(
            panel_rect.left + int(panel_rect.w * 0.52),
            panel_rect.top + int(panel_rect.h * 0.275),
            int(panel_rect.w * 0.36),
            int(panel_rect.h * 0.14),
        )
        language_font = get_ui_font(self.sf(20), bold=False)
        draw_language_box(
            self.screen,
            language_rect,
            self.preferences.language_label(self.settings_draft_language).upper(),
            language_font,
        )
        self.settings_buttons["language_box"] = language_rect

        button_width = int(panel_rect.w * 0.34)
        button_height = int(panel_rect.h * 0.14)
        left_x = panel_rect.left + int(panel_rect.w * 0.10)
        right_x = panel_rect.right - button_width - int(panel_rect.w * 0.10)
        top_row_y = panel_rect.top + int(panel_rect.h * 0.60)
        bottom_row_y = panel_rect.top + int(panel_rect.h * 0.78)
        button_font_size = self.sf(28)

        self.settings_buttons["about"] = draw_outline_button(
            self.screen,
            left_x,
            top_row_y,
            button_width,
            button_height,
            self.preferences.text("about_title"),
            button_font_size,
        )
        self.settings_buttons["donate"] = draw_outline_button(
            self.screen,
            right_x,
            top_row_y,
            button_width,
            button_height,
            self.preferences.text("donate_title"),
            button_font_size,
        )
        self.settings_buttons["save"] = draw_outline_button(
            self.screen,
            left_x,
            bottom_row_y,
            button_width,
            button_height,
            self.preferences.text("save"),
            button_font_size,
        )
        self.settings_buttons["exit"] = draw_outline_button(
            self.screen,
            right_x,
            bottom_row_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            button_font_size,
        )

        if self.language_dropdown_open:
            option_height = int(language_rect.h * 0.78)
            dropdown_rect = pygame.Rect(
                language_rect.left,
                language_rect.bottom + self.sy(6),
                language_rect.w,
                option_height * 2,
            )
            pygame.draw.rect(self.screen, WHITE, dropdown_rect)
            pygame.draw.rect(self.screen, (244, 180, 215), dropdown_rect, width=max(2, self.sx(2)))

            option_font = get_ui_font(self.sf(20), bold=True)
            for index, code in enumerate(("en", "vi")):
                rect = pygame.Rect(
                    dropdown_rect.left,
                    dropdown_rect.top + option_height * index,
                    dropdown_rect.w,
                    option_height,
                )
                if code == self.settings_draft_language:
                    pygame.draw.rect(self.screen, (255, 245, 250), rect)
                if index > 0:
                    pygame.draw.line(
                        self.screen,
                        (244, 180, 215),
                        (rect.left, rect.top),
                        (rect.right, rect.top),
                        max(1, self.sx(1)),
                    )
                option_text = option_font.render(self.preferences.language_label(code), True, BLACK)
                option_text_rect = option_text.get_rect(center=rect.center)
                self.screen.blit(option_text, option_text_rect)
                self.settings_buttons[f"language_{code}"] = rect

    def draw_about_modal(self):
        panel_rect = self.make_centered_rect(0.68, 0.68, 0.08)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )
        header_font = get_ui_font(self.sf(42), bold=True)
        draw_panel_header(self.screen, panel_rect, self.preferences.text("about_title"), header_font)

        title_font = get_ui_font(self.sf(28), bold=True)
        body_font = get_ui_font(self.sf(24), bold=True)
        highlight_font = get_ui_font(self.sf(26), bold=True)

        y = panel_rect.top + int(panel_rect.h * 0.24)

        intro_lines = wrap_text(title_font, self.preferences.text("about_intro"), int(panel_rect.w * 0.80))
        for line in intro_lines:
            label = title_font.render(line, True, BLACK)
            rect = label.get_rect(center=(panel_rect.centerx, y))
            self.screen.blit(label, rect)
            y += label.get_height() + self.sy(10)

        y += self.sy(12)
        for name in self.preferences.lines("about_names"):
            label = body_font.render(name, True, BLACK)
            rect = label.get_rect(center=(panel_rect.centerx, y))
            self.screen.blit(label, rect)
            y += label.get_height() + self.sy(14)

        y += self.sy(20)
        for line in wrap_text(highlight_font, self.preferences.text("about_highlight"), int(panel_rect.w * 0.86)):
            label = highlight_font.render(line, True, (255, 42, 42))
            rect = label.get_rect(center=(panel_rect.centerx, y))
            self.screen.blit(label, rect)
            y += label.get_height() + self.sy(10)

        creator = highlight_font.render(self.preferences.text("about_creator"), True, (255, 42, 42))
        creator_rect = creator.get_rect(center=(panel_rect.centerx, y + self.sy(6)))
        self.screen.blit(creator, creator_rect)

        button_width = max(130, panel_rect.w // 5)
        button_height = max(58, panel_rect.h // 10)
        button_x = panel_rect.centerx - button_width // 2
        button_y = panel_rect.bottom - button_height - self.sy(42)
        self.about_exit_button = draw_outline_button(
            self.screen,
            button_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            self.sf(28),
        )

    def draw_donate_modal(self):
        panel_rect = self.make_centered_rect(0.64, 0.66, 0.08)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )
        header_font = get_ui_font(self.sf(42), bold=True)
        draw_panel_header(self.screen, panel_rect, self.preferences.text("donate_title"), header_font)

        qr_size = int(min(panel_rect.w * 0.50, panel_rect.h * 0.48))
        qr_rect = pygame.Rect(0, 0, qr_size, qr_size)
        qr_rect.center = (panel_rect.centerx, panel_rect.top + int(panel_rect.h * 0.44))
        draw_qr_placeholder(self.screen, qr_rect)

        button_width = max(130, panel_rect.w // 5)
        button_height = max(58, panel_rect.h // 10)
        button_x = panel_rect.centerx - button_width // 2
        button_y = panel_rect.bottom - button_height - self.sy(42)
        self.donate_exit_button = draw_outline_button(
            self.screen,
            button_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            self.sf(28),
        )

    def draw_quit_modal(self):
        panel_rect = self.make_centered_rect(0.94, 0.38, 0.28)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )

        title_font = get_ui_font(self.sf(40), bold=True)
        title_y = panel_rect.top + int(panel_rect.h * 0.22)
        for line in wrap_text(title_font, self.preferences.text("quit_prompt"), int(panel_rect.w * 0.86)):
            label = title_font.render(line, True, BLACK)
            rect = label.get_rect(center=(panel_rect.centerx, title_y))
            self.screen.blit(label, rect)
            title_y += label.get_height() + self.sy(10)

        button_width = int(panel_rect.w * 0.22)
        button_height = int(panel_rect.h * 0.24)
        button_y = panel_rect.top + int(panel_rect.h * 0.55)
        left_x = panel_rect.left + int(panel_rect.w * 0.20)
        right_x = panel_rect.right - button_width - int(panel_rect.w * 0.20)

        self.quit_buttons["yes"] = draw_outline_button(
            self.screen,
            left_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("yes"),
            self.sf(30),
        )
        self.quit_buttons["no"] = draw_outline_button(
            self.screen,
            right_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("no"),
            self.sf(30),
        )

    def handle_settings_click(self, mouse_pos):
        if self.language_dropdown_open:
            for code in ("en", "vi"):
                rect = self.settings_buttons.get(f"language_{code}")
                if rect and rect.collidepoint(mouse_pos):
                    self.settings_draft_language = code
                    self.language_dropdown_open = False
                    return None

        language_box = self.settings_buttons.get("language_box")
        if language_box and language_box.collidepoint(mouse_pos):
            self.language_dropdown_open = not self.language_dropdown_open
            return None

        if self.language_dropdown_open:
            self.language_dropdown_open = False

        if self.settings_buttons.get("volume") and self.settings_buttons["volume"].collidepoint(mouse_pos):
            self.settings_draft_volume = not self.settings_draft_volume
            return None

        if self.settings_buttons.get("about") and self.settings_buttons["about"].collidepoint(mouse_pos):
            self.open_modal("about")
            return None

        if self.settings_buttons.get("donate") and self.settings_buttons["donate"].collidepoint(mouse_pos):
            self.open_modal("donate")
            return None

        if self.settings_buttons.get("save") and self.settings_buttons["save"].collidepoint(mouse_pos):
            try:
                self.preferences.set_language(self.settings_draft_language)
                self.preferences.set_volume(self.settings_draft_volume)
                self.preferences.save()
            except OSError:
                pass
            self.close_modal()
            return None

        if self.settings_buttons.get("exit") and self.settings_buttons["exit"].collidepoint(mouse_pos):
            self.close_modal()
            return None

        return None

    def handle_modal_click(self, mouse_pos):
        if self.current_modal == "rules":
            if self.rules_exit_button and self.rules_exit_button.collidepoint(mouse_pos):
                self.close_modal()
            return None

        if self.current_modal == "settings":
            return self.handle_settings_click(mouse_pos)

        if self.current_modal == "about":
            if self.about_exit_button and self.about_exit_button.collidepoint(mouse_pos):
                self.close_modal()
            return None

        if self.current_modal == "donate":
            if self.donate_exit_button and self.donate_exit_button.collidepoint(mouse_pos):
                self.close_modal()
            return None

        if self.current_modal == "quit_confirm":
            if self.quit_buttons.get("yes") and self.quit_buttons["yes"].collidepoint(mouse_pos):
                return "quit"
            if self.quit_buttons.get("no") and self.quit_buttons["no"].collidepoint(mouse_pos):
                self.close_modal()
            return None

        return None

    def handle_click(self, mouse_pos):
        if self.current_modal:
            return self.handle_modal_click(mouse_pos)

        if self.gear_rect and self.gear_rect.collidepoint(mouse_pos):
            self.open_modal("settings")
            return None

        if self.btn_1player and self.btn_1player.collidepoint(mouse_pos):
            return "mode_select"
        if self.btn_2players and self.btn_2players.collidepoint(mouse_pos):
            return "2players"
        if self.btn_rules and self.btn_rules.collidepoint(mouse_pos):
            self.open_modal("rules")
            return None
        if self.btn_quit and self.btn_quit.collidepoint(mouse_pos):
            self.open_modal("quit_confirm")
            return None
        return None
