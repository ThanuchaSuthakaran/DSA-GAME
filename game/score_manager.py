"""
Fish Quest - Ocean Adventure Game
Score & Game Progress Manager Module

Demonstrates:
- High Cohesion: Exclusively manages mathematical scoring, lives, coins,
  streak progression, and performance statistics.
- Decoupled Logic: Contains zero UI dependencies; produces clean state snapshots.
"""

from typing import Dict, Any
from config.settings import (
    INITIAL_LIVES,
    POINTS_PER_CORRECT,
    COINS_PER_CORRECT,
    QUESTIONS_PER_LEVEL,
    STREAK_BONUS_THRESHOLD,
    STREAK_BONUS_POINTS
)


class ScoreManager:
    """
    Tracks and computes all score, life, coin, and progression rules for a game session.
    """

    def __init__(self, initial_lives: int = INITIAL_LIVES):
        self.initial_lives = initial_lives
        self.score = 0
        self.coins = 0
        self.lives = initial_lives
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.current_streak = 0
        self.max_streak = 0

    def reset(self) -> None:
        """Resets all metrics to clean starting values for a new match."""
        self.score = 0
        self.coins = 0
        self.lives = self.initial_lives
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.current_streak = 0
        self.max_streak = 0

    def record_correct_answer(self, time_bonus: int = 0) -> Dict[str, Any]:
        """
        Awards points and coins for a correct answer, advances streaks,
        and applies bonuses.
        Returns a breakdown dict of rewards for UI feedback.
        """
        self.correct_answers += 1
        self.current_streak += 1
        if self.current_streak > self.max_streak:
            self.max_streak = self.current_streak

        base_points = POINTS_PER_CORRECT
        streak_bonus = STREAK_BONUS_POINTS if self.current_streak >= STREAK_BONUS_THRESHOLD else 0
        total_points_earned = base_points + streak_bonus + max(0, time_bonus)

        self.score += total_points_earned
        coins_earned = COINS_PER_CORRECT + (2 if self.current_streak >= STREAK_BONUS_THRESHOLD else 0)
        self.coins += coins_earned

        return {
            "correct": True,
            "points_earned": total_points_earned,
            "coins_earned": coins_earned,
            "streak": self.current_streak,
            "streak_bonus": streak_bonus > 0,
            "current_score": self.score,
            "lives_remaining": self.lives,
            "level": self.current_level
        }

    def record_incorrect_answer(self) -> Dict[str, Any]:
        """
        Deducts one life, resets current streak, and records incorrect count.
        Returns feedback dict for UI notifications.
        """
        self.incorrect_answers += 1
        self.current_streak = 0
        self.lives = max(0, self.lives - 1)

        return {
            "correct": False,
            "points_earned": 0,
            "coins_earned": 0,
            "streak": 0,
            "streak_bonus": False,
            "current_score": self.score,
            "lives_remaining": self.lives,
            "is_game_over": self.is_game_over,
            "level": self.current_level
        }

    @property
    def current_level(self) -> int:
        """Dynamic level derived from questions answered correctly."""
        return 1 + (self.correct_answers // QUESTIONS_PER_LEVEL)

    @property
    def is_game_over(self) -> bool:
        """Game ends when player has zero lives."""
        return self.lives <= 0

    def get_summary(self) -> Dict[str, Any]:
        """Returns complete performance summary for the Results Screen and Database."""
        return {
            "final_score": self.score,
            "total_coins": self.coins,
            "correct_answers": self.correct_answers,
            "incorrect_answers": self.incorrect_answers,
            "highest_streak": self.max_streak,
            "final_level": self.current_level,
            "lives_left": self.lives
        }

