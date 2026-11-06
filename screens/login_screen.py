"""
Fish Quest - Ocean Adventure Game
Login Screen Module

Demonstrates:
- Virtual Identity Authentication:
  Verifies player credentials against securely hashed PBKDF2 records.
  Establishes active user session in AuthManager.
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


class LoginScreen(BaseScreen):
    """
    Player Login screen to authenticate the player's virtual identity.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.message = ""
        self.is_success = False

        self._init_inputs()
        self._init_buttons()

    def _init_inputs(self) -> None:
        font = self.fonts["normal"]
        input_w, input_h = 320, 46
        cx = (SCREEN_WIDTH - input_w) // 2
        start_y = 190
        spacing = 80

        self.input_username = TextInput(
            rect=(cx, start_y, input_w, input_h),
            font=font,
            placeholder="Enter your username",
            max_length=20
        )

        self.input_password = TextInput(
            rect=(cx, start_y + spacing, input_w, input_h),
            font=font,
            placeholder="Enter your password",
            is_password=True,
            max_length=30,
            on_submit=lambda _: self._on_login()
        )

        self.inputs = [self.input_username, self.input_password]

    def _init_buttons(self) -> None:
        font = self.fonts["normal"]
        btn_w, btn_h = 320, 48
        cx = (SCREEN_WIDTH - btn_w) // 2
        btn_y = 380

        self.btn_login = Button(
            rect=(cx, btn_y, btn_w, btn_h),
            text="Login",
            font=font,
            theme=BTN_PRIMARY,
            on_click=self._on_login
        )

        self.btn_register_prompt = Button(
            rect=(cx, btn_y + 60, btn_w, btn_h),
            text="Need an Account? Register",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("register")
        )

        self.btn_back = Button(
            rect=(cx, btn_y + 120, btn_w, btn_h),
            text="Back to Welcome",
            font=font,
            theme=BTN_SECONDARY,
            on_click=lambda: self.manager.change_screen("welcome")
        )

        self.buttons = [self.btn_login, self.btn_register_prompt, self.btn_back]

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        self.message = ""
        self.is_success = False
        self.input_password.clear()

        if params:
            if "prefill_user" in params:
                self.input_username.set_text(params["prefill_user"])
                self.input_password.is_focused = True
            else:
                self.input_username.is_focused = True
            if "msg" in params:
                self.message = params["msg"]
                self.is_success = True
        else:
            self.input_username.is_focused = True

    def _on_login(self) -> None:
        username = self.input_username.text
        password = self.input_password.text

        success, msg = self.auth.login(username, password)
        self.message = msg
        self.is_success = success

        if success:
            # Transition to Main Menu upon successful authentication
            self.manager.schedule_action(
                delay_seconds=0.6,
                action=lambda: self.manager.change_screen("menu")
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        # Tab cycling between username and password
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if self.input_username.is_focused:
                self.input_username.is_focused = False
                self.input_password.is_focused = True
            else:
                self.input_password.is_focused = False
                self.input_username.is_focused = True
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
        self.draw_header(surface, "Player Login", "Sign in to access your ocean quest", y=105)

        # Labels
        label_font = self.fonts["small"]
        cx = (SCREEN_WIDTH - 320) // 2

        lbl_user = label_font.render("Username:", True, COLOR_TEXT_SECONDARY)
        surface.blit(lbl_user, (cx, 166))

        lbl_pass = label_font.render("Password:", True, COLOR_TEXT_SECONDARY)
        surface.blit(lbl_pass, (cx, 246))

        # Inputs
        for inp in self.inputs:
            inp.draw(surface)

        # Status / Feedback Message
        if self.message:
            msg_color = COLOR_SUCCESS_GREEN if self.is_success else COLOR_CORAL_RED
            msg_font = self.fonts["small"]
            msg_surf = msg_font.render(self.message, True, msg_color)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 345))
            surface.blit(msg_surf, msg_rect)

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)

