"""
Fish Quest - Ocean Adventure Game
Leaderboard Screen Module

Displays:
- Top 10 players retrieved from SQLite database
- Rank badges, username, highest score, total games played, total coins
- Back to Menu button
"""

from typing import Optional, List, Dict, Any
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


class LeaderboardScreen(BaseScreen):
    """
    Displays the top 10 ranked players queried directly from SQLite.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.leaderboard_data: List[Dict[str, Any]] = []
        self._init_buttons()

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
        # Fetch fresh top 10 players from database
        self.leaderboard_data = self.db.get_leaderboard(limit=10)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.btn_back.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.change_screen("menu")

    def draw(self, surface: pygame.Surface) -> None:
        card_w, card_h = 760, 580
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, 35, card_w, card_h)
        self.draw_glass_card(surface, card_rect, border_radius=20)

        # Header
        self.draw_header(surface, "Global Leaderboard", "Top 10 Ocean Adventurers (Ranked by High Score)", y=75)

        # Table Header Bar
        table_x = card_rect.x + 30
        table_w = card_rect.width - 60
        header_y = 120
        header_h = 36

        header_surf = pygame.Surface((table_w, header_h), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (22, 53, 98, 220), header_surf.get_rect(), border_radius=8)
        surface.blit(header_surf, (table_x, header_y))

        hdr_font = self.fonts["small"]
        col_rank = hdr_font.render("Rank", True, COLOR_AQUA_ACCENT)
        col_user = hdr_font.render("Player Username", True, COLOR_AQUA_ACCENT)
        col_score = hdr_font.render("High Score", True, COLOR_AQUA_ACCENT)
        col_games = hdr_font.render("Games Played", True, COLOR_AQUA_ACCENT)
        col_coins = hdr_font.render("Total Coins", True, COLOR_AQUA_ACCENT)

        surface.blit(col_rank, (table_x + 15, header_y + 8))
        surface.blit(col_user, (table_x + 95, header_y + 8))
        surface.blit(col_score, (table_x + 310, header_y + 8))
        surface.blit(col_games, (table_x + 440, header_y + 8))
        surface.blit(col_coins, (table_x + 580, header_y + 8))

        # Rows
        row_font = self.fonts["normal"]
        row_y = header_y + 42
        row_h = 34

        if not self.leaderboard_data:
            empty_surf = self.fonts["normal"].render("No games recorded yet. Be the first explorer!", True, COLOR_TEXT_SECONDARY)
            surface.blit(empty_surf, empty_surf.get_rect(center=(SCREEN_WIDTH // 2, 280)))
        else:
            for rank, entry in enumerate(self.leaderboard_data, start=1):
                # Rank styling
                if rank == 1:
                    rank_color = COLOR_GOLD
                    rank_label = "🥇 1st"
                elif rank == 2:
                    rank_color = (226, 232, 240)
                    rank_label = "🥈 2nd"
                elif rank == 3:
                    rank_color = (205, 127, 50)
                    rank_label = "🥉 3rd"
                else:
                    rank_color = COLOR_TEXT_SECONDARY
                    rank_label = f"  #{rank}"

                # Highlight logged-in player
                is_current = (entry.get("id") == self.auth.current_user_id)
                if is_current:
                    highlight_surf = pygame.Surface((table_w, row_h - 4), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surf, (14, 165, 233, 45), highlight_surf.get_rect(), border_radius=6)
                    pygame.draw.rect(highlight_surf, (56, 189, 248, 120), highlight_surf.get_rect(), width=1, border_radius=6)
                    surface.blit(highlight_surf, (table_x, row_y - 2))

                text_color = COLOR_AQUA_ACCENT if is_current else COLOR_TEXT_PRIMARY

                r_txt = row_font.render(rank_label, True, rank_color)
                u_txt = row_font.render(str(entry.get("username", ""))[:16], True, text_color)
                s_txt = row_font.render(f"{entry.get('highest_score', 0)} pts", True, COLOR_GOLD if rank == 1 else COLOR_TEXT_PRIMARY)
                g_txt = row_font.render(str(entry.get("total_games", 0)), True, COLOR_TEXT_SECONDARY)
                c_txt = row_font.render(f"{entry.get('total_coins', 0)}", True, COLOR_GOLD)

                surface.blit(r_txt, (table_x + 15, row_y))
                surface.blit(u_txt, (table_x + 95, row_y))
                surface.blit(s_txt, (table_x + 310, row_y))
                surface.blit(g_txt, (table_x + 470, row_y))
                surface.blit(c_txt, (table_x + 600, row_y))

                row_y += row_h

        # Back button
        self.btn_back.draw(surface)

