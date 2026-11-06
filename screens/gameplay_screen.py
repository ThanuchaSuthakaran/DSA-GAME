"""
Fish Quest - Ocean Adventure Game
Gameplay Screen Module

Demonstrates:
- External API Interoperability:
  Displays the live puzzle image retrieved from the official Fish Game API.
- Event-Driven Programming:
  Handles keyboard text entries, enter submissions, button clicks, and timer ticks.
- Dynamic HUD:
  Renders lives with heart icons, coins, score, difficulty level, and a dynamic timer bar.
- State Machine Integration:
  Renders LOADING, ACTIVE, FEEDBACK, PAUSED, and ERROR overlays smoothly.
"""

from typing import Optional, Dict, Any
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.text_input import TextInput
from game.game_manager import GameState
from config.settings import (
    BTN_PRIMARY,
    BTN_SUCCESS,
    BTN_DANGER,
    BTN_SECONDARY,
    BTN_WARNING,
    COLOR_AQUA_ACCENT,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_SUCCESS_GREEN,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_OVERLAY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    IMAGES_DIR
)


class GameplayScreen(BaseScreen):
    """
    Main interactive gameplay screen where the player views the API puzzle,
    submits numerical answers, and receives immediate visual feedback.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.game = manager.game_manager
        self.heart_icon: Optional[pygame.Surface] = None
        self.coin_icon: Optional[pygame.Surface] = None
        self._cached_puzzle_surface: Optional[pygame.Surface] = None
        self._cached_puzzle_ref: Optional[Any] = None

        self._load_assets()
        self._init_ui()

    def _load_assets(self) -> None:
        heart_path = IMAGES_DIR / "heart.png"
        coin_path = IMAGES_DIR / "coin.png"
        try:
            if heart_path.exists():
                raw = pygame.image.load(str(heart_path)).convert_alpha()
                self.heart_icon = pygame.transform.smoothscale(raw, (26, 26))
            if coin_path.exists():
                raw = pygame.image.load(str(coin_path)).convert_alpha()
                self.coin_icon = pygame.transform.smoothscale(raw, (26, 26))
        except Exception as e:
            print(f"[Asset Warning] Failed loading HUD icons: {e}")

    def _init_ui(self) -> None:
        font = self.fonts["normal"]
        font_lg = self.fonts["large"]

        # Answer Input Field
        input_w, input_h = 160, 48
        input_x = (SCREEN_WIDTH - input_w) // 2 - 90
        input_y = 520

        self.input_answer = TextInput(
            rect=(input_x, input_y, input_w, input_h),
            font=font_lg,
            placeholder="Answer",
            numeric_only=True,
            max_length=4,
            on_submit=self._submit_answer
        )

        # Submit Button
        self.btn_submit = Button(
            rect=(input_x + input_w + 16, input_y, 160, input_h),
            text="Submit Answer",
            font=font,
            theme=BTN_SUCCESS,
            on_click=lambda: self._submit_answer(self.input_answer.text)
        )

        # Next Question Button (shown during FEEDBACK state)
        self.btn_next = Button(
            rect=((SCREEN_WIDTH - 200) // 2, input_y, 200, input_h),
            text="Next Question ▶",
            font=font,
            theme=BTN_PRIMARY,
            on_click=self._next_question
        )

        # Pause & Exit HUD Buttons (top right)
        self.btn_pause = Button(
            rect=(SCREEN_WIDTH - 190, 16, 80, 36),
            text="Pause",
            font=self.fonts["small"],
            theme=BTN_SECONDARY,
            on_click=self._toggle_pause
        )

        self.btn_exit_hud = Button(
            rect=(SCREEN_WIDTH - 100, 16, 80, 36),
            text="Exit",
            font=self.fonts["small"],
            theme=BTN_DANGER,
            on_click=self._confirm_exit
        )

        # Pause Overlay Buttons
        overlay_cx = SCREEN_WIDTH // 2 - 120
        self.btn_resume = Button(
            rect=(overlay_cx, 320, 240, 48),
            text="Resume Game",
            font=font,
            theme=BTN_SUCCESS,
            on_click=self._toggle_pause
        )

        self.btn_quit_to_menu = Button(
            rect=(overlay_cx, 385, 240, 48),
            text="Quit to Main Menu",
            font=font,
            theme=BTN_DANGER,
            on_click=self._quit_to_menu
        )

        # Error Overlay Buttons
        self.btn_retry = Button(
            rect=(overlay_cx, 360, 240, 48),
            text="Retry API Request",
            font=font,
            theme=BTN_PRIMARY,
            on_click=lambda: self.game.load_next_puzzle()
        )

    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        if not self.auth.is_authenticated:
            self.manager.change_screen("login", {"msg": "Please login to play."})
            return

        self.input_answer.clear()
        self.input_answer.is_focused = True
        self._cached_puzzle_surface = None
        self._cached_puzzle_ref = None

    def _submit_answer(self, text: str) -> None:
        if self.game.state == GameState.ACTIVE:
            self.game.submit_answer(text)

    def _next_question(self) -> None:
        self.input_answer.clear()
        self.input_answer.is_focused = True
        self.game.load_next_puzzle()

    def _toggle_pause(self) -> None:
        self.game.toggle_pause()

    def _confirm_exit(self) -> None:
        self.game.pause_game()
        # Direct quit or confirm
        self._quit_to_menu()

    def _quit_to_menu(self) -> None:
        self.game.timer.stop()
        self.manager.change_screen("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        state = self.game.state

        if state == GameState.PAUSED:
            self.btn_resume.handle_event(event)
            self.btn_quit_to_menu.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._toggle_pause()
            return

        if state == GameState.ERROR:
            self.btn_retry.handle_event(event)
            self.btn_quit_to_menu.handle_event(event)
            return

        # Top bar buttons
        self.btn_pause.handle_event(event)
        self.btn_exit_hud.handle_event(event)

        # Space or Enter in feedback advances to next question
        if state == GameState.FEEDBACK:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._next_question()
                return
            self.btn_next.handle_event(event)
            return

        # Active state controls
        if state == GameState.ACTIVE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._toggle_pause()
                return
            self.input_answer.handle_event(event)
            self.btn_submit.handle_event(event)

    def update(self, dt: float) -> None:
        self.game.update()

        # Check for game over trigger
        if self.game.state == GameState.GAME_OVER:
            summary = self.game.score_mgr.get_summary()
            self.manager.change_screen("results", summary)

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_hud(surface)

        state = self.game.state
        if state == GameState.LOADING:
            self._draw_loading_view(surface)
        elif state == GameState.ERROR:
            self._draw_error_view(surface)
        elif state in (GameState.ACTIVE, GameState.FEEDBACK, GameState.PAUSED):
            self._draw_puzzle_area(surface)
            self._draw_interaction_area(surface)
            if state == GameState.PAUSED:
                self._draw_pause_overlay(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        """Renders top header with score, level, lives, coins, and timer."""
        # Top HUD bar
        hud_h = 60
        hud_surf = pygame.Surface((SCREEN_WIDTH, hud_h), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (8, 20, 42, 220), (0, 0, SCREEN_WIDTH, hud_h))
        pygame.draw.line(hud_surf, (56, 189, 248, 80), (0, hud_h - 1), (SCREEN_WIDTH, hud_h - 1), 1)
        surface.blit(hud_surf, (0, 0))

        font = self.fonts["normal"]
        sm_font = self.fonts["small"]

        # Player Virtual Identity name
        username = self.auth.current_username
        user_surf = font.render(f"Player: {username}", True, COLOR_TEXT_PRIMARY)
        surface.blit(user_surf, (20, 16))

        # Score & Level
        score_surf = font.render(f"Score: {self.game.score_mgr.score}", True, COLOR_AQUA_ACCENT)
        surface.blit(score_surf, (210, 16))

        lvl_surf = sm_font.render(f"Level {self.game.score_mgr.current_level}", True, COLOR_TEXT_SECONDARY)
        surface.blit(lvl_surf, (340, 20))

        # Coins
        if self.coin_icon:
            surface.blit(self.coin_icon, (430, 17))
        coins_surf = font.render(str(self.game.score_mgr.coins), True, COLOR_GOLD)
        surface.blit(coins_surf, (462, 16))

        # Lives
        lives_start_x = 540
        for i in range(self.game.score_mgr.initial_lives):
            if i < self.game.score_mgr.lives:
                if self.heart_icon:
                    surface.blit(self.heart_icon, (lives_start_x + i * 32, 17))
                else:
                    heart_txt = font.render("♥", True, COLOR_CORAL_RED)
                    surface.blit(heart_txt, (lives_start_x + i * 32, 16))
            else:
                # Dimmed lost life
                lost_txt = font.render("♡", True, (100, 116, 139))
                surface.blit(lost_txt, (lives_start_x + i * 32, 16))

        # HUD Buttons
        self.btn_pause.draw(surface)
        self.btn_exit_hud.draw(surface)

        # Countdown Timer Bar (directly under HUD)
        if self.game.state in (GameState.ACTIVE, GameState.FEEDBACK):
            timer_w = SCREEN_WIDTH
            timer_h = 5
            progress = self.game.timer.progress_ratio
            bar_color = COLOR_AQUA_ACCENT if progress > 0.4 else (COLOR_GOLD if progress > 0.2 else COLOR_CORAL_RED)

            pygame.draw.rect(surface, (20, 30, 50), (0, hud_h, timer_w, timer_h))
            pygame.draw.rect(surface, bar_color, (0, hud_h, int(timer_w * progress), timer_h))

    def _draw_puzzle_area(self, surface: pygame.Surface) -> None:
        """Renders the retrieved external API puzzle image inside an ocean frame."""
        puzzle = self.game.current_puzzle
        if not puzzle:
            return

        frame_w, frame_h = 680, 380
        frame_x = (SCREEN_WIDTH - frame_w) // 2
        frame_y = 80
        frame_rect = pygame.Rect(frame_x, frame_y, frame_w, frame_h)

        # Outer card frame
        self.draw_glass_card(surface, frame_rect, border_radius=16)

        # Prompt Banner above image
        prompt_font = self.fonts["normal"]
        prompt_text = "Count the fish in the ocean puzzle:"
        prompt_surf = prompt_font.render(prompt_text, True, COLOR_AQUA_ACCENT)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, frame_y + 24))
        surface.blit(prompt_surf, prompt_rect)

        # Prepare scaled surface
        if puzzle.image_surface:
            if self._cached_puzzle_ref != puzzle:
                orig_w, orig_h = puzzle.image_surface.get_size()
                target_w, target_h = 620, 310
                scale_factor = min(target_w / orig_w, target_h / orig_h)
                new_size = (int(orig_w * scale_factor), int(orig_h * scale_factor))
                self._cached_puzzle_surface = pygame.transform.smoothscale(puzzle.image_surface, new_size)
                self._cached_puzzle_ref = puzzle

            if self._cached_puzzle_surface:
                img_rect = self._cached_puzzle_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, frame_y + 40 + (frame_h - 40) // 2)
                )
                # Background matte for contrast
                matte_rect = img_rect.inflate(8, 8)
                pygame.draw.rect(surface, (255, 255, 255), matte_rect, border_radius=8)
                surface.blit(self._cached_puzzle_surface, img_rect)

        # Timer countdown badge (top right of puzzle card)
        sec_left = self.game.timer.seconds_left
        timer_badge = f"{sec_left}s"
        t_color = COLOR_CORAL_RED if sec_left <= 5 else COLOR_TEXT_PRIMARY
        badge_surf = self.fonts["normal"].render(timer_badge, True, t_color)
        surface.blit(badge_surf, (frame_rect.right - 55, frame_y + 14))

    def _draw_interaction_area(self, surface: pygame.Surface) -> None:
        """Renders input field, submit button, or feedback notification."""
        state = self.game.state

        if state == GameState.ACTIVE:
            self.input_answer.draw(surface)
            self.btn_submit.draw(surface)

            # Keyboard shortcut hint
            hint_font = self.fonts["tiny"]
            hint_surf = hint_font.render("Type number and press Enter or Click Submit", True, COLOR_TEXT_SECONDARY)
            hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, 585))
            surface.blit(hint_surf, hint_rect)

        elif state == GameState.FEEDBACK:
            fb = self.game.feedback_info or {}
            is_correct = fb.get("correct", False)
            msg = fb.get("message", "")

            # Feedback banner
            banner_w, banner_h = 680, 52
            banner_rect = pygame.Rect((SCREEN_WIDTH - banner_w) // 2, 470, banner_w, banner_h)

            banner_bg = (16, 185, 129, 210) if is_correct else (239, 68, 68, 210)
            banner_border = (110, 231, 183) if is_correct else (252, 165, 165)

            self.draw_glass_card(
                surface,
                banner_rect,
                border_radius=12,
                bg_color=banner_bg,
                border_color=banner_border
            )

            msg_font = self.fonts["normal"]
            msg_surf = msg_font.render(msg, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=banner_rect.center)
            surface.blit(msg_surf, msg_rect)

            # Next Question button
            self.btn_next.rect.centery = 555
            self.btn_next.draw(surface)

    def _draw_loading_view(self, surface: pygame.Surface) -> None:
        """Renders a friendly non-blocking loading notification."""
        box_w, box_h = 520, 220
        box_rect = pygame.Rect((SCREEN_WIDTH - box_w) // 2, 220, box_w, box_h)
        self.draw_glass_card(surface, box_rect, border_radius=16)

        title_surf = self.fonts["large"].render("Retrieving Puzzle...", True, COLOR_TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 280))
        surface.blit(title_surf, title_rect)

        sub_surf = self.fonts["small"].render(
            "Connecting to external Fish Game API (marcconrad.com)",
            True,
            COLOR_AQUA_ACCENT
        )
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 330))
        surface.blit(sub_surf, sub_rect)

        # Pulse or subtext
        pulse_surf = self.fonts["tiny"].render(
            "Non-blocking background HTTP request in progress...",
            True,
            COLOR_TEXT_SECONDARY
        )
        pulse_rect = pulse_surf.get_rect(center=(SCREEN_WIDTH // 2, 375))
        surface.blit(pulse_surf, pulse_rect)

    def _draw_error_view(self, surface: pygame.Surface) -> None:
        """Renders connection error diagnostics with retry options."""
        box_w, box_h = 600, 280
        box_rect = pygame.Rect((SCREEN_WIDTH - box_w) // 2, 190, box_w, box_h)
        self.draw_glass_card(
            surface,
            box_rect,
            border_radius=16,
            bg_color=(35, 15, 25, 235),
            border_color=COLOR_CORAL_RED
        )

        err_title = self.fonts["large"].render("API Connection Error", True, COLOR_CORAL_RED)
        surface.blit(err_title, err_title.get_rect(center=(SCREEN_WIDTH // 2, 230)))

        err_detail = self.game.error_message or "An unexpected network error occurred."
        detail_surf = self.fonts["small"].render(err_detail[:65], True, COLOR_TEXT_PRIMARY)
        surface.blit(detail_surf, detail_surf.get_rect(center=(SCREEN_WIDTH // 2, 285)))

        self.btn_retry.draw(surface)
        self.btn_quit_to_menu.rect.y = 415
        self.btn_quit_to_menu.draw(surface)

    def _draw_pause_overlay(self, surface: pygame.Surface) -> None:
        """Renders semi-transparent pause menu overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        surface.blit(overlay, (0, 0))

        dialog_w, dialog_h = 380, 260
        dialog_rect = pygame.Rect((SCREEN_WIDTH - dialog_w) // 2, 200, dialog_w, dialog_h)
        self.draw_glass_card(surface, dialog_rect, border_radius=20)

        title = self.fonts["title"].render("GAME PAUSED", True, COLOR_TEXT_PRIMARY)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 255)))

        self.btn_resume.draw(surface)
        self.btn_quit_to_menu.rect.y = 385
        self.btn_quit_to_menu.draw(surface)

