"""In-memory timer state."""

import time

# Longest timer we allow, to keep a typo from locking up the egg.
MAX_DURATION_SECONDS = 24 * 60 * 60


class EggTimer:
    """One timer that remembers when it started and how long it should run."""

    def __init__(self):
        self.duration_seconds = None
        self._started_at = None

    def start(self, duration_seconds=None):
        """Begin timing, optionally counting down from `duration_seconds`."""
        self.duration_seconds = duration_seconds
        self._started_at = time.monotonic()

    def stop(self):
        """Stop timing. Returns False if the timer was not running."""
        if self._started_at is None:
            return False
        if self.duration_seconds is None:
            # A stopwatch: freeze it where it stands so elapsed time holds still.
            self.duration_seconds = self.elapsed_seconds
        self._started_at = None
        return True

    @property
    def running(self):
        return self._started_at is not None

    @property
    def elapsed_seconds(self):
        """Seconds counted so far. Frozen once stopped, capped while counting down."""
        if self._started_at is None:
            return self.duration_seconds or 0.0
        elapsed = time.monotonic() - self._started_at
        if self.duration_seconds is None:
            return elapsed
        return min(elapsed, self.duration_seconds)

    @property
    def remaining_seconds(self):
        """Seconds left on a countdown, or None if no duration was given."""
        if self.duration_seconds is None:
            return None
        return max(self.duration_seconds - self.elapsed_seconds, 0.0)

    @property
    def finished(self):
        """True when a countdown has run out and nothing has restarted it."""
        return (
            self.duration_seconds is not None
            and self.elapsed_seconds >= self.duration_seconds
        )

    def status(self):
        """Plain data describing the timer, ready to send as JSON."""
        return {
            "running": self.running,
            "elapsed_seconds": self.elapsed_seconds,
            "duration_seconds": self.duration_seconds,
            "remaining_seconds": self.remaining_seconds,
            "finished": self.finished,
        }
