"""
End-to-End Integration Test for Fish Quest
Validates complete flow:
1. Virtual Identity Creation & Authentication
2. Live Fish Game API Request (Interoperability)
3. Puzzle Image Conversion (Pillow/Pygame)
4. Game Scoring & Level Progression
5. SQLite Database Persistence & Leaderboard Query
"""

import unittest
import tempfile
from pathlib import Path
import pygame

from database.db_manager import DatabaseManager
from authentication.auth_manager import AuthManager
from api.fish_api import FishAPIService, FishPuzzle
from game.game_manager import GameManager, GameState


class TestEndToEndFlow(unittest.TestCase):
    """Full integration test across all 4 architectural pillars."""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_e2e.db"
        self.db = DatabaseManager(db_path=self.db_path)
        self.auth = AuthManager(db_manager=self.db)
        self.api = FishAPIService()
        self.game = GameManager(api_service=self.api, auth_manager=self.auth, db_manager=self.db)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_complete_quest_workflow(self):
        # 1. Register Virtual Identity
        reg_ok, reg_msg = self.auth.register("AquaKnight", "Poseidon2026", "Poseidon2026")
        self.assertTrue(reg_ok, f"Registration failed: {reg_msg}")

        # 2. Authenticate Virtual Identity
        login_ok, login_msg = self.auth.login("AquaKnight", "Poseidon2026")
        self.assertTrue(login_ok, f"Login failed: {login_msg}")
        self.assertEqual(self.auth.current_username, "AquaKnight")

        # 3. Fetch Live Puzzle from University API (Interoperability)
        try:
            puzzle = self.api.fetch_puzzle(use_base64=False)
            self.assertIsInstance(puzzle, FishPuzzle)
            self.assertIsNotNone(puzzle.image_surface)
            self.assertIsInstance(puzzle.solution, int)
            print(f"\n[E2E Test] Live API Puzzle retrieved: Solution={puzzle.solution}, Fish={puzzle.fish_count}, Chest={puzzle.chest_count}")
        except Exception as e:
            self.skipTest(f"Live API network unavailable: {e}")

        # 4. Set puzzle directly in game manager and test answer evaluation
        self.game.current_puzzle = puzzle
        self.game.set_state(GameState.ACTIVE)

        # Submit correct answer
        feedback = self.game.submit_answer(str(puzzle.solution))
        self.assertTrue(feedback["correct"])
        self.assertGreaterEqual(self.game.score_mgr.score, 10)
        self.assertGreaterEqual(self.game.score_mgr.coins, 5)

        # 5. Conclude Game and Verify Database Persistence
        summary = self.game.end_game()
        self.assertEqual(self.game.state, GameState.GAME_OVER)
        self.assertEqual(summary["correct_answers"], 1)

        # 6. Verify Player Career Stats updated in SQLite
        player = self.db.get_player_by_username("AquaKnight")
        self.assertEqual(player["total_games"], 1)
        self.assertGreaterEqual(player["highest_score"], 10)
        self.assertGreaterEqual(player["total_coins"], 5)

        # 7. Verify Leaderboard reflects this player
        leaderboard = self.db.get_leaderboard(limit=5)
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]["username"], "AquaKnight")
        self.assertEqual(leaderboard[0]["highest_score"], player["highest_score"])


if __name__ == "__main__":
    unittest.main()

