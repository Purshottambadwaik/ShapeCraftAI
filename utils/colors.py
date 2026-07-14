"""
AirSketch AI - Color Utilities
Predefined color palettes and color helper functions.
All colors are in BGR format (OpenCV standard).
"""


# =============================================================================
# Named Color Palettes
# =============================================================================

NEON = {
    "cyan": (255, 255, 0),
    "magenta": (255, 0, 255),
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
    "orange": (0, 165, 255),
    "pink": (180, 105, 255),
    "blue": (255, 50, 50),
    "purple": (200, 50, 150),
}

PASTEL = {
    "pink": (203, 192, 255),
    "blue": (250, 206, 135),
    "green": (170, 255, 195),
    "yellow": (185, 255, 255),
    "lavender": (250, 230, 230),
    "peach": (185, 218, 255),
    "mint": (200, 255, 220),
    "coral": (180, 180, 255),
}

CLASSIC = {
    "red": (0, 0, 255),
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "yellow": (0, 255, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "orange": (0, 165, 255),
    "purple": (128, 0, 128),
}


def bgr_to_rgb(bgr):
    """Convert BGR tuple to RGB tuple."""
    return (bgr[2], bgr[1], bgr[0])


def rgb_to_bgr(rgb):
    """Convert RGB tuple to BGR tuple."""
    return (rgb[2], rgb[1], rgb[0])


def hex_to_bgr(hex_color):
    """Convert hex color string (e.g., '#FF5733') to BGR tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)


def bgr_to_hex(bgr):
    """Convert BGR tuple to hex color string."""
    return '#{:02x}{:02x}{:02x}'.format(bgr[2], bgr[1], bgr[0])


def blend_colors(color1, color2, alpha=0.5):
    """
    Blend two BGR colors together.
    alpha=0 returns color1, alpha=1 returns color2.
    """
    return tuple(
        int(c1 * (1 - alpha) + c2 * alpha)
        for c1, c2 in zip(color1, color2)
    )


def darken(color, factor=0.7):
    """Darken a BGR color by a factor (0-1)."""
    return tuple(int(c * factor) for c in color)


def lighten(color, factor=0.3):
    """Lighten a BGR color by blending with white."""
    return blend_colors(color, (255, 255, 255), factor)
