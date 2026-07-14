"""
AirSketch AI - Landmark Helper
Extracts and processes hand landmark positions from MediaPipe HandLandmarker results.

The new Tasks API returns landmarks as a list of NormalizedLandmark objects,
accessed by index (e.g., landmarks[8] for INDEX_TIP).
Each NormalizedLandmark has .x, .y, .z (all normalized 0-1).
"""


# MediaPipe hand landmark indices
class LandmarkID:
    """MediaPipe hand landmark index constants."""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


# Finger tip and PIP landmark IDs for finger-up detection
FINGER_TIPS = [
    LandmarkID.INDEX_TIP,
    LandmarkID.MIDDLE_TIP,
    LandmarkID.RING_TIP,
    LandmarkID.PINKY_TIP,
]

FINGER_PIPS = [
    LandmarkID.INDEX_PIP,
    LandmarkID.MIDDLE_PIP,
    LandmarkID.RING_PIP,
    LandmarkID.PINKY_PIP,
]


class LandmarkHelper:
    """
    Helper class for extracting useful information from hand landmarks.
    Works with the new MediaPipe Tasks API landmark format
    (list of NormalizedLandmark objects).
    """

    @staticmethod
    def get_landmark_list(hand_landmarks, frame_width, frame_height):
        """
        Convert landmarks to a list of (id, x, y) pixel coordinates.

        Args:
            hand_landmarks: List of NormalizedLandmark from HandLandmarker.
            frame_width: Width of the video frame in pixels.
            frame_height: Height of the video frame in pixels.

        Returns:
            list: List of tuples (landmark_id, pixel_x, pixel_y).
        """
        landmark_list = []
        for idx, lm in enumerate(hand_landmarks):
            px = int(lm.x * frame_width)
            py = int(lm.y * frame_height)
            landmark_list.append((idx, px, py))
        return landmark_list

    @staticmethod
    def get_finger_tip(hand_landmarks, finger_tip_id, frame_width, frame_height):
        """
        Get the pixel position of a specific finger tip.

        Args:
            hand_landmarks: List of NormalizedLandmark.
            finger_tip_id: Landmark ID of the finger tip.
            frame_width: Width of the video frame.
            frame_height: Height of the video frame.

        Returns:
            tuple: (x, y) pixel position.
        """
        lm = hand_landmarks[finger_tip_id]
        return (int(lm.x * frame_width), int(lm.y * frame_height))

    @staticmethod
    def get_index_finger_tip(hand_landmarks, frame_width, frame_height):
        """
        Convenience method to get the index finger tip position.

        Args:
            hand_landmarks: List of NormalizedLandmark.
            frame_width: Width of the video frame.
            frame_height: Height of the video frame.

        Returns:
            tuple: (x, y) pixel position of index finger tip.
        """
        return LandmarkHelper.get_finger_tip(
            hand_landmarks, LandmarkID.INDEX_TIP,
            frame_width, frame_height
        )

    @staticmethod
    def get_finger_positions(hand_landmarks, frame_width, frame_height):
        """
        Get positions of all five finger tips.

        Args:
            hand_landmarks: List of NormalizedLandmark.
            frame_width: Width of the video frame.
            frame_height: Height of the video frame.

        Returns:
            dict: Mapping of finger name to (x, y) position.
        """
        tips = {
            "thumb": LandmarkID.THUMB_TIP,
            "index": LandmarkID.INDEX_TIP,
            "middle": LandmarkID.MIDDLE_TIP,
            "ring": LandmarkID.RING_TIP,
            "pinky": LandmarkID.PINKY_TIP,
        }
        positions = {}
        for name, tip_id in tips.items():
            lm = hand_landmarks[tip_id]
            positions[name] = (int(lm.x * frame_width), int(lm.y * frame_height))
        return positions
