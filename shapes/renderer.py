"""
AirSketch AI - Shape Renderer
Draws corrected perfect shapes and labels onto the canvas.
"""

import cv2
import numpy as np
from config import COLOR_SHAPE_LABEL, FONT, FONT_SCALE_SMALL, FONT_THICKNESS


class ShapeRenderer:
    """
    Renders corrected shapes and labels on the canvas surface.
    """

    @staticmethod
    def draw_shape(surface, corrected_data, color, thickness=2, filled=False):
        """
        Draw a corrected shape onto a surface.

        Args:
            surface: Canvas surface (np.array) to draw on.
            corrected_data: Dict from ShapeCorrector.correct().
            color: BGR color tuple.
            thickness: Line thickness (-1 for filled).
            filled: If True, fill the shape.
        """
        shape_type = corrected_data["type"]
        render = corrected_data["render_data"]
        draw_thickness = -1 if filled else thickness

        if shape_type == "triangle":
            pts = np.array(render["vertices"], dtype=np.int32)
            if filled:
                cv2.fillPoly(surface, [pts], color)
            else:
                cv2.polylines(surface, [pts], True, color, thickness)

        elif shape_type in ("rectangle", "square"):
            if "box" in render:
                pts = render["box"]
                if filled:
                    cv2.fillPoly(surface, [pts], color)
                else:
                    cv2.polylines(surface, [pts], True, color, thickness)
            elif "vertices" in render:
                pts = np.array(render["vertices"], dtype=np.int32)
                if filled:
                    cv2.fillPoly(surface, [pts], color)
                else:
                    cv2.polylines(surface, [pts], True, color, thickness)

        elif shape_type == "circle":
            center = render["center"]
            radius = render["radius"]
            cv2.circle(surface, center, radius, color, draw_thickness)

        elif shape_type == "line":
            start = render["start"]
            end = render["end"]
            cv2.line(surface, start, end, color, thickness)

        elif shape_type == "pentagon":
            pts = np.array(render["vertices"], dtype=np.int32)
            if filled:
                cv2.fillPoly(surface, [pts], color)
            else:
                cv2.polylines(surface, [pts], True, color, thickness)

    @staticmethod
    def draw_label(surface, corrected_data, color=COLOR_SHAPE_LABEL):
        """
        Draw a text label for the shape.

        Args:
            surface: Canvas surface to draw on.
            corrected_data: Dict from ShapeCorrector.correct().
            color: Text color (BGR).
        """
        shape_type = corrected_data["type"]
        label_pos = corrected_data.get("label_pos", corrected_data["center"])

        if shape_type == "unknown":
            return

        # Capitalize the shape name
        label = shape_type.capitalize()

        # Get text size for background
        (text_w, text_h), baseline = cv2.getTextSize(
            label, FONT, FONT_SCALE_SMALL, FONT_THICKNESS
        )

        # Draw background rectangle
        x, y = int(label_pos[0]) - text_w // 2, int(label_pos[1])
        cv2.rectangle(
            surface,
            (x - 4, y - text_h - 4),
            (x + text_w + 4, y + baseline + 4),
            (40, 40, 40),
            -1
        )

        # Draw text
        cv2.putText(
            surface, label,
            (x, y),
            FONT, FONT_SCALE_SMALL, color, 1, cv2.LINE_AA
        )

    @staticmethod
    def erase_stroke(surface, points, thickness=12):
        """
        Erase a stroke by drawing black lines over it.

        Args:
            surface: Canvas surface.
            points: List of (x, y) points of the stroke to erase.
            thickness: Erase width (should be larger than the original stroke).
        """
        if len(points) < 2:
            return

        for i in range(1, len(points)):
            cv2.line(surface, points[i - 1], points[i], (0, 0, 0), thickness)
