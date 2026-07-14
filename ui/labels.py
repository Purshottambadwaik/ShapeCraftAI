"""
AirSketch AI - Labels
Text overlay components for displaying status, FPS, and shape info.
"""

import cv2
from config import (
    FONT, FONT_SCALE_SMALL, FONT_SCALE_MEDIUM,
    FONT_SCALE_LARGE, FONT_THICKNESS, COLOR_WHITE
)


class Label:
    """
    Draws text labels and status overlays on the frame.
    """

    @staticmethod
    def draw_text(frame, text, position, color=COLOR_WHITE,
                  scale=FONT_SCALE_MEDIUM, thickness=FONT_THICKNESS,
                  bg=True, bg_color=(0, 0, 0), bg_alpha=0.6):
        """
        Draw text on the frame with optional background.

        Args:
            frame: The OpenCV frame.
            text: Text string to display.
            position: (x, y) position for the text.
            color: Text color (BGR).
            scale: Font scale.
            thickness: Text thickness.
            bg: Whether to draw a background rectangle.
            bg_color: Background color.
            bg_alpha: Background opacity (not used in simple mode).
        """
        x, y = position

        if bg:
            (text_w, text_h), baseline = cv2.getTextSize(
                text, FONT, scale, thickness
            )
            cv2.rectangle(
                frame,
                (x - 4, y - text_h - 6),
                (x + text_w + 4, y + baseline + 4),
                bg_color,
                -1
            )

        cv2.putText(
            frame, text, (x, y),
            FONT, scale, color, thickness, cv2.LINE_AA
        )

    @staticmethod
    def draw_fps(frame, fps_text, position=(10, 30)):
        """
        Draw FPS counter on the frame.

        Args:
            frame: The OpenCV frame.
            fps_text: FPS text string (e.g., "30 FPS").
            position: Where to draw.
        """
        Label.draw_text(
            frame, fps_text, position,
            color=(0, 255, 0), scale=FONT_SCALE_SMALL, thickness=1
        )

    @staticmethod
    def draw_mode(frame, mode_name, position=(10, 60), color=None):
        """
        Draw the current mode indicator (DRAW, ERASE, SELECT, etc.).

        Args:
            frame: The OpenCV frame.
            mode_name: Mode name string.
            position: Where to draw.
            color: Text color. If None, auto-selected by mode.
        """
        mode_colors = {
            "DRAW": (0, 255, 0),
            "STOP": (0, 0, 255),
            "ERASE": (0, 165, 255),
            "SELECT": (255, 255, 0),
            "IDLE": (128, 128, 128),
        }
        if color is None:
            color = mode_colors.get(mode_name, COLOR_WHITE)

        Label.draw_text(
            frame, f"Mode: {mode_name}", position,
            color=color, scale=FONT_SCALE_SMALL, thickness=1
        )

    @staticmethod
    def draw_shape_info(frame, shape_name, position=(10, 90)):
        """
        Display detected shape information.

        Args:
            frame: The OpenCV frame.
            shape_name: Name of the detected shape.
            position: Where to draw.
        """
        if shape_name and shape_name != "unknown":
            Label.draw_text(
                frame, f"Shape: {shape_name.capitalize()}", position,
                color=(255, 200, 100), scale=FONT_SCALE_SMALL, thickness=1
            )

    @staticmethod
    def draw_undo_count(frame, count, position=None):
        """
        Display the number of available undo steps.

        Args:
            frame: The OpenCV frame.
            count: Number of undo steps available.
            position: Where to draw. If None, auto-positioned.
        """
        if position is None:
            h = frame.shape[0]
            position = (10, h - 20)

        Label.draw_text(
            frame, f"Undo: {count}", position,
            color=(180, 180, 180), scale=FONT_SCALE_SMALL, thickness=1
        )

    @staticmethod
    def draw_notification(frame, message, duration_frames=60):
        """
        Draw a centered notification message.

        Args:
            frame: The OpenCV frame.
            message: Notification text.
            duration_frames: Not used here (handled by caller).
        """
        h, w = frame.shape[:2]
        (text_w, text_h), _ = cv2.getTextSize(
            message, FONT, FONT_SCALE_LARGE, FONT_THICKNESS
        )
        x = (w - text_w) // 2
        y = h // 2

        # Semi-transparent background
        cv2.rectangle(
            frame,
            (x - 20, y - text_h - 20),
            (x + text_w + 20, y + 20),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            frame, message,
            (x, y),
            FONT, FONT_SCALE_LARGE, (0, 255, 150), FONT_THICKNESS, cv2.LINE_AA
        )
