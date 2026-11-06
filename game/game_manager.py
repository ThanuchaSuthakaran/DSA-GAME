"""
Fish Quest - Ocean Adventure Game
Core Game Manager Module

Demonstrates:
- Low Coupling and High Cohesion:
  Coordinates between API service, score manager, timer, and persistent database
  without tightly binding to UI render code.
- Event-Driven Programming:
  Manages gameplay states (LOADING, ACTIVE, FEEDBACK, PAUSED, GAME_OVER),
  handles answer submission events, timeout callbacks, and asynchronous API dispatches.
- Interoperability & Virtual Identity Integration:
  Connects external REST responses directly to authenticated player database records.
"""

from enum import Enum
from typing import Optional, Dict, Any, Callable

from api.fish_api import FishAPIService, FishPuzzle
from game.score_manager import ScoreManager
from game.timer import CountdownTimer
from database.db_manager import DatabaseManager
from authentication.auth_manager import AuthManager
from config.settings import (
    BASE_COUNTDOWN_SECONDS,
    MIN_COUNTDOWN_SECONDS,
    TIME_DECREASE_PER_LEVEL
)


class GameState(Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    ACTIVE = "ACTIVE"
    FEEDBACK = "FEEDBACK"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    GAME_OVER = "GAME_OVER"


class GameManager:
    """
    Orchestrates an active gameplay session.
    Maintains the current puzzle, timer, scoring, player state transitions,
    and database persistence upon match completion.
    """

    def __init__(
        self,
        api_service: Optional[FishAPIService] = None,
        auth_manager: Optional[AuthManager] = None,
        db_manager: Optional[DatabaseManager] = None
    ):
        self.api = api_service or FishAPIService()
        self.auth = auth_manager or AuthManager()
        self.db = db_manager or self.auth.db

        self.score_mgr = ScoreManager()
        self.timer = CountdownTimer(
            initial_duration=BASE_COUNTDOWN_SECONDS,
            on_expire=self._on_timer_expired
        )

        self.state = GameState.IDLE
        self.current_puzzle: Optional[FishPuzzle] = None
        self.error_message: Optional[str] = None
        self.feedback_info: Optional[Dict[str, Any]] = None
        self.last_user_answer: Optional[str] = None
        self.is_paused_before = GameState.ACTIVE

        # Callback for UI notification upon state changes
        self.on_state_change: Optional[Callable[[GameState], None]] = None

    def set_state(self, new_state: GameState) -> None:
        """Transitions game state and alerts registered observers."""
        self.state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)

    def start_game(self) -> None:
        """Initializes state and starts the first puzzle retrieval."""
        self.score_mgr.reset()
        self.error_message = None
        self.feedback_info = None
        self.current_puzzle = None
        self.load_next_puzzle()

    def calculate_question_duration(self) -> float:
        """
        Dynamically adjusts countdown duration based on level progression.
        Demonstrates difficulty scaling as the player advances.
        """
        level = self.score_mgr.current_level
        duration = BASE_COUNTDOWN_SECONDS - ((level - 1) * TIME_DECREASE_PER_LEVEL)
        return max(float(MIN_COUNTDOWN_SECONDS), float(duration))

    def load_next_puzzle(self) -> None:
        """
        Fetches a new puzzle from the external API asynchronously.
        Sets state to LOADING so the UI can display an animated loading screen.
        """
        self.set_state(GameState.LOADING)
        self.timer.stop()
        self.feedback_info = None
        self.last_user_answer = None

        def success_callback(puzzle: FishPuzzle):
            self.current_puzzle = puzzle
            duration = self.calculate_question_duration()
            self.timer.start(duration)
            self.set_state(GameState.ACTIVE)

        def error_callback(err: str):
            self.error_message = err
            self.set_state(GameState.ERROR)

        # Non-blocking asynchronous API request
        self.api.fetch_puzzle_async(
            on_success=success_callback,
            on_error=error_callback
        )

    def submit_answer(self, raw_input: str) -> Dict[str, Any]:
        """
        Evaluates player answer against the API puzzle solution.
        Deducts lives or awards points/coins accordingly.
        """
        if self.state != GameState.ACTIVE or not self.current_puzzle:
            return {"error": "Invalid state to submit answer"}

        self.timer.stop()
        clean_input = (raw_input or "").strip()
        self.last_user_answer = clean_input

        # Input validation
        if not clean_input:
            # Empty input is rejected
            self.timer.resume()
            return {"error": "Please enter a valid number."}

        try:
            player_val = int(clean_input)
        except ValueError:
            self.timer.resume()
            return {"error": "Answer must be a whole number (digits only)."}

        # Compare with API solution
        is_correct = (player_val == self.current_puzzle.solution)
        expected_solution = self.current_puzzle.solution

        if is_correct:
            # Award speed bonus based on time remaining
            time_bonus = int(self.timer.time_remaining // 5)
            feedback = self.score_mgr.record_correct_answer(time_bonus=time_bonus)
            feedback["user_answer"] = player_val
            feedback["solution"] = expected_solution
            feedback["message"] = f"Correct! +{feedback['points_earned']} Pts, +{feedback['coins_earned']} Coins"
        else:
            feedback = self.score_mgr.record_incorrect_answer()
            feedback["user_answer"] = player_val
            feedback["solution"] = expected_solution
            feedback["message"] = f"Oops! Incorrect. The correct answer was {expected_solution}."

        self.feedback_info = feedback

        if self.score_mgr.is_game_over:
            self.end_game()
        else:
            self.set_state(GameState.FEEDBACK)

        return feedback

    def _on_timer_expired(self) -> None:
        """Called automatically when the countdown timer reaches zero."""
        if self.state == GameState.ACTIVE and self.current_puzzle:
            # Count timeout as incorrect answer
            feedback = self.score_mgr.record_incorrect_answer()
            feedback["user_answer"] = "Timeout"
            feedback["solution"] = self.current_puzzle.solution
            feedback["message"] = f"Time's Up! The correct answer was {self.current_puzzle.solution}."
            self.feedback_info = feedback

            if self.score_mgr.is_game_over:
                self.end_game()
            else:
                self.set_state(GameState.FEEDBACK)

    def pause_game(self) -> None:
        """Pauses the game and timer if currently active."""
        if self.state in (GameState.ACTIVE, GameState.FEEDBACK):
            self.is_paused_before = self.state
            self.timer.pause()
            self.set_state(GameState.PAUSED)

    def resume_game(self) -> None:
        """Resumes active gameplay and restarts the timer."""
        if self.state == GameState.PAUSED:
            self.timer.resume()
            self.set_state(self.is_paused_before)

    def toggle_pause(self) -> None:
        """Toggles between paused and running state."""
        if self.state == GameState.PAUSED:
            self.resume_game()
        elif self.state in (GameState.ACTIVE, GameState.FEEDBACK):
            self.pause_game()

    def update(self) -> None:
        """Updates frame-dependent components such as the countdown timer."""
        if self.state == GameState.ACTIVE:
            self.timer.update()

    def end_game(self) -> Dict[str, Any]:
        """
        Concludes match, persists results to SQLite for authenticated player,
        and transitions to GAME_OVER state.
        """
        self.timer.stop()
        self.set_state(GameState.GAME_OVER)
        summary = self.score_mgr.get_summary()

        # Virtual Identity & Database Persistence:
        # Link completed match statistics with player's authenticated identity
        user_id = self.auth.current_user_id
        if user_id is not None:
            self.db.record_game(
                player_id=user_id,
                score=summary["final_score"],
                correct_answers=summary["correct_answers"],
                incorrect_answers=summary["incorrect_answers"],
                coins_earned=summary["total_coins"]
            )
            # Refresh user profile session cache
            self.auth.refresh_current_user()

        return summary

