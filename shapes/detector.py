"""
AirSketch AI - Shape Detector
Analyzes drawn strokes and classifies them as geometric shapes.
"""

import cv2
import numpy as np
from config import (
    APPROX_POLY_EPSILON, CIRCULARITY_THRESHOLD,
    MIN_CONTOUR_AREA, SQUARE_ASPECT_RATIO_TOLERANCE,
    LINE_STRAIGHTNESS_THRESHOLD, MIN_POINTS_FOR_SHAPE
)
from shapes.geometry import (
    circularity, aspect_ratio, distance,
    points_to_contour, centroid, bounding_box
)


class ShapeResult:
    """
    Holds the result of shape detection.
    """

    def __init__(self, shape_type="unknown", vertices=None, center=(0, 0),
                 dimensions=None, confidence=0.0, contour=None, points=None):
        """
        Args:
            shape_type: One of 'triangle', 'rectangle', 'square', 'circle',
                        'pentagon', 'line', 'unknown'.
            vertices: Approximated polygon vertices.
            center: Center point of the shape.
            dimensions: Shape-specific dimensions (e.g., radius for circle).
            confidence: Detection confidence (0-1).
            contour: OpenCV contour of the drawn stroke.
            points: Original drawn points.
        """
        self.shape_type = shape_type
        self.vertices = vertices if vertices is not None else []
        self.center = center
        self.dimensions = dimensions if dimensions is not None else {}
        self.confidence = confidence
        self.contour = contour
        self.points = points if points is not None else []

    def __str__(self):
        return (f"Shape: {self.shape_type} | Center: {self.center} | "
                f"Confidence: {self.confidence:.2f}")


class ShapeDetector:
    """
    Detects geometric shapes from a list of drawn points using
    contour approximation and geometric analysis.
    """

    def __init__(self):
        self.epsilon_factor = APPROX_POLY_EPSILON
        self.circularity_threshold = CIRCULARITY_THRESHOLD
        self.min_area = MIN_CONTOUR_AREA
        self.square_tolerance = SQUARE_ASPECT_RATIO_TOLERANCE
        self.line_threshold = LINE_STRAIGHTNESS_THRESHOLD

    def detect(self, points):
        """
        Analyze a list of drawn points and classify the shape.

        Args:
            points: List of (x, y) tuples representing the drawn stroke.

        Returns:
            ShapeResult: Detected shape information.
        """
        if len(points) < MIN_POINTS_FOR_SHAPE:
            return ShapeResult(shape_type="unknown", points=points)

        # Convert points to contour
        contour = points_to_contour(points)

        # Check if it's a line first (before closing the contour)
        line_result = self._check_line(points, contour)
        if line_result is not None:
            return line_result

        # Close the contour by connecting last point to first
        closed_points = points + [points[0]]
        contour = points_to_contour(closed_points)

        # Calculate contour properties
        area = cv2.contourArea(contour)
        if area < self.min_area:
            # Too small — might be a line or just noise
            return self._check_line(points, points_to_contour(points)) or \
                   ShapeResult(shape_type="unknown", points=points, contour=contour)

        # Approximate the polygon
        perimeter = cv2.arcLength(contour, True)
        epsilon = self.epsilon_factor * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        num_vertices = len(approx)

        # Extract vertex positions
        vertices = [(int(pt[0][0]), int(pt[0][1])) for pt in approx]
        center_pt = centroid(vertices)

        # Classify based on vertex count
        if num_vertices == 3:
            return ShapeResult(
                shape_type="triangle",
                vertices=vertices,
                center=center_pt,
                dimensions={"area": area},
                confidence=0.85,
                contour=contour,
                points=points
            )

        elif num_vertices == 4:
            # Check if it's a square or rectangle
            ar = aspect_ratio(vertices)
            if abs(ar - 1.0) < self.square_tolerance:
                shape_type = "square"
            else:
                shape_type = "rectangle"

            return ShapeResult(
                shape_type=shape_type,
                vertices=vertices,
                center=center_pt,
                dimensions={"area": area, "aspect_ratio": ar},
                confidence=0.85,
                contour=contour,
                points=points
            )

        elif num_vertices == 5:
            return ShapeResult(
                shape_type="pentagon",
                vertices=vertices,
                center=center_pt,
                dimensions={"area": area},
                confidence=0.7,
                contour=contour,
                points=points
            )

        else:
            # Many vertices — check if it's a circle
            circ = circularity(contour)
            if circ > self.circularity_threshold:
                (cx, cy), radius = cv2.minEnclosingCircle(contour)
                return ShapeResult(
                    shape_type="circle",
                    vertices=vertices,
                    center=(int(cx), int(cy)),
                    dimensions={"radius": int(radius), "area": area,
                                "circularity": circ},
                    confidence=circ,
                    contour=contour,
                    points=points
                )
            else:
                return ShapeResult(
                    shape_type="unknown",
                    vertices=vertices,
                    center=center_pt,
                    dimensions={"area": area, "circularity": circ,
                                "num_vertices": num_vertices},
                    confidence=0.3,
                    contour=contour,
                    points=points
                )

    def _check_line(self, points, contour):
        """
        Check if the drawn stroke is a straight line.

        Uses the ratio of contour arc length to the distance between
        endpoints. A perfect line has a ratio near 1.0.

        Args:
            points: List of (x, y) tuples.
            contour: OpenCV contour.

        Returns:
            ShapeResult or None if not a line.
        """
        if len(points) < 2:
            return None

        # Distance between first and last point
        endpoint_dist = distance(points[0], points[-1])
        if endpoint_dist < 20:
            return None  # Endpoints are too close — likely a closed shape

        # Calculate total path length
        path_length = 0
        for i in range(1, len(points)):
            path_length += distance(points[i - 1], points[i])

        if path_length == 0:
            return None

        straightness = endpoint_dist / path_length

        if straightness > (1.0 - self.line_threshold):
            mid = centroid(points)
            return ShapeResult(
                shape_type="line",
                vertices=[points[0], points[-1]],
                center=mid,
                dimensions={"length": endpoint_dist,
                            "straightness": straightness},
                confidence=straightness,
                contour=contour,
                points=points
            )

        return None
