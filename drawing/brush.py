"""
AirSketch AI - Brush
Manages brush properties: color, size, and eraser mode.
"""

from config import (
    DEFAULT_DRAW_COLOR, DEFAULT_BRUSH_SIZE,
    MIN_BRUSH_SIZE, MAX_BRUSH_SIZE, BRUSH_SIZE_STEP
)


class Brush:
    """
    Represents the drawing brush with configurable color and size.
    """

    def __init__(self, color=DEFAULT_DRAW_COLOR, size=DEFAULT_BRUSH_SIZE):
        """
        Initialize the brush.

        Args:
            color: BGR color tuple.
            size: Brush thickness in pixels.
        """
        self.color = color
        self.size = size
        self.is_eraser = False
        self._saved_color = color  # Store color when switching to eraser

    def set_color(self, color):
        """
        Set brush color and disable eraser mode.

        Args:
            color: BGR color tuple.
        """
        self.color = color
        self._saved_color = color
        self.is_eraser = False

    def set_size(self, size):
        """
        Set brush size (clamped to valid range).

        Args:
            size: Desired brush size.
        """
        self.size = max(MIN_BRUSH_SIZE, min(MAX_BRUSH_SIZE, size))

    def increase_size(self):
        """Increase brush size by one step."""
        self.set_size(self.size + BRUSH_SIZE_STEP)

    def decrease_size(self):
        """Decrease brush size by one step."""
        self.set_size(self.size - BRUSH_SIZE_STEP)

    def toggle_eraser(self):
        """Toggle between eraser and drawing mode."""
        if self.is_eraser:
            self.is_eraser = False
            self.color = self._saved_color
        else:
            self.is_eraser = True
            self._saved_color = self.color
            self.color = (0, 0, 0)  # Black = erase

    def get_draw_color(self):
        """
        Get the current drawing color.

        Returns:
            tuple: BGR color for drawing.
        """
        return self.color

    def get_draw_size(self):
        """
        Get the current brush size. Eraser uses larger size.

        Returns:
            int: Brush thickness.
        """
        if self.is_eraser:
            return self.size * 3  # Eraser is wider
        return self.size
