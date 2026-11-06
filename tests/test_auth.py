"""
Unit Tests for Authentication and Virtual Identity Module
Fish Quest - Ocean Adventure Game
"""

import unittest
import tempfile
from pathlib import Path

from database.db_manager import DatabaseManager
from authentication.auth_manager import AuthManager


class TestAuthManager(unittest.TestCase):
    """Verifies user registration, password hashing, and session management."""

    def setUp(self):
        # Use an isolated temporary SQLite database for clean test isolation
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_db_path = Path(self.temp_dir.name) / "test_auth.db"
        self.db = DatabaseManager(db_path=self.temp_db_path)
        self.auth = AuthManager(db_manager=self.db)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_password_hashing_and_verification(self):
        password = "SecretPassword123"
        pw_hash, salt = AuthManager.hash_password(password)

        self.assertIsNotNone(pw_hash)
        self.assertIsNotNone(salt)
        self.assertNotEqual(password, pw_hash)

        # Verification check
        self.assertTrue(AuthManager.verify_password(password, salt, pw_hash))
        self.assertFalse(AuthManager.verify_password("WrongPassword", salt, pw_hash))

    def test_successful_registration(self):
        success, msg = self.auth.register("CaptainNemo", "Submarine99", "Submarine99")
        self.assertTrue(success)
        self.assertIn("successful", msg.lower())

        # Verify record exists in database
        player = self.db.get_player_by_username("CaptainNemo")
        self.assertIsNotNone(player)
        self.assertEqual(player["username"], "CaptainNemo")

    def test_duplicate_username_prevention(self):
        self.auth.register("Ariel", "Flounder12", "Flounder12")
        success, msg = self.auth.register("Ariel", "DifferentPass", "DifferentPass")
        self.assertFalse(success)
        self.assertIn("already taken", msg.lower())

    def test_registration_validation_rules(self):
        # Username too short
        ok, msg = self.auth.register("ab", "pass123", "pass123")
        self.assertFalse(ok)

        # Password mismatch
        ok, msg = self.auth.register("ValidUser", "pass1", "pass2")
        self.assertFalse(ok)
        self.assertIn("do not match", msg.lower())

        # Password too short
        ok, msg = self.auth.register("ValidUser", "12", "12")
        self.assertFalse(ok)

    def test_login_flow_and_session_state(self):
        self.auth.register("Poseidon", "Trident99", "Trident99")

        # Wrong password
        ok, msg = self.auth.login("Poseidon", "WrongPass")
        self.assertFalse(ok)
        self.assertFalse(self.auth.is_authenticated)

        # Correct password
        ok, msg = self.auth.login("Poseidon", "Trident99")
        self.assertTrue(ok)
        self.assertTrue(self.auth.is_authenticated)
        self.assertEqual(self.auth.current_username, "Poseidon")

        # Logout
        self.auth.logout()
        self.assertFalse(self.auth.is_authenticated)
        self.assertEqual(self.auth.current_username, "Guest")


if __name__ == "__main__":
    unittest.main()
