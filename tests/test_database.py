"""
Unit Tests for SQLite Database Module
Fish Quest - Ocean Adventure Game
"""

import unittest
import tempfile
from pathlib import Path

from database.db_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Verifies schema creation, user persistence, and leaderboard queries."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_db.db"
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_create_and_retrieve_player(self):
        pid = self.db.create_player("Dolphin1", "hash123", "salt123")
        self.assertIsNotNone(pid)

        player = self.db.get_player_by_username("Dolphin1")
        self.assertIsNotNone(player)
        self.assertEqual(player["username"], "Dolphin1")
        self.assertEqual(player["highest_score"], 0)
        self.assertEqual(player["total_games"], 0)
        self.assertEqual(player["total_coins"], 0)

    def test_record_game_and_update_career_stats(self):
        pid = self.db.create_player("Sharky", "hashabc", "saltabc")

        # Game 1: 50 points, 15 coins
        hist_id = self.db.record_game(
            player_id=pid,
            score=50,
            correct_answers=5,
            incorrect_answers=1,
            coins_earned=15
        )
        self.assertIsNotNone(hist_id)

        player = self.db.get_player_by_id(pid)
        self.assertEqual(player["highest_score"], 50)
        self.assertEqual(player["total_games"], 1)
        self.assertEqual(player["total_coins"], 15)

        # Game 2: Lower score (30 points), 10 coins -> high score remains 50
        self.db.record_game(
            player_id=pid,
            score=30,
            correct_answers=3,
            incorrect_answers=3,
            coins_earned=10
        )
        player = self.db.get_player_by_id(pid)
        self.assertEqual(player["highest_score"], 50)
        self.assertEqual(player["total_games"], 2)
        self.assertEqual(player["total_coins"], 25)

        # Game 3: Higher score (90 points), 20 coins -> high score updates to 90
        self.db.record_game(
            player_id=pid,
            score=90,
            correct_answers=8,
            incorrect_answers=0,
            coins_earned=20
        )
        player = self.db.get_player_by_id(pid)
        self.assertEqual(player["highest_score"], 90)
        self.assertEqual(player["total_games"], 3)
        self.assertEqual(player["total_coins"], 45)

    def test_leaderboard_sorting(self):
        # Create 3 players with varying scores
        p1 = self.db.create_player("BronzePlayer", "h", "s")
        p2 = self.db.create_player("GoldPlayer", "h", "s")
        p3 = self.db.create_player("SilverPlayer", "h", "s")

        self.db.record_game(p1, score=20, correct_answers=2, incorrect_answers=1, coins_earned=5)
        self.db.record_game(p2, score=150, correct_answers=12, incorrect_answers=1, coins_earned=50)
        self.db.record_game(p3, score=80, correct_answers=7, incorrect_answers=2, coins_earned=25)

        leaders = self.db.get_leaderboard(limit=10)
        self.assertEqual(len(leaders), 3)
        self.assertEqual(leaders[0]["username"], "GoldPlayer")
        self.assertEqual(leaders[0]["highest_score"], 150)
        self.assertEqual(leaders[1]["username"], "SilverPlayer")
        self.assertEqual(leaders[1]["highest_score"], 80)
        self.assertEqual(leaders[2]["username"], "BronzePlayer")
        self.assertEqual(leaders[2]["highest_score"], 20)


if __name__ == "__main__":
    unittest.main()

