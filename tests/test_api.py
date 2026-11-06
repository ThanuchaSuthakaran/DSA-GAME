"""
Unit Tests for External Fish Game API Integration Module
Fish Quest - Ocean Adventure Game
"""

import unittest
from unittest.mock import patch, MagicMock
import base64
import io
from PIL import Image
import pygame

from api.fish_api import FishAPIService, FishPuzzle


class TestFishAPIService(unittest.TestCase):
    """Verifies API parsing, Base64 decoding, image conversion, and error handling."""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def setUp(self):
        self.api = FishAPIService()

    def _create_dummy_png_bytes(self) -> bytes:
        """Helper to create minimal valid PNG binary bytes."""
        img = Image.new("RGBA", (100, 50), (10, 50, 100, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @patch("requests.get")
    def test_parse_json_with_fish_and_chest_fields(self, mock_get):
        png_bytes = self._create_dummy_png_bytes()

        # Mock API JSON response
        mock_api_resp = MagicMock()
        mock_api_resp.status_code = 200
        mock_api_resp.json.return_value = {
            "question": "https://www.sanfoh.com/uob/fish/data/ch_sample.png",
            "fish": 5,
            "chest": 3
        }

        # Mock image download response
        mock_img_resp = MagicMock()
        mock_img_resp.status_code = 200
        mock_img_resp.content = png_bytes

        # requests.get will return API response first, then image response
        mock_get.side_effect = [mock_api_resp, mock_img_resp]

        puzzle = self.api.fetch_puzzle(use_base64=False)

        self.assertIsInstance(puzzle, FishPuzzle)
        self.assertEqual(puzzle.solution, 5)
        self.assertEqual(puzzle.fish_count, 5)
        self.assertEqual(puzzle.chest_count, 3)
        self.assertFalse(puzzle.is_base64)
        self.assertIsNotNone(puzzle.image_surface)
        self.assertEqual(puzzle.image_surface.get_size(), (100, 50))

    @patch("requests.get")
    def test_parse_base64_encoded_payload(self, mock_get):
        png_bytes = self._create_dummy_png_bytes()
        b64_str = base64.b64encode(png_bytes).decode("ascii")

        mock_api_resp = MagicMock()
        mock_api_resp.status_code = 200
        mock_api_resp.json.return_value = {
            "question": b64_str,
            "fish": 8,
            "chest": 0
        }
        mock_get.return_value = mock_api_resp

        puzzle = self.api.fetch_puzzle(use_base64=True)

        self.assertIsInstance(puzzle, FishPuzzle)
        self.assertEqual(puzzle.solution, 8)
        self.assertTrue(puzzle.is_base64)
        self.assertIsNotNone(puzzle.image_surface)

    @patch("requests.get")
    def test_missing_question_field_raises_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"fish": 4}  # missing 'question'
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError) as ctx:
            self.api.fetch_puzzle()
        self.assertIn("missing mandatory 'question' field", str(ctx.exception).lower())

    @patch("requests.get")
    def test_missing_numerical_solution_raises_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"question": "http://example.com/img.png"}
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError) as ctx:
            self.api.fetch_puzzle()
        self.assertIn("could not extract a valid numerical solution", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()

