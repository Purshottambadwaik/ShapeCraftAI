"""
AirSketch AI - Canvas
Manages the drawing surface overlay and completed shapes.
"""

import cv2
import numpy as np
from config import CAMERA_WIDTH, CAMERA_HEIGHT


class Canvas:
    """
    Drawing canvas as a transparent overlay on top of the video frame.
    Manages the current stroke, completed shapes, and merging with the video.
    """

    def __init__(self, width=CAMERA_WIDTH, height=CAMERA_HEIGHT):
        """
        Initialize a blank canvas.

        Args:
            width: Canvas width in pixels.
            height: Canvas height in pixels.
        """
        self.width = width
        self.height = height
        # Main canvas for all finalized shapes
        self.surface = np.zeros((height, width, 3), dtype=np.uint8)
        # Temporary canvas for current stroke (drawn in real-time, cleared on stop)
        self.temp_surface = np.zeros((height, width, 3), dtype=np.uint8)
        # List of completed shape data for undo support
        self.shapes = []

    def draw_point(self, x, y, color, thickness):
        """
        Draw a single point (filled circle) on the temporary surface.

        Args:
            x, y: Point coordinates.
            color: BGR color tuple.
            thickness: Circle radius.
        """
        cv2.circle(self.temp_surface, (x, y), thickness // 2 + 1, color, -1)

    def draw_line(self, prev, curr, color, thickness):
        """
        Draw a line segment on the temporary surface.

        Args:
            prev: Previous point (x, y).
            curr: Current point (x, y).
            color: BGR color tuple.
            thickness: Line thickness.
        """
        cv2.line(self.temp_surface, prev, curr, color, thickness)

    def commit_stroke(self):
        """
        Commit the temporary surface (current stroke) to the main surface.
        Called when stroke is finalized (before shape detection).
        """
        # Merge temp into main
        mask = np.any(self.temp_surface > 0, axis=2)
        self.surface[mask] = self.temp_surface[mask]
        self.clear_temp()

    def clear_temp(self):
        """Clear the temporary drawing surface."""
        self.temp_surface = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def draw_shape_on_surface(self, draw_func):
        """
        Draw a shape directly on the main surface using a provided drawing function.

        Args:
            draw_func: A function that takes a surface (np.array) and draws on it.
        """
        draw_func(self.surface)

    def remove_last_shape_area(self, draw_func_black):
        """
        Erase the rough stroke by drawing black over it.

        Args:
            draw_func_black: A function that draws the area to erase in black.
        """
        draw_func_black(self.surface)

    def add_shape_record(self, shape_data):
        """
        Add a shape record for undo tracking.

        Args:
            shape_data: Dict containing shape info and the canvas snapshot.
        """
        self.shapes.append(shape_data)

    def clear(self):
        """Clear the entire canvas (all shapes and strokes)."""
        self.surface = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.temp_surface = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.shapes = []

    def get_overlay(self):
        """
        Get the combined overlay (main surface + temp surface).

        Returns:
            np.array: Combined drawing surface.
        """
        combined = self.surface.copy()
        mask = np.any(self.temp_surface > 0, axis=2)
        combined[mask] = self.temp_surface[mask]
        return combined

    def merge_with_frame(self, frame):
        """
        Merge the canvas overlay onto a video frame.

        Args:
            frame: BGR video frame.

        Returns:
            np.array: Frame with canvas overlay.
        """
        overlay = self.get_overlay()
        # Use addWeighted for areas with content, keep frame where canvas is black
        gray = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

        # Where canvas has content, blend it on top
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) // 255
        result = frame * (1 - mask_3ch) + overlay * mask_3ch
        return result.astype(np.uint8)

    def get_snapshot(self):
        """
        Get a deep copy of the current canvas state for undo.

        Returns:
            np.array: Copy of the main surface.
        """
        return self.surface.copy()

    def restore_snapshot(self, snapshot):
        """
        Restore canvas from a snapshot.

        Args:
            snapshot: Previously saved canvas state.
        """
        self.surface = snapshot.copy()
