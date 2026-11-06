"""
Fish Quest - Ocean Adventure Game
Base Screen Abstract Class

Demonstrates:
- Object-Oriented Design & High Cohesion:
  Provides common lifecycle methods (on_enter, handle_event, update, draw, on_exit)
  and reusable UI helper routines across all game screens.
"""

from typing import Optional, Any, Dict
import pygame
from config.settings import (
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_AQUA_ACCENT
)


class BaseScreen:
    """
    Abstract base class for all game screens.
    Enforces consistent lifecycle, event handling, and rendering hooks.
    """

    def __init__(self, manager: Any):
        self.manager = manager
        self.fonts = manager.fonts
        self.auth = manager.auth
        self.db = manager.db

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        """Invoked when transitioning into this screen."""
        pass

    def on_exit(self) -> None:
        """Invoked when transitioning away from this screen."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handles Pygame input events."""
        pass

    def update(self, dt: float) -> None:
        """Updates screen logic, animations, and timers."""
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Renders screen contents onto the main surface."""
        pass

    # Helper UI drawing methods
    def draw_glass_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        border_radius: int = 16,
        bg_color=COLOR_CARD_BG,
        border_color=COLOR_CARD_BORDER,
        border_width: int = 2
    ) -> None:
        """Draws a modern translucent glassmorphic card with a subtle glow border."""
        card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            card_surf,
            bg_color,
            card_surf.get_rect(),
            border_radius=border_radius
        )
        pygame.draw.rect(
            card_surf,
            border_color,
            card_surf.get_rect(),
            width=border_width,
            border_radius=border_radius
        )
        surface.blit(card_surf, rect.topleft)

    def draw_header(
        self,
        surface: pygame.Surface,
        title: str,
        subtitle: Optional[str] = None,
        y: int = 40
    ) -> None:
        """Renders standard centered header typography."""
        title_font = self.fonts["large"]
        title_surf = title_font.render(title, True, COLOR_TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(surface.get_width() // 2, y))
        surface.blit(title_surf, title_rect)

        if subtitle:
            sub_font = self.fonts["small"]
            sub_surf = sub_font.render(subtitle, True, COLOR_AQUA_ACCENT)
            sub_rect = sub_surf.get_rect(center=(surface.get_width() // 2, y + 36))
            surface.blit(sub_surf, sub_rect)

