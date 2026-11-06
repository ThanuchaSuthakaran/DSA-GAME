"""
Fish Quest - Ocean Adventure Game
Welcome Screen Module

Displays:
- Game Title and Logo
- Play, Login, Register, Instructions, and Exit buttons.
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
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    IMAGES_DIR
)


class WelcomeScreen(BaseScreen):
    """
    Main entry screen welcoming the player to Fish Quest.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.buttons = []
        self.fish_icon: Optional[pygame.Surface] = None
        self._load_assets()
        self._init_buttons()

    def _load_assets(self) -> None:
        icon_path = IMAGES_DIR / "fish_icon.png"
        if icon_path.exists():
            try:
                raw_icon = pygame.image.load(str(icon_path)).convert_alpha()
                self.fish_icon = pygame.transform.smoothscale(raw_icon, (140, 96))
            except Exception as e:
                print(f"[Asset Warning] Could not load fish icon: {e}")

    def _init_buttons(self) -> None:
        btn_w, btn_h = 240, 50
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 280
        spacing = 64

        font = self.fonts["normal"]

        self.btn_play = Button(
            rect=(cx, start_y, btn_w, btn_h),
            text="Play Game",
            font=font,
            theme=BTN_SUCCESS,
            on_click=self._on_play
        )

        self.btn_login = Button(
            rect=(cx, start_y + spacing, btn_w, btn_h),
            text="Login",
            font=font,
            theme=BTN_PRIMARY,
            on_click=lambda: self.manager.change_screen("login")
        )

        self.btn_register = Button(
            rect=(cx, start_y + spacing * 2, btn_w, btn_h),
            text="Register",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("register")
        )

        self.btn_instructions = Button(
            rect=(cx, start_y + spacing * 3, btn_w, btn_h),
            text="Instructions",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("instructions")
        )

        self.btn_exit = Button(
            rect=(cx, start_y + spacing * 4, btn_w, btn_h),
            text="Exit Game",
            font=font,
            theme=BTN_DANGER,
            on_click=lambda: self.manager.quit_game()
        )

        self.buttons = [
            self.btn_play,
            self.btn_login,
            self.btn_register,
            self.btn_instructions,
            self.btn_exit
        ]

    def _on_play(self) -> None:
        """Route to main menu if authenticated, or login prompt if unauthenticated."""
        if self.auth.is_authenticated:
            self.manager.change_screen("menu")
        else:
            # If not logged in, direct to login screen to authenticate virtual identity
            self.manager.change_screen("login")

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        # Update Play button label dynamically
        if self.auth.is_authenticated:
            self.btn_play.text = "Continue as " + self.auth.current_username
        else:
            self.btn_play.text = "Play Game"

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        # Outer Card Container
        card_w, card_h = 440, 580
        card_rect = pygame.Rect(
            (SCREEN_WIDTH - card_w) // 2,
            50,
            card_w,
            card_h
        )
        self.draw_glass_card(surface, card_rect, border_radius=20)

        # Title & Subtitle
        title_font = self.fonts["title"]
        title_surf = title_font.render("FISH QUEST", True, COLOR_TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 95))
        surface.blit(title_surf, title_rect)

        sub_font = self.fonts["small"]
        sub_surf = sub_font.render("OCEAN ADVENTURE", True, COLOR_AQUA_ACCENT)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(sub_surf, sub_rect)

        # Fish Icon
        if self.fish_icon:
            icon_rect = self.fish_icon.get_rect(center=(SCREEN_WIDTH // 2, 200))
            surface.blit(self.fish_icon, icon_rect)

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Version & University Module Notice
        info_font = self.fonts["tiny"]
        info_surf = info_font.render("CIS045-3 Distributed Service Architectures | v1.0", True, COLOR_TEXT_SECONDARY)
        info_rect = info_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        surface.blit(info_surf, info_rect)

