"""
AirSketch AI - Helper Utilities
Generic helper functions used across the project.
"""

import math


def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def map_range(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    if in_max == in_min:
        return out_min
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def distance(p1, p2):
    """Calculate Euclidean distance between two points (x, y)."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def midpoint(p1, p2):
    """Calculate the midpoint between two points."""
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)


def lerp(a, b, t):
    """Linear interpolation between a and b by factor t (0-1)."""
    return a + (b - a) * t


def normalize_angle(angle):
    """Normalize angle to range [0, 360)."""
    return angle % 360
