"""
Fish Quest - Ocean Adventure Game
Instructions & Academic Themes Screen Module

Displays:
- Gameplay instructions and scoring mechanics
- Academic explanations of the four assignment concepts:
  1. Low Coupling & High Cohesion
  2. Event-Driven Programming
  3. Interoperability
  4. Virtual Identity
"""

from typing import Optional, Dict, Any
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button
from config.settings import (
    BTN_PRIMARY,
    COLOR_AQUA_ACCENT,
    COLOR_GOLD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)


class InstructionsScreen(BaseScreen):
    """
    Displays game tutorial and academic theme breakdowns.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.return_screen = "welcome"
        self._init_buttons()

    def _init_buttons(self) -> None:
        font = self.fonts["normal"]
        btn_w, btn_h = 240, 48
        cx = (SCREEN_WIDTH - btn_w) // 2
        btn_y = SCREEN_HEIGHT - 70

        self.btn_back = Button(
            rect=(cx, btn_y, btn_w, btn_h),
            text="Back",
            font=font,
            theme=BTN_PRIMARY,
            on_click=lambda: self.manager.change_screen(self.return_screen)
        )

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        if self.auth.is_authenticated:
            self.return_screen = "menu"
        else:
            self.return_screen = "welcome"

    def handle_event(self, event: pygame.event.Event) -> None:
        self.btn_back.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.change_screen(self.return_screen)

    def draw(self, surface: pygame.Surface) -> None:
        card_w, card_h = 860, 580
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, 35, card_w, card_h)
        self.draw_glass_card(surface, card_rect, border_radius=20)

        self.draw_header(surface, "How to Play & System Architecture", "CIS045-3 Distributed Service Architectures", y=70)

        f_head = self.fonts["normal"]
        f_body = self.fonts["small"]

        # Left Column: Gameplay Rules
        col1_x = card_rect.x + 35
        col1_w = 380

        # Section 1: Gameplay Rules
        s1_y = 115
        surface.blit(f_head.render("🎮 Ocean Adventure Rules", True, COLOR_GOLD), (col1_x, s1_y))

        rules = [
            "• Each round fetches a live puzzle from the Fish Game API.",
            "• Count the fish displayed in the ocean puzzle image.",
            "• Enter your numeric answer and click Submit (or press Enter).",
            "• Correct answers award +10 points and +5 coins.",
            "• 3+ correct answers in a row grant a Streak Bonus (+5 pts)!",
            "• Incorrect answers or running out of time deducts 1 Life.",
            "• You begin each quest with 3 lives.",
            "• Progression: Timer decreases as your level increases.",
            "• Match records and career totals are saved automatically."
        ]

        cur_y = s1_y + 32
        for r in rules:
            r_surf = f_body.render(r, True, COLOR_TEXT_PRIMARY)
            surface.blit(r_surf, (col1_x, cur_y))
            cur_y += 24

        # Right Column: The 4 Core Architectural Themes
        col2_x = card_rect.x + 440
        col2_w = 380

        surface.blit(f_head.render("🏛 Four Architectural Themes", True, COLOR_AQUA_ACCENT), (col2_x, s1_y))

        themes = [
            ("1. Low Coupling & High Cohesion",
             "Separates UI screens, DatabaseManager, AuthManager, API service, and Game state into isolated modules."),

            ("2. Event-Driven Programming",
             "Pygame event loop handles inputs, timers, and callbacks. Asynchronous threading prevents GUI freeze."),

            ("3. Interoperability",
             "Communicates with remote REST API via HTTP GET, parsing JSON and decoding Base64 / binary PNG streams."),

            ("4. Virtual Identity",
             "Persistent player accounts via SQLite with secure PBKDF2-HMAC-SHA256 salted hashes and session tracking.")
        ]

        t_y = s1_y + 32
        for title, desc in themes:
            t_title = f_body.render(title, True, COLOR_AQUA_ACCENT)
            surface.blit(t_title, (col2_x, t_y))
            t_y += 20

            # Wrap description into lines
            words = desc.split(" ")
            line = ""
            for w in words:
                test_line = f"{line} {w}".strip()
                if f_body.size(test_line)[0] < col2_w:
                    line = test_line
                else:
                    surface.blit(f_body.render(line, True, COLOR_TEXT_SECONDARY), (col2_x + 10, t_y))
                    t_y += 18
                    line = w
            if line:
                surface.blit(f_body.render(line, True, COLOR_TEXT_SECONDARY), (col2_x + 10, t_y))
                t_y += 24

        # Back Button
        self.btn_back.draw(surface)

