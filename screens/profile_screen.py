"""
Fish Quest - Ocean Adventure Game
Profile Screen Module

Displays:
- Authenticated player's virtual identity details
- Career stats (highest score, games played, total coins)
- Account creation timestamp
- Recent match performance history from SQLite
- Back button
"""

from typing import Optional, List, Dict, Any
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button
from config.settings import (
    BTN_PRIMARY,
    COLOR_AQUA_ACCENT,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_SUCCESS_GREEN,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    IMAGES_DIR
)


class ProfileScreen(BaseScreen):
    """
    Displays the authenticated player's complete virtual identity and history.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.recent_matches: List[Dict[str, Any]] = []
        self.coin_icon: Optional[pygame.Surface] = None
        self._load_assets()
        self._init_buttons()

    def _load_assets(self) -> None:
        coin_path = IMAGES_DIR / "coin.png"
        try:
            if coin_path.exists():
                raw = pygame.image.load(str(coin_path)).convert_alpha()
                self.coin_icon = pygame.transform.smoothscale(raw, (28, 28))
        except Exception as e:
            print(f"[Asset Warning] Failed to load coin icon: {e}")

    def _init_buttons(self) -> None:
        font = self.fonts["normal"]
        btn_w, btn_h = 240, 48
        cx = (SCREEN_WIDTH - btn_w) // 2
        btn_y = SCREEN_HEIGHT - 75

        self.btn_back = Button(
            rect=(cx, btn_y, btn_w, btn_h),
            text="Back to Main Menu",
            font=font,
            theme=BTN_PRIMARY,
            on_click=lambda: self.manager.change_screen("menu")
        )

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        if not self.auth.is_authenticated:
            self.manager.change_screen("login", {"msg": "Please login to view profile."})
            return

        self.auth.refresh_current_user()
        user_id = self.auth.current_user_id
        if user_id is not None:
            self.recent_matches = self.db.get_player_history(user_id, limit=5)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.btn_back.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.change_screen("menu")

    def draw(self, surface: pygame.Surface) -> None:
        card_w, card_h = 760, 580
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, 35, card_w, card_h)
        self.draw_glass_card(surface, card_rect, border_radius=20)

        curr = self.auth.current_user or {}
        username = curr.get("username", "Guest")
        created_at = curr.get("created_at", "N/A")[:10]  # Just YYYY-MM-DD
        high_score = curr.get("highest_score", 0)
        total_games = curr.get("total_games", 0)
        total_coins = curr.get("total_coins", 0)

        # Header
        self.draw_header(surface, f"Player Identity: {username}", f"Member since {created_at}", y=75)

        # 3 Career Overview Metric Cards
        metric_w = 200
        metric_h = 90
        spacing = 30
        total_metrics_w = (metric_w * 3) + (spacing * 2)
        start_x = (SCREEN_WIDTH - total_metrics_w) // 2
        m_y = 125

        # 1. High Score Card
        rect1 = pygame.Rect(start_x, m_y, metric_w, metric_h)
        self._draw_mini_card(surface, rect1, "Highest Score", f"{high_score} pts", COLOR_AQUA_ACCENT)

        # 2. Total Coins Card
        rect2 = pygame.Rect(start_x + metric_w + spacing, m_y, metric_w, metric_h)
        self._draw_mini_card(surface, rect2, "Total Coins", f"{total_coins}", COLOR_GOLD)

        # 3. Games Played Card
        rect3 = pygame.Rect(start_x + (metric_w + spacing) * 2, m_y, metric_w, metric_h)
        self._draw_mini_card(surface, rect3, "Games Played", f"{total_games}", COLOR_TEXT_PRIMARY)

        # Recent Matches Section Title
        sec_y = 235
        sec_font = self.fonts["normal"]
        sec_surf = sec_font.render("Recent Match History (SQLite Persistence)", True, COLOR_AQUA_ACCENT)
        surface.blit(sec_surf, (card_rect.x + 35, sec_y))

        # Recent Matches Table
        table_x = card_rect.x + 35
        table_w = card_rect.width - 70
        hdr_y = 270
        hdr_h = 32

        # Table Header
        t_hdr = pygame.Surface((table_w, hdr_h), pygame.SRCALPHA)
        pygame.draw.rect(t_hdr, (22, 53, 98, 220), t_hdr.get_rect(), border_radius=6)
        surface.blit(t_hdr, (table_x, hdr_y))

        f_sm = self.fonts["small"]
        surface.blit(f_sm.render("Date / Time", True, COLOR_AQUA_ACCENT), (table_x + 15, hdr_y + 7))
        surface.blit(f_sm.render("Final Score", True, COLOR_AQUA_ACCENT), (table_x + 190, hdr_y + 7))
        surface.blit(f_sm.render("Correct / Incorrect", True, COLOR_AQUA_ACCENT), (table_x + 330, hdr_y + 7))
        surface.blit(f_sm.render("Coins Earned", True, COLOR_AQUA_ACCENT), (table_x + 520, hdr_y + 7))

        row_y = hdr_y + 38
        row_h = 32
        row_font = self.fonts["normal"]

        if not self.recent_matches:
            no_games = row_font.render("No game history recorded yet. Start playing to see your stats!", True, COLOR_TEXT_SECONDARY)
            surface.blit(no_games, (table_x + 15, row_y + 15))
        else:
            for match in self.recent_matches:
                date_str = match.get("played_at", "")[:16].replace("T", " ")
                score = match.get("score", 0)
                cor = match.get("correct_answers", 0)
                incor = match.get("incorrect_answers", 0)
                coins_m = match.get("coins_earned", 0)

                d_surf = row_font.render(date_str, True, COLOR_TEXT_SECONDARY)
                s_surf = row_font.render(f"{score} pts", True, COLOR_TEXT_PRIMARY)
                ci_surf = row_font.render(f"✔ {cor}  |  ✖ {incor}", True, COLOR_TEXT_PRIMARY)
                c_surf = row_font.render(f"+{coins_m} 🪙", True, COLOR_GOLD)

                surface.blit(d_surf, (table_x + 15, row_y))
                surface.blit(s_surf, (table_x + 190, row_y))
                surface.blit(ci_surf, (table_x + 330, row_y))
                surface.blit(c_surf, (table_x + 520, row_y))

                row_y += row_h

        # Back button
        self.btn_back.draw(surface)

    def _draw_mini_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        value: str,
        val_color: tuple
    ) -> None:
        """Helper to render a sleek stat card."""
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (12, 28, 55, 200), s.get_rect(), border_radius=12)
        pygame.draw.rect(s, (56, 189, 248, 80), s.get_rect(), width=1, border_radius=12)
        surface.blit(s, rect.topleft)

        l_surf = self.fonts["small"].render(label, True, COLOR_TEXT_SECONDARY)
        surface.blit(l_surf, (rect.x + 16, rect.y + 14))

        v_surf = self.fonts["large"].render(value, True, val_color)
        surface.blit(v_surf, (rect.x + 16, rect.y + 38))

