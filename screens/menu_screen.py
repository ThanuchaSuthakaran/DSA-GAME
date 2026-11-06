"""
Fish Quest - Ocean Adventure Game
Main Menu Screen Module

Displays:
- Welcome message with active player's username
- Start Game, Leaderboard, My Profile, Instructions, and Logout buttons.
- Player overview badges (Highest Score, Total Coins).
"""

from typing import Optional, Dict, Any
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button
from config.settings import (
    BTN_PRIMARY,
    BTN_SUCCESS,
    BTN_SECONDARY,
    BTN_DANGER,
    COLOR_AQUA_ACCENT,
    COLOR_GOLD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SCREEN_WIDTH,
    IMAGES_DIR
)


class MenuScreen(BaseScreen):
    """
    Central hub for authenticated players.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.buttons = []
        self.coin_icon: Optional[pygame.Surface] = None
        self._load_assets()
        self._init_buttons()

    def _load_assets(self) -> None:
        coin_path = IMAGES_DIR / "coin.png"
        if coin_path.exists():
            try:
                raw_coin = pygame.image.load(str(coin_path)).convert_alpha()
                self.coin_icon = pygame.transform.smoothscale(raw_coin, (28, 28))
            except Exception as e:
                print(f"[Asset Warning] Failed to load coin icon: {e}")

    def _init_buttons(self) -> None:
        font = self.fonts["normal"]
        btn_w, btn_h = 340, 52
        cx = (SCREEN_WIDTH - btn_w) // 2
        start_y = 220
        spacing = 66

        self.btn_start = Button(
            rect=(cx, start_y, btn_w, btn_h),
            text="Start Game Quest",
            font=font,
            theme=BTN_SUCCESS,
            on_click=self._start_game
        )

        self.btn_leaderboard = Button(
            rect=(cx, start_y + spacing, btn_w, btn_h),
            text="Global Leaderboard",
            font=font,
            theme=BTN_PRIMARY,
            on_click=lambda: self.manager.change_screen("leaderboard")
        )

        self.btn_profile = Button(
            rect=(cx, start_y + spacing * 2, btn_w, btn_h),
            text="My Profile & Stats",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("profile")
        )

        self.btn_instructions = Button(
            rect=(cx, start_y + spacing * 3, btn_w, btn_h),
            text="Game Instructions",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("instructions")
        )

        self.btn_logout = Button(
            rect=(cx, start_y + spacing * 4, btn_w, btn_h),
            text="Logout",
            font=font,
            theme=BTN_DANGER,
            on_click=self._logout
        )

        self.buttons = [
            self.btn_start,
            self.btn_leaderboard,
            self.btn_profile,
            self.btn_instructions,
            self.btn_logout
        ]

    def _start_game(self) -> None:
        """Starts a new game session in GameManager and navigates to Gameplay."""
        self.manager.game_manager.start_game()
        self.manager.change_screen("gameplay")

    def _logout(self) -> None:
        """Logs out active user and returns to Welcome screen."""
        self.auth.logout()
        self.manager.change_screen("welcome")

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        # Route protection: verify virtual identity
        if not self.auth.is_authenticated:
            self.manager.change_screen("login", {"msg": "Please login to access the menu."})
            return
        self.auth.refresh_current_user()

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        card_w, card_h = 460, 580
        card_rect = pygame.Rect(
            (SCREEN_WIDTH - card_w) // 2,
            50,
            card_w,
            card_h
        )
        self.draw_glass_card(surface, card_rect, border_radius=20)

        # Welcome Header displaying authenticated virtual identity
        username = self.auth.current_username
        welcome_title = f"Welcome, {username}!"
        self.draw_header(surface, welcome_title, "Ready to explore the ocean depths?", y=95)

        # Status Pill Bar: High Score & Coins
        pill_w, pill_h = 360, 42
        pill_rect = pygame.Rect((SCREEN_WIDTH - pill_w) // 2, 145, pill_w, pill_h)
        pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pygame.draw.rect(pill_surf, (15, 35, 70, 180), pill_surf.get_rect(), border_radius=21)
        pygame.draw.rect(pill_surf, (56, 189, 248, 120), pill_surf.get_rect(), width=1, border_radius=21)
        surface.blit(pill_surf, pill_rect.topleft)

        curr = self.auth.current_user or {}
        high_score = curr.get("highest_score", 0)
        total_coins = curr.get("total_coins", 0)

        badge_font = self.fonts["small"]
        hs_text = badge_font.render(f"Best: {high_score} pts", True, COLOR_AQUA_ACCENT)
        surface.blit(hs_text, (pill_rect.x + 30, pill_rect.y + 11))

        if self.coin_icon:
            surface.blit(self.coin_icon, (pill_rect.right - 140, pill_rect.y + 7))
        coins_text = badge_font.render(f"{total_coins} Coins", True, COLOR_GOLD)
        surface.blit(coins_text, (pill_rect.right - 105, pill_rect.y + 11))

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)

