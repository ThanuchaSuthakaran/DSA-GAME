"""
Fish Quest - Ocean Adventure Game
Screen Manager Module

Demonstrates:
- Low Coupling and High Cohesion:
  Manages UI transitions between decoupled screen instances while maintaining
  shared services (Auth, Database, Game Manager, Fonts, Particle Ambience).
- Event-Driven Architecture:
  Routes Pygame events directly to the currently active screen.
"""

import time
from typing import Dict, Any, Optional, Callable, List
import pygame

from database.db_manager import DatabaseManager
from authentication.auth_manager import AuthManager
from game.game_manager import GameManager
from ui.particles import BubbleParticleSystem
from config.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BACKGROUNDS_DIR,
    COLOR_OCEAN_NAVY
)

from screens.welcome_screen import WelcomeScreen
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.menu_screen import MenuScreen
from screens.gameplay_screen import GameplayScreen
from screens.result_screen import ResultScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.profile_screen import ProfileScreen
from screens.instructions_screen import InstructionsScreen


class ScreenManager:
    """
    Coordinates navigation between all screens, handles top-level Pygame events,
    updates ambient particles, and executes scheduled delayed actions.
    """

    def __init__(self, db: DatabaseManager, auth: AuthManager, game: GameManager):
        self.db = db
        self.auth = auth
        self.game_manager = game

        self.running = True
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._init_fonts()

        # Background ambience
        self.bg_surface: Optional[pygame.Surface] = None
        self._load_background()
        self.bubbles = BubbleParticleSystem(count=40)

        # Scheduled delayed actions
        self._scheduled_actions: List[Dict[str, Any]] = []

        # Screen instances
        self.screens: Dict[str, Any] = {
            "welcome": WelcomeScreen(self),
            "login": LoginScreen(self),
            "register": RegisterScreen(self),
            "menu": MenuScreen(self),
            "gameplay": GameplayScreen(self),
            "results": ResultScreen(self),
            "leaderboard": LeaderboardScreen(self),
            "profile": ProfileScreen(self),
            "instructions": InstructionsScreen(self)
        }

        self.current_screen_name: str = "welcome"
        self.current_screen = self.screens["welcome"]
        self.current_screen.on_enter()

    def _init_fonts(self) -> None:
        """Initializes scalable system fonts with fallbacks for high readability."""
        font_family = "Segoe UI, Trebuchet MS, Arial, Helvetica, sans-serif"
        try:
            self.fonts["title"] = pygame.font.SysFont(font_family, 38, bold=True)
            self.fonts["large"] = pygame.font.SysFont(font_family, 26, bold=True)
            self.fonts["normal"] = pygame.font.SysFont(font_family, 18, bold=False)
            self.fonts["small"] = pygame.font.SysFont(font_family, 14, bold=False)
            self.fonts["tiny"] = pygame.font.SysFont(font_family, 12, bold=False)
        except Exception as e:
            print(f"[Font Warning] Fallback to default pygame font: {e}")
            self.fonts["title"] = pygame.font.Font(None, 48)
            self.fonts["large"] = pygame.font.Font(None, 34)
            self.fonts["normal"] = pygame.font.Font(None, 24)
            self.fonts["small"] = pygame.font.Font(None, 18)
            self.fonts["tiny"] = pygame.font.Font(None, 14)

    def _load_background(self) -> None:
        """Loads pre-rendered background image or creates fallback procedural gradient."""
        bg_file = BACKGROUNDS_DIR / "ocean_bg.png"
        if bg_file.exists():
            try:
                raw_bg = pygame.image.load(str(bg_file)).convert()
                self.bg_surface = pygame.transform.scale(raw_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"[Asset Warning] Failed loading ocean background: {e}")

        if not self.bg_surface:
            # Fallback procedural surface
            self.bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_surface.fill(COLOR_OCEAN_NAVY)

    def change_screen(self, screen_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Switches active view and triggers lifecycle callbacks."""
        if screen_name not in self.screens:
            print(f"[Error] Screen '{screen_name}' does not exist.")
            return

        if self.current_screen:
            self.current_screen.on_exit()

        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.on_enter(params)

    def schedule_action(self, delay_seconds: float, action: Callable[[], None]) -> None:
        """Enqueues a delayed callback to execute after delay_seconds."""
        fire_time = time.time() + delay_seconds
        self._scheduled_actions.append({"fire_at": fire_time, "action": action})

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processes global events and dispatches to active screen."""
        if event.type == pygame.QUIT:
            self.quit_game()
            return

        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, dt: float) -> None:
        """Updates background particles, screen state, and scheduled actions."""
        # Update ambient particles
        self.bubbles.update(dt)

        # Update scheduled actions
        now = time.time()
        remaining_actions = []
        for item in self._scheduled_actions:
            if now >= item["fire_at"]:
                try:
                    item["action"]()
                except Exception as e:
                    print(f"[Error in Scheduled Action] {e}")
            else:
                remaining_actions.append(item)
        self._scheduled_actions = remaining_actions

        # Update active screen
        if self.current_screen:
            self.current_screen.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders ocean background, ambient bubbles, and the current screen."""
        if self.bg_surface:
            surface.blit(self.bg_surface, (0, 0))

        # Ambient bubbles layer
        self.bubbles.draw(surface)

        # Active screen layer
        if self.current_screen:
            self.current_screen.draw(surface)

    def quit_game(self) -> None:
        """Stops the main loop and safely exits the application."""
        self.running = False

