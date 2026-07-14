"""
AirSketch AI - Configuration
All project-wide constants and settings.
"""

# =============================================================================
# Camera Settings
# =============================================================================
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# =============================================================================
# MediaPipe Settings
# =============================================================================
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7

# =============================================================================
# Drawing Settings
# =============================================================================
DEFAULT_BRUSH_SIZE = 4
MIN_BRUSH_SIZE = 1
MAX_BRUSH_SIZE = 20
BRUSH_SIZE_STEP = 1

# Smoothing factor for exponential moving average (0 = no smoothing, 1 = max lag)
SMOOTHING_FACTOR = 0.4

# Moving average window size
MOVING_AVG_WINDOW = 5

# Minimum points required to attempt shape detection
MIN_POINTS_FOR_SHAPE = 15

# =============================================================================
# Shape Detection Settings
# =============================================================================
# Epsilon factor for cv2.approxPolyDP (fraction of arc length)
APPROX_POLY_EPSILON = 0.03

# Circularity threshold (1.0 = perfect circle)
CIRCULARITY_THRESHOLD = 0.7

# Minimum contour area to consider as a valid shape
MIN_CONTOUR_AREA = 800

# Aspect ratio tolerance for square detection (1.0 = perfect square)
SQUARE_ASPECT_RATIO_TOLERANCE = 0.25

# Straightness threshold for line detection
LINE_STRAIGHTNESS_THRESHOLD = 0.05

# =============================================================================
# Gesture Thresholds
# =============================================================================
# Finger tip must be this much above PIP joint to be considered "up"
FINGER_UP_THRESHOLD = 0.0  # 0 means tip.y < pip.y is enough

# Minimum distance between points to register a new drawing point
MIN_DRAW_DISTANCE = 3

# =============================================================================
# UI Settings
# =============================================================================
TOOLBAR_HEIGHT = 80
TOOLBAR_PADDING = 10
BUTTON_SIZE = 50
BUTTON_SPACING = 10
BUTTON_BORDER_RADIUS = 8

# =============================================================================
# Colors (BGR format for OpenCV)
# =============================================================================
# UI Colors
COLOR_TOOLBAR_BG = (40, 40, 40)
COLOR_TOOLBAR_BORDER = (80, 80, 80)
COLOR_BUTTON_BG = (60, 60, 60)
COLOR_BUTTON_HOVER = (90, 90, 90)
COLOR_BUTTON_ACTIVE = (120, 80, 255)
COLOR_BUTTON_TEXT = (220, 220, 220)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)

# Drawing Palette (BGR)
COLOR_CYAN = (255, 255, 0)
COLOR_MAGENTA = (255, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_ORANGE = (0, 165, 255)
COLOR_PINK = (180, 105, 255)
COLOR_PURPLE = (200, 50, 150)
COLOR_LIME = (0, 255, 128)

# Default drawing color
DEFAULT_DRAW_COLOR = COLOR_CYAN

# Shape label color
COLOR_SHAPE_LABEL = (255, 255, 255)

# Indicator colors
COLOR_DRAWING_INDICATOR = (0, 255, 0)
COLOR_STOP_INDICATOR = (0, 0, 255)
COLOR_ERASE_INDICATOR = (0, 165, 255)
COLOR_SELECT_INDICATOR = (255, 255, 0)

# =============================================================================
# Drawing Color Palette (list for toolbar)
# =============================================================================
PALETTE_COLORS = [
    COLOR_CYAN,
    COLOR_MAGENTA,
    COLOR_YELLOW,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_PINK,
    COLOR_PURPLE,
    COLOR_LIME,
    COLOR_WHITE,
]

# =============================================================================
# History Settings
# =============================================================================
MAX_UNDO_STEPS = 30

# =============================================================================
# File Output Settings
# =============================================================================
OUTPUT_IMAGE_DIR = "outputs/images"
OUTPUT_VIDEO_DIR = "outputs/videos"
IMAGE_FORMAT = ".png"

# =============================================================================
# Font Settings
# =============================================================================
FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_SMALL = 0.5
FONT_SCALE_MEDIUM = 0.7
FONT_SCALE_LARGE = 1.0
FONT_THICKNESS = 2

# =============================================================================
# FPS Settings
# =============================================================================
FPS_AVG_FRAMES = 30
