"""
Fish Quest - Ocean Adventure Game
Interactive UI Button Component

Demonstrates:
- Event-Driven Programming:
  Handles mouse movements (hover states) and click events with visual feedback.
- Reusable UI Widget:
  Supports color schemes, rounded corners, icons, disabled states, and callbacks.
"""

from typing import Optional, Callable, Tuple, Dict
import pygame
from config.settings import BTN_PRIMARY, COLOR_TEXT_MUTED


class Button:
    """
    A customizable, event-driven Pygame button with hover effects and animations.
    """

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        font: pygame.font.Font,
        theme: Dict[str, Tuple[int, int, int]] = BTN_PRIMARY,
        on_click: Optional[Callable[[], None]] = None,
        border_radius: int = 12,
        enabled: bool = True
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.theme = theme
        self.on_click = on_click
        self.border_radius = border_radius
        self.enabled = enabled

        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Processes a Pygame event. Returns True if the button was activated (clicked).
        """
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.on_click:
                    self.on_click()
                return True
            self.is_pressed = False

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Renders button onto target surface with theme styling."""
        if not self.enabled:
            bg_color = (40, 50, 70)
            text_color = COLOR_TEXT_MUTED
            border_color = (60, 70, 90)
        elif self.is_pressed:
            bg_color = self.theme.get("pressed", self.theme["normal"])
            text_color = self.theme["text"]
            border_color = self.theme["border"]
        elif self.is_hovered:
            bg_color = self.theme.get("hover", self.theme["normal"])
            text_color = self.theme["text"]
            border_color = self.theme["border"]
        else:
            bg_color = self.theme["normal"]
            text_color = self.theme["text"]
            border_color = self.theme["border"]

        # Background fill
        pygame.draw.rect(
            surface,
            bg_color,
            self.rect,
            border_radius=self.border_radius
        )

        # Highlight top glow border if hovered
        border_width = 2 if self.is_hovered else 1
        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            width=border_width,
            border_radius=self.border_radius
        )

        # Text label
        txt_surf = self.font.render(self.text, True, text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

