"""
Fish Quest - Ocean Adventure Game
External Fish Game API Service Module

Demonstrates:
- Interoperability:
  Integrates a remote RESTful web service (Marc Conrad's Fish Game API at the
  University of Bedfordshire) with a Python desktop client.
  Demonstrates HTTP protocol communication, JSON serialisation/deserialisation,
  dynamic schema inspection, Base64 decoding, and binary image stream loading.
- Event-Driven & Non-Blocking Design:
  Provides asynchronous background thread dispatching so that network latency
  never freezes the 60 FPS Pygame render loop.
- Low Coupling:
  Translates remote heterogeneous web responses into a clean, strongly-typed
  `FishPuzzle` domain object, shielding the UI from API-level details.
"""

import io
import base64
import threading
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any

import requests
from PIL import Image
import pygame

from config.settings import API_BASE_URL, API_TIMEOUT_SECONDS


@dataclass
class FishPuzzle:
    """
    Strongly typed domain entity representing a retrieved Fish Game puzzle.
    Contains the question source, the verified numerical solution, extra metadata,
    and a ready-to-render Pygame Surface.
    """
    image_url: str
    solution: int
    fish_count: int
    chest_count: Optional[int]
    image_surface: Optional[pygame.Surface] = None
    is_base64: bool = False
    raw_bytes: Optional[bytes] = None


class FishAPIService:
    """
    Encapsulates all communication with the external Fish Game API.
    Handles network requests, JSON decoding, Base64 image decoding,
    Pillow stream conversions, and background threading.
    """

    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT_SECONDS):
        self.base_url = base_url
        self.timeout = timeout
        self._current_worker: Optional[threading.Thread] = None

    def fetch_puzzle(self, use_base64: bool = False) -> FishPuzzle:
        """
        Synchronously requests a new puzzle from the external API.
        
        Steps:
          1. Performs HTTP GET request to `api.php?out=json[&base64=yes]`.
          2. Parses JSON payload.
          3. Dynamically extracts the image data and solution value.
          4. Downloads/decodes the image binary bytes.
          5. Converts bytes into a Pygame Surface via io.BytesIO and Pillow.
          6. Returns a populated FishPuzzle instance.
          
        Raises:
          requests.RequestException: If network connection fails or times out.
          ValueError: If the JSON payload lacks required fields or is malformed.
        """
        params = {"out": "json"}
        if use_base64:
            params["base64"] = "yes"

        # Step 1: Make HTTP Request
        # Interoperability: Standard HTTP GET request over TCP/IP
        response = requests.get(self.base_url, params=params, timeout=self.timeout)
        response.raise_for_status()

        # Step 2: JSON Deserialization
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError(f"Unexpected API response type: expected dict, got {type(data)}")

        # Step 3: Inspect Actual Response Schema
        # The API returns 'question' (URL or base64 data) and numerical solution keys
        # ('fish' count and 'chest' count; some variants may provide 'solution').
        question_data = data.get("question")
        if not question_data:
            raise ValueError(f"API JSON missing mandatory 'question' field: {data}")

        # Extract numeric solution: prioritize 'solution', then 'fish', then any int value
        solution_val: Optional[int] = None
        if "solution" in data and data["solution"] is not None:
            solution_val = int(data["solution"])
        elif "fish" in data and data["fish"] is not None:
            solution_val = int(data["fish"])
        else:
            # Fallback search for any integer in response
            for k, v in data.items():
                if k != "question" and isinstance(v, (int, str)) and str(v).isdigit():
                    solution_val = int(v)
                    break

        if solution_val is None:
            raise ValueError(f"Could not extract a valid numerical solution from API response: {data}")

        fish_count = int(data.get("fish", solution_val))
        chest_count = int(data["chest"]) if "chest" in data and str(data["chest"]).isdigit() else None

        # Step 4 & 5: Load and convert image to Pygame surface
        image_surface, raw_bytes, is_b64 = self._process_image(question_data)

        return FishPuzzle(
            image_url=question_data if not is_b64 else "[Base64 Data]",
            solution=solution_val,
            fish_count=fish_count,
            chest_count=chest_count,
            image_surface=image_surface,
            is_base64=is_b64,
            raw_bytes=raw_bytes
        )

    def _process_image(self, question_str: str) -> tuple[pygame.Surface, bytes, bool]:
        """
        Decodes Base64 or downloads from HTTP URL, processes through Pillow/Pygame,
        and returns (pygame.Surface, raw_bytes, is_base64).
        """
        is_base64 = False
        raw_bytes: bytes

        # Check if question is Base64 encoded or a remote URL
        clean_str = question_str.strip()
        if clean_str.startswith("http://") or clean_str.startswith("https://"):
            # Download the binary image stream
            img_res = requests.get(clean_str, timeout=self.timeout)
            img_res.raise_for_status()
            raw_bytes = img_res.content
        else:
            # Base64 string decoding
            is_base64 = True
            # Strip data URI header if present (e.g. data:image/png;base64,...)
            if "," in clean_str:
                clean_str = clean_str.split(",", 1)[1]
            raw_bytes = base64.b64decode(clean_str)

        # Use Pillow to ensure image integrity and handle alpha transparency if needed
        pil_image = Image.open(io.BytesIO(raw_bytes))
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")

        # Convert Pillow image into a native Pygame Surface
        image_bytes = pil_image.tobytes()
        if hasattr(pygame.image, "frombytes"):
            surface = pygame.image.frombytes(image_bytes, pil_image.size, "RGBA")
        else:
            surface = pygame.image.fromstring(image_bytes, pil_image.size, "RGBA")

        return surface, raw_bytes, is_base64

    def fetch_puzzle_async(
        self,
        on_success: Callable[[FishPuzzle], None],
        on_error: Callable[[str], None],
        use_base64: bool = False
    ) -> None:
        """
        Spawns a daemon thread to retrieve a puzzle asynchronously.
        Demonstrates non-blocking event-driven programming: the main Pygame
        loop can display loading animations and handle user events while
        the network request completes in the background.
        """
        def worker():
            try:
                puzzle = self.fetch_puzzle(use_base64=use_base64)
                on_success(puzzle)
            except requests.Timeout:
                on_error("Connection timed out while contacting the Fish Game API. Please check your internet.")
            except requests.ConnectionError:
                on_error("Unable to reach the Fish Game API server (marcconrad.com). Please verify connectivity.")
            except requests.HTTPError as he:
                on_error(f"HTTP error occurred from Fish API: {he.response.status_code}")
            except Exception as e:
                on_error(f"Failed to load puzzle: {str(e)}")

        self._current_worker = threading.Thread(target=worker, daemon=True)
        self._current_worker.start()
