import json
from pathlib import Path

import pygame


SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.json"
SUPPORTED_LANGUAGES = ("en", "vi")
LANGUAGE_NAMES = {
    "en": "English",
    "vi": "Tiếng Việt",
}

TRANSLATIONS = {
    "en": {
        "home_1player": "1 PLAYER",
        "home_2players": "2 PLAYERS",
        "home_rules": "RULES",
        "home_quit": "QUIT",
        "team_name": "TEAM 5",
        "settings_title": "SETTING",
        "about_title": "ABOUT",
        "donate_title": "DONATE",
        "save": "SAVE",
        "exit": "EXIT",
        "yes": "YES",
        "no": "NO",
        "quit_prompt": "ARE YOU SURE YOU WANT TO QUIT ?",
        "levels_title": "LEVELS",
        "easy": "EASY",
        "medium": "MEDIUM",
        "hard": "HARD",
        "status_your_turn": "YOUR TURN",
        "status_ai_turn": "AI TURN",
        "status_player1_turn": "PLAYER 1 TURN",
        "status_player2_turn": "PLAYER 2 TURN",
        "status_you_win": "YOU WIN!",
        "status_ai_win": "AI WIN!",
        "status_player1_win": "PLAYER 1 WINS!",
        "status_player2_win": "PLAYER 2 WINS!",
        "status_draw": "DRAW!",
        "rules_lines": [
            "Players take turns dropping a piece into one of the columns.",
            "On each turn, choose a column.",
            "The piece falls to the lowest empty slot in that column.",
            "You cannot place a piece in a full column.",
            "Connect four matching pieces in a row, column, or diagonal to win.",
            "If the board fills up and nobody connects four, the game is a draw.",
        ],
        "about_intro": "Project Team 5, Artificial Intelligence, UTC.",
        "about_highlight": "This game was first developed by",
        "about_creator": "Howard Wexler",
        "about_names": [
            "Ta Bach Dat",
            "Le Nhat Long",
            "Nguyen Dieu Linh",
        ],
    },
    "vi": {
        "home_1player": "1 NGƯỜI CHƠI",
        "home_2players": "2 NGƯỜI CHƠI",
        "home_rules": "LUẬT CHƠI",
        "home_quit": "THOÁT",
        "team_name": "NHÓM 5",
        "settings_title": "CÀI ĐẶT",
        "about_title": "GIỚI THIỆU",
        "donate_title": "ỦNG HỘ",
        "save": "LƯU",
        "exit": "THOÁT",
        "yes": "CÓ",
        "no": "KHÔNG",
        "quit_prompt": "BẠN CÓ CHẮC MUỐN THOÁT KHỎI TRÒ CHƠI KHÔNG?",
        "levels_title": "MỨC ĐỘ",
        "easy": "DỄ",
        "medium": "TRUNG BÌNH",
        "hard": "KHÓ",
        "status_your_turn": "LƯỢT CỦA BẠN",
        "status_ai_turn": "LƯỢT CỦA AI",
        "status_player1_turn": "LƯỢT NGƯỜI CHƠI 1",
        "status_player2_turn": "LƯỢT NGƯỜI CHƠI 2",
        "status_you_win": "BẠN THẮNG!",
        "status_ai_win": "AI THẮNG!",
        "status_player1_win": "NGƯỜI CHƠI 1 THẮNG!",
        "status_player2_win": "NGƯỜI CHƠI 2 THẮNG!",
        "status_draw": "HÒA!",
        "rules_lines": [
            "Hai người lần lượt thay phiên nhau thả quân cờ vào các cột.",
            "Mỗi lượt, bạn chọn một cột.",
            "Quân cờ sẽ rơi xuống vị trí thấp nhất còn trống trong cột đó.",
            "Bạn không thể đặt quân vào cột đã đầy.",
            "Ai tạo được 4 quân cùng màu liên tiếp theo hàng ngang, dọc hoặc chéo trước sẽ thắng.",
            "Bảng đầy và không có 4 quân liên tiếp thì hòa.",
        ],
        "about_intro": "Project team 5 môn Trí tuệ nhân tạo, UTC.",
        "about_highlight": "Trò chơi được phát triển lần đầu bởi",
        "about_creator": "Howard Wexler",
        "about_names": [
            "Tạ Bách Đạt",
            "Lê Nhật Long",
            "Nguyễn Diệu Linh",
        ],
    },
}


class GamePreferences:
    def __init__(self, language="en", volume_on=True):
        self.language = language if language in SUPPORTED_LANGUAGES else "en"
        self.volume_on = bool(volume_on)

    @classmethod
    def load(cls):
        if not SETTINGS_FILE.exists():
            return cls()

        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        return cls(
            language=data.get("language", "en"),
            volume_on=data.get("volume_on", True),
        )

    def save(self):
        SETTINGS_FILE.write_text(
            json.dumps(
                {
                    "language": self.language,
                    "volume_on": self.volume_on,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def apply_audio(self):
        volume = 1.0 if self.volume_on else 0.0

        if not pygame.mixer.get_init():
            return

        try:
            pygame.mixer.music.set_volume(volume)
        except pygame.error:
            pass

    def set_language(self, language):
        if language in SUPPORTED_LANGUAGES:
            self.language = language

    def set_volume(self, volume_on):
        self.volume_on = bool(volume_on)
        self.apply_audio()

    def toggle_volume(self):
        self.set_volume(not self.volume_on)

    def text(self, key):
        selected = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        fallback = TRANSLATIONS["en"]
        return selected.get(key, fallback.get(key, key))

    def lines(self, key):
        value = self.text(key)
        if isinstance(value, list):
            return value
        return [str(value)]

    def language_label(self, language_code):
        return LANGUAGE_NAMES.get(language_code, language_code.upper())
