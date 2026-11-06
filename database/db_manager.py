"""
Fish Quest - Ocean Adventure Game
Database Manager Module

Demonstrates:
- Low Coupling and High Cohesion: Isolates all SQLite database persistence operations
  behind a clean Data Access Object (DAO) interface. The rest of the application
  never writes raw SQL.
- Virtual Identity Persistence: Securely persists player accounts, credentials, and
  historical gameplay progress.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pathlib import Path

from config.settings import DATABASE_PATH


class DatabaseManager:
    """
    Manages persistent SQLite storage for players and game records.
    Provides encapsulated methods to initialize schema, register users,
    retrieve virtual identities, update gameplay statistics, and generate leaderboards.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """
        Initializes the SQLite database tables if they do not exist.
        Creates:
          1. players (virtual identity, credentials, career totals)
          2. game_history (individual completed match metrics)
        """
        schema = """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            highest_score INTEGER DEFAULT 0,
            total_games INTEGER DEFAULT 0,
            total_coins INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            incorrect_answers INTEGER NOT NULL,
            coins_earned INTEGER NOT NULL,
            played_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_players_score ON players (highest_score DESC);
        CREATE INDEX IF NOT EXISTS idx_history_player ON game_history (player_id);
        """
        conn = self.get_connection()
        try:
            with conn:
                conn.executescript(schema)
        finally:
            conn.close()

    def create_player(self, username: str, password_hash: str, salt: str) -> Optional[int]:
        """
        Registers a new player into the database.
        Returns the new player's ID, or None if the username already exists or an error occurs.
        """
        query = """
        INSERT INTO players (username, password_hash, salt, created_at)
        VALUES (?, ?, ?, ?);
        """
        now = datetime.now(timezone.utc).isoformat()
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, (username.strip(), password_hash, salt, now))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Duplicate username collision
            return None
        except sqlite3.Error as e:
            print(f"[Database Error] Failed to create player '{username}': {e}")
            return None
        finally:
            conn.close()

    def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a player record by username (case-insensitive).
        Returns a dictionary or None if not found.
        """
        query = "SELECT * FROM players WHERE username = ? COLLATE NOCASE;"
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (username.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"[Database Error] Querying username '{username}' failed: {e}")
            return None
        finally:
            conn.close()

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a player record by primary key ID."""
        query = "SELECT * FROM players WHERE id = ?;"
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"[Database Error] Querying player ID {player_id} failed: {e}")
            return None
        finally:
            conn.close()

    def update_player_stats(self, player_id: int, new_score: int, coins_earned: int) -> bool:
        """
        Updates cumulative stats for a player after a completed game:
        increments total_games and total_coins, and updates highest_score if beaten.
        """
        query = """
        UPDATE players
        SET total_games = total_games + 1,
            total_coins = total_coins + ?,
            highest_score = MAX(highest_score, ?)
        WHERE id = ?;
        """
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, (coins_earned, new_score, player_id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[Database Error] Updating stats for player {player_id} failed: {e}")
            return False
        finally:
            conn.close()

    def record_game(self, player_id: int, score: int, correct_answers: int,
                    incorrect_answers: int, coins_earned: int) -> Optional[int]:
        """
        Inserts a completed game session into game_history and updates the player's career stats.
        Returns the new game_history ID.
        """
        insert_history = """
        INSERT INTO game_history (player_id, score, correct_answers, incorrect_answers, coins_earned, played_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        now = datetime.now(timezone.utc).isoformat()
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(insert_history, (
                    player_id, score, correct_answers, incorrect_answers, coins_earned, now
                ))
                history_id = cursor.lastrowid

                # Atomically update player totals
                update_totals = """
                UPDATE players
                SET total_games = total_games + 1,
                    total_coins = total_coins + ?,
                    highest_score = MAX(highest_score, ?)
                WHERE id = ?;
                """
                cursor.execute(update_totals, (coins_earned, score, player_id))
                return history_id
        except sqlite3.Error as e:
            print(f"[Database Error] Failed to record game for player {player_id}: {e}")
            return None
        finally:
            conn.close()

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves top players sorted by highest_score descending.
        Returns up to `limit` records including username, highest_score, total_games, total_coins.
        """
        query = """
        SELECT id, username, highest_score, total_games, total_coins, created_at
        FROM players
        ORDER BY highest_score DESC, total_games ASC, id ASC
        LIMIT ?;
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"[Database Error] Failed to fetch leaderboard: {e}")
            return []
        finally:
            conn.close()

    def get_player_history(self, player_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recent game records for a specific player."""
        query = """
        SELECT id, score, correct_answers, incorrect_answers, coins_earned, played_at
        FROM game_history
        WHERE player_id = ?
        ORDER BY played_at DESC
        LIMIT ?;
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (player_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"[Database Error] Failed to fetch history for player {player_id}: {e}")
            return []
        finally:
            conn.close()
