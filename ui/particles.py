"""
Fish Quest - Ocean Adventure Game
Underwater Ambience & Bubble Particle System

Demonstrates:
- Visual Design & Simulation:
  Renders realistic, floating underwater bubbles and ambient effects to create
  an immersive oceanic experience.
"""

import math
import random
from typing import List, Dict, Any
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class BubbleParticleSystem:
    """
    Simulates floating underwater bubbles with smooth swaying motion and alpha transparency.
    """

    def __init__(self, count: int = 35):
        self.count = count
        self.particles: List[Dict[str, Any]] = []
        self._init_particles()

    def _init_particles(self) -> None:
        """Populates particles with randomized positions, speeds, and sizes."""
        for _ in range(self.count):
            self.particles.append(self._create_particle(random_y=True))

    def _create_particle(self, random_y: bool = False) -> Dict[str, Any]:
        """Generates a single bubble particle."""
        radius = random.randint(3, 10)
        speed = random.uniform(0.6, 2.2)
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT) if random_y else SCREEN_HEIGHT + random.randint(10, 50)
        wobble_speed = random.uniform(1.5, 3.5)
        wobble_amp = random.uniform(15, 35)
        alpha = random.randint(60, 160)

        return {
            "x": float(x),
            "y": float(y),
            "base_x": float(x),
            "radius": radius,
            "speed": speed,
            "wobble_speed": wobble_speed,
            "wobble_amp": wobble_amp,
            "wobble_time": random.uniform(0, 10),
            "alpha": alpha
        }

    def update(self, dt: float = 0.016) -> None:
        """Updates particle coordinates and resets bubbles that leave the screen."""
        for p in self.particles:
            p["y"] -= p["speed"] * (dt * 60)
            p["wobble_time"] += dt * p["wobble_speed"]
            p["x"] = p["base_x"] + math.sin(p["wobble_time"]) * p["wobble_amp"]

            # Wrap around when bubble reaches the ocean surface
            if p["y"] < -20:
                new_p = self._create_particle(random_y=False)
                p.update(new_p)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders all bubbles with soft transparency onto the target surface."""
        for p in self.particles:
            r = int(p["radius"])
            size = r * 2 + 4
            bubble_surf = pygame.Surface((size, size), pygame.SRCALPHA)

            center = (size // 2, size // 2)
            # Outer bubble ring
            pygame.draw.circle(
                bubble_surf,
                (200, 240, 255, p["alpha"]),
                center,
                r,
                width=1
            )
            # Soft inner glow
            pygame.draw.circle(
                bubble_surf,
                (180, 230, 255, max(15, p["alpha"] // 4)),
                center,
                max(1, r - 1)
            )
            # Highlight reflection dot
            highlight_x = center[0] - max(1, r // 3)
            highlight_y = center[1] - max(1, r // 3)
            highlight_r = max(1, r // 4)
            pygame.draw.circle(
                bubble_surf,
                (255, 255, 255, min(255, p["alpha"] + 60)),
                (highlight_x, highlight_y),
                highlight_r
            )

            surface.blit(bubble_surf, (int(p["x"]) - size // 2, int(p["y"]) - size // 2))

