"""
AirSketch AI - Button
Clickable rectangular UI button component for the toolbar.
"""

import cv2
from config import (
    COLOR_BUTTON_BG, COLOR_BUTTON_HOVER,
    COLOR_BUTTON_ACTIVE, COLOR_BUTTON_TEXT,
    FONT, FONT_SCALE_SMALL, FONT_THICKNESS
)


class Button:
    """
    A rectangular clickable button drawn on the OpenCV frame.
    """

    def __init__(self, x, y, w, h, label="", color=None, action=None,
                 is_color_button=False):
        """
        Initialize a button.

        Args:
            x, y: Top-left corner position.
            w, h: Width and height.
            label: Text label to display.
            color: Button fill color (BGR). If None, uses default.
            action: String identifier for the button action.
            is_color_button: If True, this button represents a color selection.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.color = color if color else COLOR_BUTTON_BG
        self.action = action
        self.is_color_button = is_color_button
        self.is_active = False
        self.is_hovered = False

    def contains(self, px, py):
        """
        Check if a point is inside this button.

        Args:
            px, py: Point coordinates.

        Returns:
            bool: True if the point is inside the button.
        """
        return (self.x <= px <= self.x + self.w and
                self.y <= py <= self.y + self.h)

    def draw(self, frame):
        """
        Draw the button on the frame.

        Args:
            frame: The OpenCV frame to draw on.
        """
        # Determine background color based on state
        if self.is_active:
            bg_color = COLOR_BUTTON_ACTIVE
        elif self.is_hovered:
            bg_color = COLOR_BUTTON_HOVER
        else:
            bg_color = self.color if self.is_color_button else COLOR_BUTTON_BG

        # Draw filled rectangle
        cv2.rectangle(
            frame,
            (self.x, self.y),
            (self.x + self.w, self.y + self.h),
            bg_color,
            -1
        )

        # Draw border
        border_color = COLOR_BUTTON_ACTIVE if self.is_active else (100, 100, 100)
        cv2.rectangle(
            frame,
            (self.x, self.y),
            (self.x + self.w, self.y + self.h),
            border_color,
            2
        )

        # Draw color swatch if it's a color button
        if self.is_color_button:
            padding = 4
            cv2.rectangle(
                frame,
                (self.x + padding, self.y + padding),
                (self.x + self.w - padding, self.y + self.h - padding),
                self.color,
                -1
            )
            # Active indicator — white border
            if self.is_active:
                cv2.rectangle(
                    frame,
                    (self.x, self.y),
                    (self.x + self.w, self.y + self.h),
                    (255, 255, 255),
                    2
                )
        elif self.label:
            # Draw text label
            (text_w, text_h), _ = cv2.getTextSize(
                self.label, FONT, FONT_SCALE_SMALL, 1
            )
            text_x = self.x + (self.w - text_w) // 2
            text_y = self.y + (self.h + text_h) // 2
            cv2.putText(
                frame, self.label,
                (text_x, text_y),
                FONT, FONT_SCALE_SMALL, COLOR_BUTTON_TEXT, 1, cv2.LINE_AA
            )
