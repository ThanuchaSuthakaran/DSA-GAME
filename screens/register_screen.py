"""
Fish Quest - Ocean Adventure Game
Registration Screen Module

Demonstrates:
- Virtual Identity Creation:
  Collects player credentials, validates rules, hashes password with PBKDF2 salt,
  and securely creates the persistent player account in SQLite.
- Event-Driven Input:
  Supports Tab navigation, enter submissions, and real-time validation error alerts.
"""

from typing import Optional, Dict, Any
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.text_input import TextInput
from config.settings import (
    BTN_PRIMARY,
    BTN_SECONDARY,
    COLOR_SUCCESS_GREEN,
    COLOR_CORAL_RED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SCREEN_WIDTH
)


class RegisterScreen(BaseScreen):
    """
    Player Registration screen to establish a new virtual identity.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.message = ""
        self.is_success = False

        self._init_inputs()
        self._init_buttons()

    def _init_inputs(self) -> None:
        font = self.fonts["normal"]
        input_w, input_h = 320, 44
        cx = (SCREEN_WIDTH - input_w) // 2
        start_y = 160
        spacing = 70

        self.input_username = TextInput(
            rect=(cx, start_y, input_w, input_h),
            font=font,
            placeholder="Choose username (3-20 chars)",
            max_length=20
        )

        self.input_password = TextInput(
            rect=(cx, start_y + spacing, input_w, input_h),
            font=font,
            placeholder="Choose password (min 4 chars)",
            is_password=True,
            max_length=30
        )

        self.input_confirm = TextInput(
            rect=(cx, start_y + spacing * 2, input_w, input_h),
            font=font,
            placeholder="Confirm password",
            is_password=True,
            max_length=30,
            on_submit=lambda _: self._on_register()
        )

        self.inputs = [self.input_username, self.input_password, self.input_confirm]

    def _init_buttons(self) -> None:
        font = self.fonts["normal"]
        btn_w, btn_h = 320, 48
        cx = (SCREEN_WIDTH - btn_w) // 2
        btn_y = 390

        self.btn_register = Button(
            rect=(cx, btn_y, btn_w, btn_h),
            text="Create Virtual Identity",
            font=font,
            theme=BTN_PRIMARY,
            on_click=self._on_register
        )

        self.btn_back = Button(
            rect=(cx, btn_y + 60, btn_w, btn_h),
            text="Back to Welcome",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("welcome")
        )

        self.buttons = [self.btn_register, self.btn_back]

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        self.message = ""
        self.is_success = False
        for inp in self.inputs:
            inp.clear()
        self.input_username.is_focused = True

    def _on_register(self) -> None:
        username = self.input_username.text
        password = self.input_password.text
        confirm = self.input_confirm.text

        success, msg = self.auth.register(username, password, confirm)
        self.message = msg
        self.is_success = success

        if success:
            # Auto log in the player or prompt to log in
            # Direct them to login screen with prefilled message
            self.manager.schedule_action(
                delay_seconds=1.2,
                action=lambda: self.manager.change_screen("login", {"prefill_user": username, "msg": "Registration complete! Please log in."})
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        # Tab cycling across input fields
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            idx = 0
            for i, inp in enumerate(self.inputs):
                if inp.is_focused:
                    inp.is_focused = False
                    idx = (i + 1) % len(self.inputs)
                    break
            self.inputs[idx].is_focused = True
            return

        for inp in self.inputs:
            inp.handle_event(event)

        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        # Outer Card Container
        card_w, card_h = 440, 560
        card_rect = pygame.Rect(
            (SCREEN_WIDTH - card_w) // 2,
            55,
            card_w,
            card_h
        )
        self.draw_glass_card(surface, card_rect, border_radius=20)

        # Header
        self.draw_header(surface, "Player Registration", "Create your underwater Virtual Identity", y=95)

        # Labels for Inputs
        label_font = self.fonts["small"]
        cx = (SCREEN_WIDTH - 320) // 2

        lbl_user = label_font.render("Username:", True, COLOR_TEXT_SECONDARY)
        surface.blit(lbl_user, (cx, 138))

        lbl_pass = label_font.render("Password:", True, COLOR_TEXT_SECONDARY)
        surface.blit(lbl_pass, (cx, 208))

        lbl_conf = label_font.render("Confirm Password:", True, COLOR_TEXT_SECONDARY)
        surface.blit(lbl_conf, (cx, 278))

        # Inputs
        for inp in self.inputs:
            inp.draw(surface)

        # Status / Feedback Message
        if self.message:
            msg_color = COLOR_SUCCESS_GREEN if self.is_success else COLOR_CORAL_RED
            msg_font = self.fonts["small"]
            msg_surf = msg_font.render(self.message, True, msg_color)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 360))
            surface.blit(msg_surf, msg_rect)

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)

