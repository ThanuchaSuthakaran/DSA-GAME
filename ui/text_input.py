"""
Fish Quest - Ocean Adventure Game
Interactive UI Text Input Component

Demonstrates:
- Event-Driven Programming:
  Captures keyboard strokes, backspaces, enter submissions, and mouse focus events.
- Cohesion and Encapsulation:
  Encapsulates cursor blinking, text truncation, password masking, and numeric filtering.
"""

import time
from typing import Optional, Callable, Tuple
import pygame
from config.settings import (
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_INPUT_FOCUS,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED
)


class TextInput:
    """
    A full-featured text input box supporting focus, cursor rendering,
    character filtering, password masking, and Enter submission.
    """

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        font: pygame.font.Font,
        placeholder: str = "",
        is_password: bool = False,
        numeric_only: bool = False,
        max_length: int = 30,
        on_submit: Optional[Callable[[str], None]] = None,
        border_radius: int = 10
    ):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.is_password = is_password
        self.numeric_only = numeric_only
        self.max_length = max_length
        self.on_submit = on_submit
        self.border_radius = border_radius

        self.text = ""
        self.is_focused = False
        self._cursor_visible = True
        self._cursor_timer = time.time()

    def set_text(self, text: str) -> None:
        """Sets text programmatically."""
        self.text = text[:self.max_length]

    def clear(self) -> None:
        """Clears current text input."""
        self.text = ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Processes mouse and keyboard events.
        Returns True if Enter was pressed and input submitted.
        """
        # Mouse Click for Focus
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_focused = self.rect.collidepoint(event.pos)
            self._cursor_visible = True
            self._cursor_timer = time.time()
            return False

        # Keyboard Input
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.on_submit:
                    self.on_submit(self.text)
                return True

            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_TAB:
                # Let parent screen handle tab focus
                return False

            elif event.unicode:
                char = event.unicode
                # Check character filtering
                if self.numeric_only:
                    if not char.isdigit():
                        return False

                if len(self.text) < self.max_length and char.isprintable():
                    self.text += char

            # Reset cursor blink on keystroke
            self._cursor_visible = True
            self._cursor_timer = time.time()

        return False

    def update(self) -> None:
        """Updates the blinking cursor animation."""
        if time.time() - self._cursor_timer > 0.5:
            self._cursor_visible = not self._cursor_visible
            self._cursor_timer = time.time()

    def draw(self, surface: pygame.Surface) -> None:
        """Renders input field, border, text, and blinking cursor."""
        self.update()

        # Background
        pygame.draw.rect(
            surface,
            COLOR_INPUT_BG,
            self.rect,
            border_radius=self.border_radius
        )

        # Border (highlighted if focused)
        border_color = COLOR_INPUT_FOCUS if self.is_focused else COLOR_INPUT_BORDER
        border_width = 2 if self.is_focused else 1
        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            width=border_width,
            border_radius=self.border_radius
        )

        # Determine display text
        display_str = self.text
        if self.is_password and self.text:
            display_str = "•" * len(self.text)

        padding_x = 12
        if display_str:
            txt_surf = self.font.render(display_str, True, COLOR_TEXT_PRIMARY)
        elif not self.is_focused and self.placeholder:
            txt_surf = self.font.render(self.placeholder, True, COLOR_TEXT_MUTED)
        else:
            txt_surf = None

        text_y = self.rect.centery - (self.font.get_height() // 2)

        if txt_surf:
            surface.blit(txt_surf, (self.rect.x + padding_x, text_y))
            rendered_width = txt_surf.get_width()
        else:
            rendered_width = 0

        # Blinking cursor
        if self.is_focused and self._cursor_visible:
            cursor_x = self.rect.x + padding_x + rendered_width + 2
            cursor_top = self.rect.centery - (self.font.get_height() // 2) + 2
            cursor_bottom = cursor_top + self.font.get_height() - 4
            pygame.draw.line(
                surface,
                COLOR_INPUT_FOCUS,
                (cursor_x, cursor_top),
                (cursor_x, cursor_bottom),
                width=2
            )

