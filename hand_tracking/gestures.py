"""
AirSketch AI - Gesture Detection
Detects specific hand gestures (draw, stop, erase, select) from landmarks.

Works with the new MediaPipe Tasks API landmark format
(list of NormalizedLandmark objects with .x, .y, .z).
"""

from hand_tracking.landmarks import LandmarkID, FINGER_TIPS, FINGER_PIPS


class GestureDetector:
    """
    Detects hand gestures by analyzing which fingers are raised or folded.
    """

    @staticmethod
    def detect_fingers_up(hand_landmarks):
        """
        Determine which fingers are raised (extended).

        Uses the tip-vs-PIP heuristic:
        - For index, middle, ring, pinky: tip.y < pip.y means finger is up.
        - For thumb: tip.x relative to IP.x (accounts for left/right hand).

        Args:
            hand_landmarks: List of NormalizedLandmark from HandLandmarker.

        Returns:
            list: [thumb, index, middle, ring, pinky] — True if up, False if down.
        """
        fingers = []

        # Thumb: compare tip.x with IP.x
        thumb_tip = hand_landmarks[LandmarkID.THUMB_TIP]
        thumb_ip = hand_landmarks[LandmarkID.THUMB_IP]

        # Use wrist and middle MCP to determine hand orientation
        wrist = hand_landmarks[LandmarkID.WRIST]
        middle_mcp = hand_landmarks[LandmarkID.MIDDLE_MCP]

        # Determine if it's a right or left hand based on wrist-middle MCP direction
        if wrist.x < middle_mcp.x:
            # Right hand orientation
            fingers.append(thumb_tip.x > thumb_ip.x)
        else:
            # Left hand orientation
            fingers.append(thumb_tip.x < thumb_ip.x)

        # Index, Middle, Ring, Pinky: tip above PIP means finger is up
        for tip_id, pip_id in zip(FINGER_TIPS, FINGER_PIPS):
            tip = hand_landmarks[tip_id]
            pip = hand_landmarks[pip_id]
            fingers.append(tip.y < pip.y)

        return fingers

    @staticmethod
    def is_drawing_gesture(fingers):
        """
        Check if the gesture is 'draw' — only index finger raised.

        Args:
            fingers: List of 5 booleans [thumb, index, middle, ring, pinky].

        Returns:
            bool: True if in drawing mode.
        """
        # Index up, middle/ring/pinky down
        return (fingers[1] and
                not fingers[2] and
                not fingers[3] and
                not fingers[4])

    @staticmethod
    def is_stop_gesture(fingers):
        """
        Check if the gesture is 'stop' — closed fist (all fingers down).
        Triggers shape detection on the current stroke.

        Args:
            fingers: List of 5 booleans.

        Returns:
            bool: True if fist is closed.
        """
        return not any(fingers)

    @staticmethod
    def is_erase_gesture(fingers):
        """
        Check if the gesture is 'erase/navigate' — index + middle raised.

        Args:
            fingers: List of 5 booleans.

        Returns:
            bool: True if in erase/navigate mode.
        """
        return (fingers[1] and
                fingers[2] and
                not fingers[3] and
                not fingers[4])

    @staticmethod
    def is_select_gesture(fingers):
        """
        Check if the gesture is 'select' — all fingers open (open palm).
        Used for toolbar interaction.

        Args:
            fingers: List of 5 booleans.

        Returns:
            bool: True if palm is open.
        """
        # At least 4 fingers must be up (thumb detection can be unreliable)
        return sum(fingers) >= 4

    @staticmethod
    def get_gesture_name(fingers):
        """
        Get a human-readable name for the current gesture.

        Args:
            fingers: List of 5 booleans.

        Returns:
            str: Gesture name.
        """
        if GestureDetector.is_drawing_gesture(fingers):
            return "DRAW"
        elif GestureDetector.is_stop_gesture(fingers):
            return "STOP"
        elif GestureDetector.is_erase_gesture(fingers):
            return "ERASE"
        elif GestureDetector.is_select_gesture(fingers):
            return "SELECT"
        else:
            return "IDLE"
