"""
Unit Tests for Scoring and Progress Manager Module
Fish Quest - Ocean Adventure Game
"""

import unittest
from game.score_manager import ScoreManager
from config.settings import INITIAL_LIVES, POINTS_PER_CORRECT, COINS_PER_CORRECT, STREAK_BONUS_POINTS


class TestScoreManager(unittest.TestCase):
    """Verifies score, life, coin, and level progression rules."""

    def setUp(self):
        self.mgr = ScoreManager(initial_lives=3)

    def test_initial_state(self):
        self.assertEqual(self.mgr.score, 0)
        self.assertEqual(self.mgr.coins, 0)
        self.assertEqual(self.mgr.lives, 3)
        self.assertEqual(self.mgr.correct_answers, 0)
        self.assertEqual(self.mgr.incorrect_answers, 0)
        self.assertEqual(self.mgr.current_level, 1)
        self.assertFalse(self.mgr.is_game_over)

    def test_single_correct_answer(self):
        res = self.mgr.record_correct_answer(time_bonus=0)
        self.assertTrue(res["correct"])
        self.assertEqual(self.mgr.score, POINTS_PER_CORRECT)
        self.assertEqual(self.mgr.coins, COINS_PER_CORRECT)
        self.assertEqual(self.mgr.current_streak, 1)
        self.assertEqual(self.mgr.lives, 3)

    def test_streak_bonus(self):
        # 1st correct: normal
        self.mgr.record_correct_answer()
        # 2nd correct: normal
        self.mgr.record_correct_answer()
        # 3rd correct: triggers streak bonus
        res3 = self.mgr.record_correct_answer()

        self.assertTrue(res3["streak_bonus"])
        expected_points = (POINTS_PER_CORRECT * 3) + STREAK_BONUS_POINTS
        self.assertEqual(self.mgr.score, expected_points)

    def test_incorrect_answer_and_life_deduction(self):
        self.mgr.record_correct_answer()
        self.assertEqual(self.mgr.current_streak, 1)

        # Record incorrect
        res = self.mgr.record_incorrect_answer()
        self.assertFalse(res["correct"])
        self.assertEqual(self.mgr.lives, 2)
        self.assertEqual(self.mgr.current_streak, 0)  # Streak reset
        self.assertFalse(self.mgr.is_game_over)

    def test_game_over_on_zero_lives(self):
        self.mgr.record_incorrect_answer()  # lives = 2
        self.mgr.record_incorrect_answer()  # lives = 1
        res = self.mgr.record_incorrect_answer()  # lives = 0

        self.assertEqual(self.mgr.lives, 0)
        self.assertTrue(self.mgr.is_game_over)
        self.assertTrue(res["is_game_over"])

    def test_level_progression(self):
        self.assertEqual(self.mgr.current_level, 1)
        # 3 questions per level
        self.mgr.record_correct_answer()
        self.mgr.record_correct_answer()
        self.assertEqual(self.mgr.current_level, 1)

        self.mgr.record_correct_answer()
        self.assertEqual(self.mgr.current_level, 2)


if __name__ == "__main__":
    unittest.main()

