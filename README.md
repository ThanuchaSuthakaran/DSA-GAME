# Fish Quest – Ocean Adventure Game

> **Module**: CIS045-3 Distributed Service Architectures  
> **Course**: BSc (Hons) Computer Science  
> **Application**: 2D Desktop Educational Puzzle Game  
> **Platform**: Windows (Python 3, Pygame)

---

## 1. Project Overview

**Fish Quest – Ocean Adventure** is a complete, modern 2D educational desktop puzzle game built in Python. The game challenges players to explore oceanic depths by solving visual counting puzzles fetched in real time from an external university REST web service. 

Players authenticate through a secure local Virtual Identity system, count fish in dynamically generated ocean scenes, earn scores and coin treasures, advance through escalating difficulty levels, and compete for top ranks on a persistent global leaderboard.

---

## 2. Technologies Used

- **Python 3.10+ / Python 3.14**: Core programming language.
- **Pygame-CE / Pygame**: Graphical User Interface (GUI), 60 FPS rendering pipeline, event queue, sound/visual asset blitting.
- **Requests**: External HTTP communication, REST endpoint queries, image streaming.
- **SQLite3**: ACID-compliant relational local database for player identities, career stats, and match histories.
- **JSON**: Standard data exchange format for consuming API responses.
- **Pillow (PIL)**: Image stream inspection, alpha transparency compositing, format conversion, and procedural asset generation.
- **PBKDF2-HMAC-SHA256**: Cryptographic password hashing with 16-byte random salts.
- **Unittest**: Automated unit and end-to-end integration test suite.

---

## 3. Installation Instructions

### Prerequisites
- Python 3.10 or newer installed on Windows.
- Active Internet connection (to communicate with the University Fish Game API).

### Setup Steps
1. Clone or extract the project directory to your local machine:
   ```bash
   cd "Fish Quest"
   ```

2. (Optional but recommended) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 4. How to Run the Game & Tests

### Starting the Application
Launch the game directly from the root directory:
```bash
python main.py
```

### Running Automated Unit & Integration Tests
Execute the full test suite with test discovery:
```bash
python -m unittest discover tests
```
Or execute individual test modules:
```bash
python -m unittest tests/test_auth.py
python -m unittest tests/test_score.py
python -m unittest tests/test_api.py
python -m unittest tests/test_database.py
python -m unittest tests/test_integration.py
```

---

## 5. External Fish Game API Integration

The game connects to the official educational puzzle API created by Prof. Marc Conrad at the University of Bedfordshire:

- **Documentation**: [https://marcconrad.com/uob/fish/doc.php](https://marcconrad.com/uob/fish/doc.php)
- **API Endpoint**: `http://marcconrad.com/uob/fish/api.php?out=json`

### Inspected JSON Response Schema
A live GET request to the endpoint produces the following JSON payload:
```json
{
  "question": "https://www.sanfoh.com/uob/fish/data/ch_fc1517_233014_008x004.png",
  "fish": 4,
  "chest": 8
}
```
When `base64=yes` is requested (`http://marcconrad.com/uob/fish/api.php?out=json&base64=yes`):
```json
{
  "question": "iVBORw0KGgoAAAANSUhEUgAAApQAAAFoCAYAAADpd2vDAAAACXBIWXMAAA7E...",
  "fish": 4,
  "chest": 8
}
```

### Response Processing Pipeline
1. **Dynamic Field Inspection**: The `FishAPIService` (`api/fish_api.py`) inspects the returned dictionary. It checks for `"solution"`, `"fish"`, and any fallback integer field, ensuring compatibility across different API variations.
2. **Binary Stream & Base64 Decoding**: If the `"question"` field contains an HTTP URL, `requests.get()` streams the image bytes. If it contains Base64-encoded text, Python's `base64.b64decode()` decodes the raw binary data.
3. **Pillow & Pygame Surface Conversion**: The raw bytes are loaded into a `PIL.Image` via `io.BytesIO`, verified for format integrity, converted to RGBA mode, and transferred into a native `pygame.Surface` using `pygame.image.frombytes()` / `fromstring()`.
4. **Strong Typing**: The parsed data is bundled into an immutable `FishPuzzle` dataclass:
   ```python
   @dataclass
   class FishPuzzle:
       image_url: str
       solution: int
       fish_count: int
       chest_count: Optional[int]
       image_surface: Optional[pygame.Surface]
       is_base64: bool
       raw_bytes: Optional[bytes]
   ```
5. **Non-Blocking Asynchronous Retrieval**: Network requests are dispatched to background daemon threads (`fetch_puzzle_async`). The Pygame loop continues rendering at 60 FPS with an animated loading indicator, completely eliminating UI freezing while waiting on network round-trips.

---

## 6. SQLite Database Architecture

Data persistence is managed cleanly by `DatabaseManager` (`database/db_manager.py`) storing all tables in `fish_quest.db`.

### Entity-Relationship Diagram

```
+-----------------------------------+        +-----------------------------------+
|              PLAYERS              |        |           GAME_HISTORY            |
+-----------------------------------+        +-----------------------------------+
| id (INTEGER PK AUTOINCREMENT)     | 1    * | id (INTEGER PK AUTOINCREMENT)     |
| username (TEXT UNIQUE NOCASE)     |<-------| player_id (INTEGER FK)            |
| password_hash (TEXT NOT NULL)     |        | score (INTEGER NOT NULL)          |
| salt (TEXT NOT NULL)              |        | correct_answers (INTEGER NOT NULL)|
| highest_score (INTEGER DEFAULT 0) |        | incorrect_answers (INTEGER)       |
| total_games (INTEGER DEFAULT 0)   |        | coins_earned (INTEGER NOT NULL)   |
| total_coins (INTEGER DEFAULT 0)   |        | played_at (TEXT NOT NULL ISO8601) |
| created_at (TEXT NOT NULL ISO8601)|        +-----------------------------------+
+-----------------------------------+
```

### Table Definitions
1. **`players`**: Represents the persistent Virtual Identity of each registered player. Stores salted password hashes, career high scores, total matches played, accumulated coin balance, and registration timestamp.
2. **`game_history`**: Records individual match sessions, linking foreign key `player_id` to the parent identity. Stores score achieved, correct/incorrect counters, coins earned, and match timestamp.

---

## 7. Software Architecture & Module Responsibilities

The codebase follows strict Object-Oriented separation of concerns:

```
FishQuest/
│
├── main.py                     # Composition root; initializes Pygame & wires dependencies
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete architectural documentation
├── fish_quest.db               # SQLite database file (auto-generated)
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Global constants, colors, screen dimensions, API parameters
│
├── api/
│   ├── __init__.py
│   └── fish_api.py             # External Fish Game API client, Base64 decoding, threading
│
├── database/
│   ├── __init__.py
│   └── db_manager.py           # SQLite Data Access Object (DAO); CRUD, leaderboard queries
│
├── authentication/
│   ├── __init__.py
│   └── auth_manager.py         # Virtual identity, PBKDF2 password hashing & session management
│
├── game/
│   ├── __init__.py
│   ├── timer.py                # Frame-independent countdown timer with pause/resume
│   ├── score_manager.py        # Score calculations, streak multipliers, life tracking
│   └── game_manager.py         # Game coordinator and state machine (LOADING, ACTIVE, FEEDBACK, PAUSED, GAME_OVER)
│
├── screens/
│   ├── __init__.py
│   ├── base_screen.py          # Abstract screen with lifecycle hooks & UI helpers
│   ├── screen_manager.py       # Screen navigation coordinator & background particle layer
│   ├── welcome_screen.py       # Title, logo, and main entry navigation
│   ├── login_screen.py         # Virtual identity login form
│   ├── register_screen.py      # Virtual identity registration form
│   ├── menu_screen.py          # Authenticated player dashboard
│   ├── gameplay_screen.py      # Live puzzle rendering, HUD, timer bar, answer input
│   ├── leaderboard_screen.py   # Global top 10 player rankings
│   ├── profile_screen.py       # Player career stats & recent match history
│   └── instructions_screen.py  # Tutorial & explanation of the 4 distributed system themes
│
├── ui/
│   ├── __init__.py
│   ├── button.py               # Event-driven interactive button with hover glow effects
│   ├── text_input.py           # Interactive text box with cursor, masking & Enter submission
│   └── particles.py            # Floating bubble ambience simulation system
│
├── assets/
│   ├── asset_factory.py        # Procedural generator for ocean backgrounds, fish & HUD icons
│   ├── images/                 # Generated clownfish, heart, coin sprites
│   ├── backgrounds/            # Generated high-resolution ocean gradient background
│   └── fonts/                  # Font resources
│
└── tests/
    ├── __init__.py
    ├── test_auth.py            # Unit tests for password hashing & session state
    ├── test_api.py             # Unit tests for JSON parsing & Base64 decoding
    ├── test_score.py           # Unit tests for scoring, streaks, lives & level progression
    ├── test_database.py        # Unit tests for SQLite schema, updates & leaderboard
    └── test_integration.py     # End-to-end test connecting API, Auth, Pygame & SQLite
```

---

## 8. Demonstration of the Four Assignment Themes

### Theme 1: Low Coupling and High Cohesion

- **High Cohesion**:
  - `DatabaseManager` (`database/db_manager.py`) is exclusively concerned with SQLite persistence. It does not contain any Pygame rendering, networking, or user interface logic.
  - `FishAPIService` (`api/fish_api.py`) focuses solely on HTTP communication, JSON parsing, Base64 decoding, and converting binary streams into `FishPuzzle` instances.
  - `ScoreManager` (`game/score_manager.py`) encapsulates mathematical game rules (streak bonus thresholds, point additions, life deductions).
  - `CountdownTimer` (`game/timer.py`) manages real-time delta countdowns, pause/resume, and expiration callbacks independently of rendering.
- **Low Coupling**:
  - Modules interact through clean, well-defined parameter interfaces and data transfer objects (`FishPuzzle`, dictionaries, tuples).
  - Screens never issue direct SQL queries or HTTP requests; they delegate actions through `ScreenManager`, `GameManager`, and `AuthManager`.
  - In `main.py`, dependency injection is used to instantiate and connect `DatabaseManager`, `AuthManager`, `FishAPIService`, `GameManager`, and `ScreenManager`.

### Theme 2: Event-Driven Programming

- **Pygame Event Loop**:
  - `main.py` runs a central event pump (`pygame.event.get()`). Events (`QUIT`, `MOUSEBUTTONDOWN`, `MOUSEBUTTONUP`, `MOUSEMOTION`, `KEYDOWN`) are routed through `ScreenManager.handle_event(event)` to the active screen.
- **Interactive UI Components**:
  - `Button.handle_event()` (`ui/button.py`) tracks mouse hover states and invokes registered `on_click` callbacks when clicked.
  - `TextInput.handle_event()` (`ui/text_input.py`) captures keystrokes, manages cursor position, handles Backspace, and dispatches on Enter press (`K_RETURN`).
- **Decoupled Callbacks & Timers**:
  - `CountdownTimer` triggers an `on_expire` callback upon reaching zero (`GameManager._on_timer_expired`), cleanly deducting a life without tight polling.
  - `ScreenManager.schedule_action()` allows non-blocking delayed screen transitions.
- **Non-Blocking Asynchronous Concurrency**:
  - `FishAPIService.fetch_puzzle_async()` runs remote HTTP operations in a background daemon thread. When the response arrives, it invokes thread-safe `on_success` or `on_error` callbacks, ensuring the 60 FPS Pygame render loop never freezes.

### Theme 3: Interoperability

- **Heterogeneous Systems Integration**:
  - The local desktop application written in Python communicates with a remote external web service hosted on an Apache/PHP web server (`marcconrad.com/uob/fish/api.php`).
- **Data Exchange Formats**:
  - Communication is conducted over HTTP GET.
  - The response payload is transferred as JSON (`{"question": "...", "fish": 4, "chest": 8}`).
  - Binary image streams are transferred over HTTPS or delivered inline as Base64-encoded strings (`base64=yes`).
- **Protocol Translation & Format Bridging**:
  - The Python client bridges JSON strings into Python dictionaries, decodes Base64 data via `base64.b64decode()`, passes bytes into Pillow `PIL.Image`, and translates them into native `pygame.Surface` textures for SDL rendering.
- **Fault Tolerance**:
  - Robust exception handling in `FishAPIService` catches `requests.Timeout`, `requests.ConnectionError`, and HTTP error codes, surfacing diagnostic feedback to the player with a dedicated "Retry API Request" option.

### Theme 4: Virtual Identity

- **Digital Representation**:
  - A player's "Virtual Identity" represents their digital persona within the game universe. It decouples their real-world persona from their in-game achievements, nickname, and historical progress.
- **Secure Registration & Password Hashing**:
  - Implemented in `AuthManager` (`authentication/auth_manager.py`). Passwords are never stored in plaintext.
  - Uses NIST-recommended `hashlib.pbkdf2_hmac("sha256", password, salt, 100000)` combined with 16 cryptographically secure random salt bytes (`os.urandom(16)`).
  - Validation ensures unique usernames (preventing duplicate identities) and password minimum length requirements.
- **Session Management & Access Control**:
  - `AuthManager` maintains the active virtual identity in `self.current_user`.
  - Protected screens (`GameplayScreen`, `ProfileScreen`, `MenuScreen`) enforce authentication checks upon entry (`on_enter()`), redirecting unauthenticated visitors to the login screen.
- **Identity Persistence & Accountability**:
  - Every completed quest updates the player's career totals in SQLite (`highest_score`, `total_games`, `total_coins`) and logs a timestamped match history row.
  - Global achievements are reflected on the Leaderboard screen, allowing different virtual identities to compete against each other fairly.

---

## 9. Academic Integrity and Attribution

In accordance with academic integrity guidelines:
- **Architecture and Implementation**: Designed and developed as a university assessment project for CIS045-3 Distributed Service Architectures.
- **AI Assistance Disclosure**: Initial architectural scaffolding, modular organization, and UI templates were assisted by Google DeepMind's Antigravity AI pair programmer. All algorithmic logic, database schemas, cryptographic procedures, and API mappings were validated, tested, and verified.
- **External Web API**: The Fish Game puzzle service and puzzle images are provided by Prof. Marc Conrad, University of Bedfordshire ([http://marcconrad.com/uob/fish/doc.php](http://marcconrad.com/uob/fish/doc.php)).
- **Standard Libraries**: Uses Python standard libraries (`sqlite3`, `hashlib`, `hmac`, `urllib`, `threading`, `io`, `base64`) and community-standard open-source libraries (`pygame-ce`, `requests`, `pillow`).

---

## 10. External Resources and References

1. **Fish Game API Documentation**: Conrad, M. (2026). *The Fish Game API Documentation*. Available at: [http://marcconrad.com/uob/fish/doc.php](http://marcconrad.com/uob/fish/doc.php).
2. **Pygame-CE Documentation**: *Pygame Community Edition Documentation*. Available at: [https://pyga.me/docs/](https://pyga.me/docs/).
3. **Python Cryptographic Hashing**: Python Software Foundation. *hashlib — Secure hashes and message digests*. Available at: [https://docs.python.org/3/library/hashlib.html](https://docs.python.org/3/library/hashlib.html).
4. **SQLite Documentation**: Hipp, R. et al. *SQLite Database Engine*. Available at: [https://www.sqlite.org/docs.html](https://www.sqlite.org/docs.html).
5. **Coupling and Cohesion in Software Design**: Pressman, R. S. & Maxim, B. R. (2020). *Software Engineering: A Practitioner's Approach*. McGraw-Hill Education.

