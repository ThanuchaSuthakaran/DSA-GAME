"""
Fish Quest - Ocean Adventure Game
Authentication & Virtual Identity Manager Module

Demonstrates:
- Virtual Identity:
  In distributed and interactive computer systems, a "Virtual Identity" represents
  the digital persona of a human participant. It encapsulates credentials, authorization,
  career state (high scores, coin balances, achievements), and accountability across
  sessions without disclosing real-world identity.
- Security Best Practices:
  Passwords are never stored in plaintext. They are salted with 16 cryptographically
  secure random bytes (os.urandom) and hashed using PBKDF2-HMAC-SHA256 with 100,000 iterations.
- Low Coupling:
  AuthManager delegates all data persistence to DatabaseManager, remaining independent
  of GUI presentation or network communication.
"""

import os
import hashlib
import hmac
from typing import Optional, Dict, Any, Tuple
from database.db_manager import DatabaseManager


class AuthManager:
    """
    Handles user registration, authentication, password hashing, and active session state.
    """

    PBKDF2_ITERATIONS = 100_000
    HASH_ALGORITHM = "sha256"

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.current_user: Optional[Dict[str, Any]] = None

    @classmethod
    def hash_password(cls, password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
        """
        Hashes a plaintext password with PBKDF2-HMAC-SHA256.
        Returns a tuple of (hash_hex, salt_hex).
        """
        if salt_hex is None:
            salt_bytes = os.urandom(16)
            salt_hex = salt_bytes.hex()
        else:
            salt_bytes = bytes.fromhex(salt_hex)

        key = hashlib.pbkdf2_hmac(
            hash_name=cls.HASH_ALGORITHM,
            password=password.encode("utf-8"),
            salt=salt_bytes,
            iterations=cls.PBKDF2_ITERATIONS
        )
        return key.hex(), salt_hex

    @classmethod
    def verify_password(cls, password: str, salt_hex: str, expected_hash_hex: str) -> bool:
        """Verifies a plaintext password against the recorded salt and hash."""
        computed_hash, _ = cls.hash_password(password, salt_hex)
        return hmac.compare_digest(computed_hash, expected_hash_hex)

    def register(self, username: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        Validates input and creates a new virtual identity player account.
        Returns (success: bool, message: str).
        """
        username = (username or "").strip()
        password = password or ""
        confirm_password = confirm_password or ""

        # Validation rules
        if not username:
            return False, "Username cannot be empty."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(username) > 20:
            return False, "Username cannot exceed 20 characters."
        if not username.isalnum() and "_" not in username:
            return False, "Username may only contain letters, numbers, and underscores."
        if not password:
            return False, "Password cannot be empty."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        if password != confirm_password:
            return False, "Passwords do not match."

        # Check existing
        existing = self.db.get_player_by_username(username)
        if existing:
            return False, f"Username '{username}' is already taken."

        # Secure hash and persist
        pw_hash, salt = self.hash_password(password)
        player_id = self.db.create_player(username, pw_hash, salt)

        if player_id is None:
            return False, "Registration failed due to a database error."

        return True, "Registration successful! You may now log in."

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticates credentials and establishes the active virtual identity session.
        Returns (success: bool, message: str).
        """
        username = (username or "").strip()
        password = password or ""

        if not username or not password:
            return False, "Please enter both username and password."

        player = self.db.get_player_by_username(username)
        if not player:
            return False, "Invalid username or password."

        salt = player.get("salt", "")
        pw_hash = player.get("password_hash", "")

        if not self.verify_password(password, salt, pw_hash):
            return False, "Invalid username or password."

        # Establish authenticated session
        self.current_user = player
        return True, f"Welcome back, {player['username']}!"

    def logout(self) -> None:
        """Terminates the active authenticated player session."""
        self.current_user = None

    def refresh_current_user(self) -> None:
        """Reloads the current user profile from the database to keep stats fresh."""
        if self.current_user and "id" in self.current_user:
            updated = self.db.get_player_by_id(self.current_user["id"])
            if updated:
                self.current_user = updated

    @property
    def is_authenticated(self) -> bool:
        """Returns True if a player is currently logged in."""
        return self.current_user is not None

    @property
    def current_username(self) -> str:
        """Returns active player's username or 'Guest'."""
        if self.current_user:
            return self.current_user.get("username", "Guest")
        return "Guest"

    @property
    def current_user_id(self) -> Optional[int]:
        """Returns the active player's database ID or None."""
        if self.current_user:
            return self.current_user.get("id")
        return None
