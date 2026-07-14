"""
AirSketch AI - Hand Detector
Wraps MediaPipe HandLandmarker (Tasks API) for hand detection and landmark extraction.
"""

import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker, HandLandmarkerOptions, RunningMode,
    HandLandmarksConnections, drawing_utils
)
from config import MAX_HANDS, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE

# Path to the hand landmarker model
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "hand_landmarker.task"
)


class HandDetector:
    """
    Detects hands in video frames using the MediaPipe HandLandmarker Tasks API.
    Returns annotated frames and raw landmark data.
    """

    def __init__(self, max_hands=MAX_HANDS,
                 detection_confidence=DETECTION_CONFIDENCE,
                 tracking_confidence=TRACKING_CONFIDENCE,
                 model_path=_MODEL_PATH):
        """
        Initialize the MediaPipe HandLandmarker.

        Args:
            max_hands: Maximum number of hands to detect.
            detection_confidence: Minimum confidence for hand detection.
            tracking_confidence: Minimum confidence for hand tracking.
            model_path: Path to the hand_landmarker.task model file.
        """
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.connections = HandLandmarksConnections.HAND_CONNECTIONS
        self.results = None
        self._frame_timestamp_ms = 0

    def find_hands(self, frame, draw=True):
        """
        Detect hands in the given frame.

        Args:
            frame: BGR image from webcam.
            draw: Whether to draw landmarks on the frame.

        Returns:
            frame: The frame (with or without drawn landmarks).
            bool: Whether any hands were detected.
        """
        # Convert BGR to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Detect with monotonically increasing timestamp
        self._frame_timestamp_ms += 33  # ~30 FPS
        self.results = self.landmarker.detect_for_video(
            mp_image, self._frame_timestamp_ms
        )

        if self.has_hands() and draw:
            self._draw_landmarks(frame)

        return frame, self.has_hands()

    def _draw_landmarks(self, frame):
        """
        Draw hand landmarks and connections on the frame.

        Args:
            frame: BGR image to draw on.
        """
        h, w = frame.shape[:2]

        for hand_landmarks in self.results.hand_landmarks:
            # Draw connections
            for connection in self.connections:
                start_lm = hand_landmarks[connection.start]
                end_lm = hand_landmarks[connection.end]

                start_pt = (int(start_lm.x * w), int(start_lm.y * h))
                end_pt = (int(end_lm.x * w), int(end_lm.y * h))

                cv2.line(frame, start_pt, end_pt, (0, 255, 0), 2)

            # Draw landmark points
            for lm in hand_landmarks:
                px = int(lm.x * w)
                py = int(lm.y * h)
                cv2.circle(frame, (px, py), 4, (255, 0, 128), -1)
                cv2.circle(frame, (px, py), 5, (255, 255, 255), 1)

    def has_hands(self):
        """Check if any hands were detected in the last frame."""
        return (self.results is not None and
                len(self.results.hand_landmarks) > 0)

    def get_hand_landmarks(self, hand_index=0):
        """
        Get raw landmarks for a specific hand.

        The returned object is a list of NormalizedLandmark with .x, .y, .z
        properties (all normalized 0-1). Access by index matching MediaPipe
        hand landmark IDs (0=WRIST, 4=THUMB_TIP, 8=INDEX_TIP, etc.).

        Args:
            hand_index: Which hand (0 = first detected).

        Returns:
            List of NormalizedLandmark, or None.
        """
        if not self.has_hands():
            return None
        hands_list = self.results.hand_landmarks
        if hand_index < len(hands_list):
            return hands_list[hand_index]
        return None

    def release(self):
        """Release MediaPipe resources."""
        self.landmarker.close()
