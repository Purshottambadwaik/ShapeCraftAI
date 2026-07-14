"""
AirSketch AI - FPS Counter
Tracks and calculates frames per second using time-based averaging.
"""

import time
from config import FPS_AVG_FRAMES


class FPSCounter:
    """
    Calculates and smooths FPS over a rolling window of frames.
    """

    def __init__(self, avg_frames=FPS_AVG_FRAMES):
        """
        Initialize FPS counter.

        Args:
            avg_frames: Number of frames to average over for stable FPS display.
        """
        self.avg_frames = avg_frames
        self.timestamps = []
        self.fps = 0.0

    def update(self):
        """
        Call once per frame to update the FPS calculation.
        """
        now = time.time()
        self.timestamps.append(now)

        # Keep only the last N timestamps
        if len(self.timestamps) > self.avg_frames:
            self.timestamps = self.timestamps[-self.avg_frames:]

        # Calculate FPS from time difference
        if len(self.timestamps) >= 2:
            elapsed = self.timestamps[-1] - self.timestamps[0]
            if elapsed > 0:
                self.fps = (len(self.timestamps) - 1) / elapsed

    def get_fps(self):
        """
        Returns the current smoothed FPS value.

        Returns:
            float: Current FPS.
        """
        return self.fps

    def get_fps_text(self):
        """
        Returns formatted FPS string for display.

        Returns:
            str: FPS formatted as "XX FPS".
        """
        return f"{int(self.fps)} FPS"
