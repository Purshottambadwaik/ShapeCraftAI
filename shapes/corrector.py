"""
AirSketch AI - Shape Corrector
Converts rough detected shapes into perfect geometric shapes.
"""

import cv2
import math
import numpy as np
from shapes.geometry import distance, centroid


class ShapeCorrector:
    """
    Takes a ShapeResult from the detector and generates
    perfect geometric coordinates for the corrected shape.
    """

    @staticmethod
    def correct(shape_result):
        """
        Generate perfect geometry for the detected shape.

        Args:
            shape_result: ShapeResult from ShapeDetector.

        Returns:
            dict: Corrected shape data with type-specific rendering info.
                  Keys: 'type', 'render_data', 'center', 'label_pos'
        """
        shape_type = shape_result.shape_type

        if shape_type == "triangle":
            return ShapeCorrector._correct_triangle(shape_result)
        elif shape_type in ("rectangle", "square"):
            return ShapeCorrector._correct_rectangle(shape_result)
        elif shape_type == "circle":
            return ShapeCorrector._correct_circle(shape_result)
        elif shape_type == "line":
            return ShapeCorrector._correct_line(shape_result)
        elif shape_type == "pentagon":
            return ShapeCorrector._correct_pentagon(shape_result)
        else:
            # Unknown shape — return raw points
            return {
                "type": "unknown",
                "render_data": {"points": shape_result.points},
                "center": shape_result.center,
                "label_pos": shape_result.center,
            }

    @staticmethod
    def _correct_triangle(shape_result):
        """
        Create a perfect triangle from the detected vertices.
        Preserves the approximate size and position.
        """
        vertices = shape_result.vertices
        if len(vertices) < 3:
            return {"type": "unknown", "render_data": {}, "center": (0, 0),
                    "label_pos": (0, 0)}

        # Use the 3 detected vertices directly but snap to cleaner positions
        # Calculate centroid and average distance from centroid
        cx, cy = centroid(vertices)
        avg_dist = sum(distance(v, (cx, cy)) for v in vertices) / 3

        # Compute angles of vertices relative to centroid
        angles = []
        for v in vertices:
            angle = math.atan2(v[1] - cy, v[0] - cx)
            angles.append(angle)

        # Sort by angle and redistribute evenly for equilateral-ish triangle
        angles.sort()

        # Generate corrected vertices at averaged distances
        corrected = []
        for angle in angles:
            new_x = int(cx + avg_dist * math.cos(angle))
            new_y = int(cy + avg_dist * math.sin(angle))
            corrected.append((new_x, new_y))

        label_y = min(v[1] for v in corrected) - 15
        label_pos = (cx, label_y)

        return {
            "type": "triangle",
            "render_data": {"vertices": corrected},
            "center": (cx, cy),
            "label_pos": label_pos,
        }

    @staticmethod
    def _correct_rectangle(shape_result):
        """
        Create a perfect rectangle using minAreaRect.
        """
        points = shape_result.points
        contour = np.array(points, dtype=np.float32).reshape(-1, 1, 2)

        # Get minimum area bounding rectangle
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int32(box)

        center = (int(rect[0][0]), int(rect[0][1]))
        vertices = [tuple(pt) for pt in box]

        label_y = min(v[1] for v in vertices) - 15
        label_pos = (center[0], label_y)

        # Determine if it's a square or rectangle
        width, height = rect[1]
        if width > 0 and height > 0:
            ar = max(width, height) / min(width, height)
            shape_type = "square" if abs(ar - 1.0) < 0.25 else "rectangle"
        else:
            shape_type = shape_result.shape_type

        return {
            "type": shape_type,
            "render_data": {"vertices": vertices, "box": box},
            "center": center,
            "label_pos": label_pos,
        }

    @staticmethod
    def _correct_circle(shape_result):
        """
        Create a perfect circle using minEnclosingCircle.
        """
        points = shape_result.points
        contour = np.array(points, dtype=np.float32).reshape(-1, 1, 2)

        (cx, cy), radius = cv2.minEnclosingCircle(contour)
        center = (int(cx), int(cy))
        radius = int(radius)

        label_pos = (center[0], center[1] - radius - 15)

        return {
            "type": "circle",
            "render_data": {"center": center, "radius": radius},
            "center": center,
            "label_pos": label_pos,
        }

    @staticmethod
    def _correct_line(shape_result):
        """
        Create a perfect straight line from start to end point.
        """
        vertices = shape_result.vertices
        if len(vertices) < 2:
            return {"type": "unknown", "render_data": {}, "center": (0, 0),
                    "label_pos": (0, 0)}

        start = vertices[0]
        end = vertices[-1]
        center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)

        label_pos = (center[0], center[1] - 15)

        return {
            "type": "line",
            "render_data": {"start": start, "end": end},
            "center": center,
            "label_pos": label_pos,
        }

    @staticmethod
    def _correct_pentagon(shape_result):
        """
        Create a regular pentagon from the detected vertices.
        """
        vertices = shape_result.vertices
        if len(vertices) < 5:
            return {"type": "unknown", "render_data": {}, "center": (0, 0),
                    "label_pos": (0, 0)}

        cx, cy = centroid(vertices)
        avg_dist = sum(distance(v, (cx, cy)) for v in vertices) / len(vertices)

        # Generate regular pentagon vertices
        corrected = []
        for i in range(5):
            angle = -math.pi / 2 + i * (2 * math.pi / 5)
            new_x = int(cx + avg_dist * math.cos(angle))
            new_y = int(cy + avg_dist * math.sin(angle))
            corrected.append((new_x, new_y))

        label_y = min(v[1] for v in corrected) - 15
        label_pos = (cx, label_y)

        return {
            "type": "pentagon",
            "render_data": {"vertices": corrected},
            "center": (cx, cy),
            "label_pos": label_pos,
        }
