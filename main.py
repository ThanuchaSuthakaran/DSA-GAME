"""
Fish Quest – Ocean Adventure Game
CIS045-3 Distributed Service Architectures Assignment
Main Application Entry Point

Demonstrates:
1. Low Coupling and High Cohesion:
   - main.py acts as the composition root, wiring independent modules together.
   - Core game logic, persistent database operations, authentication,
     and network API services remain decoupled from the main loop.
2. Event-Driven Programming:
   - Uses Pygame's event pump and clock tick loop to dispatch user actions
     (mouse clicks, keystrokes, window closes) to active screen handlers.
3. Interoperability:
   - Initiates external RESTful Fish API integration.
4. Virtual Identity:
   - Wires AuthManager and SQLite DatabaseManager to track player sessions.
"""

import sys
import pygame

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FPS, IMAGES_DIR
from database.db_manager import DatabaseManager
from authentication.auth_manager import AuthManager
from api.fish_api import FishAPIService
from game.game_manager import GameManager
from screens.screen_manager import ScreenManager
from assets.asset_factory import generate_all_assets


def main():
    """Application entry point and composition root."""
    # Step 1: Ensure asset graphics exist (procedural generation fallback)
    generate_all_assets()

    # Step 2: Initialize Pygame subsystems
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption(WINDOW_TITLE)

    # Set Window Icon if available
    icon_path = IMAGES_DIR / "fish_icon.png"
    if icon_path.exists():
        try:
            icon_surf = pygame.image.load(str(icon_path))
            pygame.display.set_icon(icon_surf)
        except Exception as e:
            print(f"[Icon Warning] Could not set window icon: {e}")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Step 3: Instantiate core services (Dependency Injection)
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager=db_manager)
    api_service = FishAPIService()
    game_manager = GameManager(
        api_service=api_service,
        auth_manager=auth_manager,
        db_manager=db_manager
    )

    # Step 4: Screen Coordinator
    screen_manager = ScreenManager(
        db=db_manager,
        auth=auth_manager,
        game=game_manager
    )

    # Step 5: Main Event Loop (Event-Driven Architecture)
    while screen_manager.running:
        dt = clock.tick(FPS) / 1000.0  # Frame delta time in seconds

        # Process Pygame Event Queue
        for event in pygame.event.get():
            screen_manager.handle_event(event)

        # Update Frame-dependent State and Timers
        screen_manager.update(dt)

        # Render Active Frame
        screen_manager.draw(screen)

        # Flip Double Buffer
        pygame.display.flip()

    # Clean Shutdown
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

