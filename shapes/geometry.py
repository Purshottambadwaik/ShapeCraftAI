"""
AirSketch AI - Geometry Helpers
Pure geometry utility functions for shape analysis.
"""

import math
import cv2
import numpy as np


def distance(p1, p2):
    """
    Euclidean distance between two points.

    Args:
        p1, p2: Points as (x, y) tuples.

    Returns:
        float: Distance.
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def angle_between(p1, p2, p3):
    """
    Calculate the angle at p2 formed by the line segments p1-p2 and p2-p3.

    Args:
        p1, p2, p3: Points as (x, y) tuples.

    Returns:
        float: Angle in degrees.
    """
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_angle))


def is_convex(points):
    """
    Check if a polygon defined by points is convex.

    Args:
        points: List of (x, y) tuples defining the polygon.

    Returns:
        bool: True if convex.
    """
    contour = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    return cv2.isContourConvex(contour)


def polygon_area(points):
    """
    Calculate the area of a polygon using the Shoelace formula.

    Args:
        points: List of (x, y) tuples.

    Returns:
        float: Area of the polygon.
    """
    n = len(points)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0


def circularity(contour):
    """
    Calculate the circularity of a contour.
    Perfect circle = 1.0, irregular shapes < 1.0.

    Formula: 4π × area / perimeter²

    Args:
        contour: OpenCV contour (np.array).

    Returns:
        float: Circularity score (0 to 1).
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if perimeter == 0:
        return 0.0

    return (4 * math.pi * area) / (perimeter ** 2)


def aspect_ratio(rect_points):
    """
    Calculate the aspect ratio of a rectangle defined by 4 points.

    Args:
        rect_points: List of 4 (x, y) tuples.

    Returns:
        float: Aspect ratio (width / height), always >= 1.0.
    """
    if len(rect_points) < 4:
        return 0.0

    # Calculate side lengths
    side1 = distance(rect_points[0], rect_points[1])
    side2 = distance(rect_points[1], rect_points[2])

    if side1 == 0 or side2 == 0:
        return 0.0

    ratio = max(side1, side2) / min(side1, side2)
    return ratio


def bounding_box(points):
    """
    Calculate the axis-aligned bounding box of a set of points.

    Args:
        points: List of (x, y) tuples.

    Returns:
        tuple: (x, y, w, h) of the bounding box.
    """
    if not points:
        return (0, 0, 0, 0)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    x_min = min(xs)
    y_min = min(ys)
    x_max = max(xs)
    y_max = max(ys)

    return (x_min, y_min, x_max - x_min, y_max - y_min)


def centroid(points):
    """
    Calculate the centroid (center of mass) of a set of points.

    Args:
        points: List of (x, y) tuples.

    Returns:
        tuple: (cx, cy) centroid coordinates.
    """
    if not points:
        return (0, 0)

    cx = sum(p[0] for p in points) // len(points)
    cy = sum(p[1] for p in points) // len(points)
    return (cx, cy)


def points_to_contour(points):
    """
    Convert a list of (x, y) points to an OpenCV contour format.

    Args:
        points: List of (x, y) tuples.

    Returns:
        np.array: Contour in OpenCV format.
    """
    return np.array(points, dtype=np.int32).reshape(-1, 1, 2)
