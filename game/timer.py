"""
Fish Quest - Ocean Adventure Game
Game Countdown Timer Module

Demonstrates:
- High Cohesion: Purely responsible for time tracking, delta updates,
  pause/resume management, and expiration notifications.
- Event-Driven Programming: Emits expiration triggers when the countdown hits zero.
"""

import time
from typing import Optional, Callable


class CountdownTimer:
    """
    A robust, frame-independent countdown timer with pause and resume capabilities.
    """

    def __init__(self, initial_duration: float = 25.0, on_expire: Optional[Callable[[], None]] = None):
        self.duration = float(initial_duration)
        self.time_remaining = float(initial_duration)
        self.is_paused = False
        self.is_active = False
        self.on_expire = on_expire
        self._last_tick = time.time()

    def start(self, duration: Optional[float] = None) -> None:
        """Starts or resets the timer with the specified duration."""
        if duration is not None:
            self.duration = float(duration)
        self.time_remaining = self.duration
        self.is_active = True
        self.is_paused = False
        self._last_tick = time.time()

    def pause(self) -> None:
        """Pauses the countdown without resetting remaining time."""
        if self.is_active and not self.is_paused:
            self._update_remaining()
            self.is_paused = True

    def resume(self) -> None:
        """Resumes countdown from paused state."""
        if self.is_active and self.is_paused:
            self.is_paused = False
            self._last_tick = time.time()

    def toggle_pause(self) -> bool:
        """Toggles between paused and running state. Returns is_paused."""
        if self.is_paused:
            self.resume()
        else:
            self.pause()
        return self.is_paused

    def stop(self) -> None:
        """Stops the timer completely."""
        self.is_active = False
        self.is_paused = False

    def update(self) -> bool:
        """
        Updates the timer using real wall-clock delta time.
        Must be called once per frame in the game loop.
        Returns True if the timer just expired on this frame.
        """
        if not self.is_active or self.is_paused:
            return False

        now = time.time()
        delta = now - self._last_tick
        self._last_tick = now

        self.time_remaining -= delta

        if self.time_remaining <= 0.0:
            self.time_remaining = 0.0
            self.is_active = False
            if self.on_expire:
                self.on_expire()
            return True

        return False

    def _update_remaining(self) -> None:
        now = time.time()
        delta = now - self._last_tick
        self._last_tick = now
        self.time_remaining = max(0.0, self.time_remaining - delta)

    @property
    def seconds_left(self) -> int:
        """Returns integer seconds remaining (rounded up for user clarity)."""
        return int(max(0, self.time_remaining + 0.99))

    @property
    def progress_ratio(self) -> float:
        """Returns normalized ratio [0.0, 1.0] representing remaining time."""
        if self.duration <= 0:
            return 0.0
        return max(0.0, min(1.0, self.time_remaining / self.duration))

