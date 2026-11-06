"""
Fish Quest - Ocean Adventure Game
Results Screen Module

Displays:
- Player username
- Final score
- Total correct answers
- Total incorrect answers
- Coins earned
- Play Again and Main Menu buttons
"""

from typing import Optional, Dict, Any
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button
from config.settings import (
    BTN_SUCCESS,
    BTN_PRIMARY,
    COLOR_AQUA_ACCENT,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_SUCCESS_GREEN,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SCREEN_WIDTH,
    IMAGES_DIR
)


class ResultScreen(BaseScreen):
    """
    Final match summary screen displaying player achievements and database records.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.summary_data: Dict[str, Any] = {}
        self.coin_icon: Optional[pygame.Surface] = None
        self._load_assets()
        self._init_buttons()

    def _load_assets(self) -> None:
        coin_path = IMAGES_DIR / "coin.png"
        try:
            if coin_path.exists():
                raw = pygame.image.load(str(coin_path)).convert_alpha()
                self.coin_icon = pygame.transform.smoothscale(raw, (32, 32))
        except Exception as e:
            print(f"[Asset Warning] Failed loading coin icon: {e}")

    def _init_buttons(self) -> None:
        font = self.fonts["normal"]
        btn_w, btn_h = 240, 50
        start_y = 500

        self.btn_play_again = Button(
            rect=(SCREEN_WIDTH // 2 - btn_w - 15, start_y, btn_w, btn_h),
            text="Play Again ↻",
            font=font,
            theme=BTN_SUCCESS,
            on_click=self._on_play_again
        )

        self.btn_menu = Button(
            rect=(SCREEN_WIDTH // 2 + 15, start_y, btn_w, btn_h),
            text="Main Menu ☰",
            font=font,
            theme=BTN_PRIMARY,
            on_click=lambda: self.manager.change_screen("menu")
        )

        self.buttons = [self.btn_play_again, self.btn_menu]

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        self.summary_data = params or {}

    def _on_play_again(self) -> None:
        self.manager.game_manager.start_game()
        self.manager.change_screen("gameplay")

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        card_w, card_h = 560, 560
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, 50, card_w, card_h)
        self.draw_glass_card(surface, card_rect, border_radius=20)

        # Header
        self.draw_header(surface, "Quest Completed!", "Here is your ocean adventure summary", y=95)

        # Player Username Virtual Identity badge
        username = self.auth.current_username
        user_font = self.fonts["large"]
        user_surf = user_font.render(f"Explorer: {username}", True, COLOR_AQUA_ACCENT)
        user_rect = user_surf.get_rect(center=(SCREEN_WIDTH // 2, 145))
        surface.blit(user_surf, user_rect)

        # Big Final Score
        final_score = self.summary_data.get("final_score", 0)
        score_font = self.fonts["title"]
        score_surf = score_font.render(f"{final_score} PTS", True, COLOR_TEXT_PRIMARY)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 210))
        surface.blit(score_surf, score_rect)

        # Metrics Grid Card
        grid_w, grid_h = 460, 190
        grid_rect = pygame.Rect((SCREEN_WIDTH - grid_w) // 2, 260, grid_w, grid_h)
        grid_surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
        pygame.draw.rect(grid_surf, (10, 24, 48, 180), grid_surf.get_rect(), border_radius=12)
        pygame.draw.rect(grid_surf, (56, 189, 248, 90), grid_surf.get_rect(), width=1, border_radius=12)
        surface.blit(grid_surf, grid_rect.topleft)

        correct = self.summary_data.get("correct_answers", 0)
        incorrect = self.summary_data.get("incorrect_answers", 0)
        coins = self.summary_data.get("total_coins", 0)
        streak = self.summary_data.get("highest_streak", 0)
        level = self.summary_data.get("final_level", 1)

        font_norm = self.fonts["normal"]
        font_sm = self.fonts["small"]

        # Left Column: Correct & Incorrect
        c_label = font_sm.render("Correct Answers:", True, COLOR_TEXT_SECONDARY)
        c_val = font_norm.render(f"✔  {correct}", True, COLOR_SUCCESS_GREEN)
        surface.blit(c_label, (grid_rect.x + 30, grid_rect.y + 25))
        surface.blit(c_val, (grid_rect.x + 30, grid_rect.y + 48))

        i_label = font_sm.render("Incorrect Answers:", True, COLOR_TEXT_SECONDARY)
        i_val = font_norm.render(f"✖  {incorrect}", True, COLOR_CORAL_RED)
        surface.blit(i_label, (grid_rect.x + 30, grid_rect.y + 95))
        surface.blit(i_val, (grid_rect.x + 30, grid_rect.y + 118))

        # Right Column: Coins & Best Streak
        coin_label = font_sm.render("Coins Earned:", True, COLOR_TEXT_SECONDARY)
        surface.blit(coin_label, (grid_rect.x + 250, grid_rect.y + 25))
        if self.coin_icon:
            surface.blit(self.coin_icon, (grid_rect.x + 248, grid_rect.y + 48))
        coins_val = font_norm.render(f"+{coins}", True, COLOR_GOLD)
        surface.blit(coins_val, (grid_rect.x + 288, grid_rect.y + 52))

        s_label = font_sm.render("Highest Streak & Level:", True, COLOR_TEXT_SECONDARY)
        s_val = font_norm.render(f"🔥 {streak} in a row (Lvl {level})", True, COLOR_AQUA_ACCENT)
        surface.blit(s_label, (grid_rect.x + 250, grid_rect.y + 95))
        surface.blit(s_val, (grid_rect.x + 250, grid_rect.y + 118))

        # Database auto-saved notice
        saved_surf = self.fonts["tiny"].render(
            "Match record automatically saved to persistent SQLite database.",
            True,
            COLOR_TEXT_SECONDARY
        )
        saved_rect = saved_surf.get_rect(center=(SCREEN_WIDTH // 2, 470))
        surface.blit(saved_surf, saved_rect)

        # Action Buttons
        for btn in self.buttons:
            btn.draw(surface)

