"""
AirSketch AI - Point Smoother
Smooths hand tracking points to reduce jitter using EMA and moving average.
"""

from collections import deque
from config import SMOOTHING_FACTOR, MOVING_AVG_WINDOW


class PointSmoother:
    """
    Smooths a stream of (x, y) points using Exponential Moving Average (EMA)
    and/or a simple moving average filter.
    """

    def __init__(self, alpha=SMOOTHING_FACTOR, window_size=MOVING_AVG_WINDOW):
        """
        Initialize the smoother.

        Args:
            alpha: EMA smoothing factor (0 = no smoothing, higher = more lag).
            window_size: Number of recent points for moving average.
        """
        self.alpha = alpha
        self.window_size = window_size
        self.prev_x = None
        self.prev_y = None
        self.history = deque(maxlen=window_size)

    def smooth_ema(self, x, y):
        """
        Apply Exponential Moving Average smoothing.

        Args:
            x, y: Raw input coordinates.

        Returns:
            tuple: Smoothed (x, y) coordinates.
        """
        if self.prev_x is None:
            self.prev_x = x
            self.prev_y = y
            return (x, y)

        smooth_x = int(self.prev_x + self.alpha * (x - self.prev_x))
        smooth_y = int(self.prev_y + self.alpha * (y - self.prev_y))

        self.prev_x = smooth_x
        self.prev_y = smooth_y

        return (smooth_x, smooth_y)

    def smooth_moving_avg(self, x, y):
        """
        Apply Simple Moving Average smoothing.

        Args:
            x, y: Raw input coordinates.

        Returns:
            tuple: Smoothed (x, y) coordinates.
        """
        self.history.append((x, y))

        if len(self.history) == 0:
            return (x, y)

        avg_x = sum(p[0] for p in self.history) // len(self.history)
        avg_y = sum(p[1] for p in self.history) // len(self.history)

        return (avg_x, avg_y)

    def smooth(self, x, y):
        """
        Apply combined smoothing (EMA as primary, with moving average history).

        Args:
            x, y: Raw input coordinates.

        Returns:
            tuple: Smoothed (x, y) coordinates.
        """
        # First apply EMA
        sx, sy = self.smooth_ema(x, y)
        # Then apply moving average on the EMA output
        return self.smooth_moving_avg(sx, sy)

    def reset(self):
        """Reset the smoother state (call when starting a new stroke)."""
        self.prev_x = None
        self.prev_y = None
        self.history.clear()
