"""
AirSketch AI - Smart Shape Recognition using Hand Gestures
===========================================================

Main entry point. Runs the webcam loop, detects hand gestures,
draws on a virtual canvas, recognizes shapes, and corrects them
to perfect geometry.

Controls:
    ☝️  Index finger only     → DRAW mode (trace path on canvas)
    ✌️  Index + Middle up     → ERASE / Navigate toolbar
    ✊  Closed fist            → STOP drawing → triggers shape detection
    🖐️  Open palm (4+ fingers) → SELECT mode (interact with toolbar)

Keyboard:
    q  → Quit
    c  → Clear canvas
    u  → Undo last shape
    s  → Save current drawing
    +  → Increase brush size
    -  → Decrease brush size
"""

import sys
import os
import cv2
import numpy as np

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    TOOLBAR_HEIGHT, MIN_DRAW_DISTANCE, MIN_POINTS_FOR_SHAPE
)
from hand_tracking.detector import HandDetector
from hand_tracking.landmarks import LandmarkHelper
from hand_tracking.gestures import GestureDetector
from drawing.canvas import Canvas
from drawing.brush import Brush
from drawing.smoother import PointSmoother
from drawing.history import History
from shapes.detector import ShapeDetector, ShapeResult
from shapes.corrector import ShapeCorrector
from shapes.renderer import ShapeRenderer
from ui.toolbar import Toolbar
from ui.labels import Label
from utils.fps import FPSCounter
from utils.file_manager import FileManager
from utils.helpers import distance


def main():
    """Main application loop."""

    # =========================================================================
    # Initialize Components
    # =========================================================================
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # DirectShow for Windows
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    if not cap.isOpened():
        print("[AirSketch] ERROR: Could not open camera.")
        return

    # Get actual frame dimensions (may differ from requested)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[AirSketch] Camera: {actual_width}x{actual_height}")

    # Create the window BEFORE the loop so it's always visible
    window_name = "AirSketch AI"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 720)
    cv2.moveWindow(window_name, 100, 50)  # Position at top-left area
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)  # Always on top

    # Core components
    hand_detector = HandDetector()
    gesture_detector = GestureDetector()
    landmark_helper = LandmarkHelper()
    canvas = Canvas(width=actual_width, height=actual_height)
    brush = Brush()
    smoother = PointSmoother()
    history = History()
    shape_detector = ShapeDetector()
    file_manager = FileManager()
    fps_counter = FPSCounter()

    # UI components
    toolbar = Toolbar(frame_width=actual_width)

    # =========================================================================
    # State Variables
    # =========================================================================
    current_stroke = []          # Points of the current drawing stroke
    is_drawing = False           # Whether we're actively drawing
    prev_point = None            # Previous drawing point (for lines)
    last_gesture = "IDLE"        # Previous frame's gesture
    detected_shape_name = ""     # Name of last detected shape
    notification_text = ""       # Notification message to display
    notification_timer = 0       # Frames remaining for notification

    # Store completed shapes for rendering labels
    completed_shapes = []        # List of (corrected_data, color) tuples

    print("[AirSketch] Starting... Press 'q' to quit.")
    print("[AirSketch] Gestures: Index=Draw, Fist=Stop/Detect, "
          "Two fingers=Erase, Open palm=Select")

    # =========================================================================
    # Main Loop
    # =========================================================================
    while True:
        success, frame = cap.read()
        if not success:
            print("[AirSketch] Failed to grab frame.")
            break

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        fps_counter.update()

        # ----- Hand Detection -----
        frame, hands_found = hand_detector.find_hands(frame, draw=True)

        current_gesture = "IDLE"

        if hands_found:
            hand_landmarks = hand_detector.get_hand_landmarks()
            if hand_landmarks:
                # Get landmark positions
                lm_list = landmark_helper.get_landmark_list(
                    hand_landmarks, actual_width, actual_height
                )
                index_pos = landmark_helper.get_index_finger_tip(
                    hand_landmarks, actual_width, actual_height
                )

                # Detect gesture
                fingers = gesture_detector.detect_fingers_up(hand_landmarks)
                current_gesture = gesture_detector.get_gesture_name(fingers)

                ix, iy = index_pos

                # Draw finger tip indicator
                tip_color = {
                    "DRAW": (0, 255, 0),
                    "ERASE": (0, 165, 255),
                    "SELECT": (255, 255, 0),
                    "STOP": (0, 0, 255),
                }.get(current_gesture, (128, 128, 128))
                cv2.circle(frame, (ix, iy), 10, tip_color, -1)
                cv2.circle(frame, (ix, iy), 12, (255, 255, 255), 1)

                # ===== DRAW MODE =====
                if current_gesture == "DRAW":
                    # Don't draw in toolbar area
                    if not toolbar.is_in_toolbar(iy):
                        # Smooth the point
                        sx, sy = smoother.smooth(ix, iy)

                        if not is_drawing:
                            # Start new stroke
                            is_drawing = True
                            current_stroke = [(sx, sy)]
                            prev_point = (sx, sy)
                            # Save canvas state before drawing for undo
                            history.push(canvas.get_snapshot())
                        else:
                            # Continue stroke — draw line from prev to current
                            if prev_point is not None:
                                dist = distance(prev_point, (sx, sy))
                                if dist > MIN_DRAW_DISTANCE:
                                    canvas.draw_line(
                                        prev_point, (sx, sy),
                                        brush.get_draw_color(),
                                        brush.get_draw_size()
                                    )
                                    current_stroke.append((sx, sy))
                                    prev_point = (sx, sy)

                # ===== STOP / FIST — Detect Shape =====
                elif current_gesture == "STOP":
                    if is_drawing and len(current_stroke) >= MIN_POINTS_FOR_SHAPE:
                        # Commit the current temp stroke
                        canvas.commit_stroke()

                        # Detect shape from stroke points
                        shape_result = shape_detector.detect(current_stroke)
                        detected_shape_name = shape_result.shape_type

                        if shape_result.shape_type != "unknown":
                            # Correct shape to perfect geometry
                            corrected = ShapeCorrector.correct(shape_result)

                            # Erase the rough stroke
                            ShapeRenderer.erase_stroke(
                                canvas.surface, current_stroke,
                                thickness=brush.get_draw_size() + 10
                            )

                            # Draw perfect shape
                            draw_color = brush.get_draw_color()
                            ShapeRenderer.draw_shape(
                                canvas.surface, corrected,
                                draw_color, brush.get_draw_size()
                            )

                            # Draw label
                            ShapeRenderer.draw_label(canvas.surface, corrected)

                            # Store for persistent labels
                            completed_shapes.append((corrected, draw_color))

                            notification_text = (
                                f"{shape_result.shape_type.capitalize()} detected!"
                            )
                            notification_timer = 45

                            print(f"[AirSketch] {shape_result}")
                        else:
                            # Unknown shape — keep the raw drawing
                            notification_text = "Shape not recognized"
                            notification_timer = 30

                        # Reset stroke
                        is_drawing = False
                        current_stroke = []
                        prev_point = None
                        smoother.reset()

                    elif is_drawing:
                        # Too few points — commit as raw drawing
                        canvas.commit_stroke()
                        is_drawing = False
                        current_stroke = []
                        prev_point = None
                        smoother.reset()

                # ===== SELECT MODE — Toolbar Interaction =====
                elif current_gesture == "SELECT":
                    if is_drawing:
                        # Stop drawing if we were
                        canvas.commit_stroke()
                        is_drawing = False
                        current_stroke = []
                        prev_point = None
                        smoother.reset()

                    # Update toolbar hover
                    toolbar.update_hover(ix, iy)

                    # Check for toolbar click (finger in toolbar area)
                    if toolbar.is_in_toolbar(iy):
                        action, data = toolbar.handle_click(ix, iy)

                        if action == "set_color":
                            brush.set_color(data)
                            notification_text = "Color changed"
                            notification_timer = 20

                        elif action == "brush_increase":
                            brush.increase_size()
                            notification_text = f"Brush: {brush.size}"
                            notification_timer = 20

                        elif action == "brush_decrease":
                            brush.decrease_size()
                            notification_text = f"Brush: {brush.size}"
                            notification_timer = 20

                        elif action == "clear":
                            history.push(canvas.get_snapshot())
                            canvas.clear()
                            completed_shapes = []
                            notification_text = "Canvas cleared"
                            notification_timer = 30

                        elif action == "undo":
                            snapshot = history.undo()
                            if snapshot is not None:
                                canvas.restore_snapshot(snapshot)
                                # Remove last completed shape
                                if completed_shapes:
                                    completed_shapes.pop()
                                notification_text = "Undo"
                                notification_timer = 20
                            else:
                                notification_text = "Nothing to undo"
                                notification_timer = 20

                        elif action == "save":
                            merged = canvas.merge_with_frame(frame)
                            path = file_manager.save_image(merged)
                            if path:
                                notification_text = "Saved!"
                                notification_timer = 45
                            else:
                                notification_text = "Save failed"
                                notification_timer = 30

                # ===== ERASE MODE =====
                elif current_gesture == "ERASE":
                    if is_drawing:
                        canvas.commit_stroke()
                        is_drawing = False
                        current_stroke = []
                        prev_point = None
                        smoother.reset()

                    # Erase at finger position
                    if not toolbar.is_in_toolbar(iy):
                        cv2.circle(
                            canvas.surface, (ix, iy), 20, (0, 0, 0), -1
                        )

                # ===== IDLE =====
                else:
                    if is_drawing:
                        # Commit stroke if transitioning from draw
                        canvas.commit_stroke()
                        is_drawing = False
                        current_stroke = []
                        prev_point = None
                        smoother.reset()

        else:
            # No hand detected
            if is_drawing:
                canvas.commit_stroke()
                is_drawing = False
                current_stroke = []
                prev_point = None
                smoother.reset()

        last_gesture = current_gesture

        # ----- Merge Canvas with Frame -----
        frame = canvas.merge_with_frame(frame)

        # ----- Draw UI -----
        toolbar.draw(frame, brush_size=brush.size)

        # Draw status labels (below toolbar)
        label_y_start = TOOLBAR_HEIGHT + 25
        Label.draw_fps(frame, fps_counter.get_fps_text(),
                       position=(10, label_y_start))
        Label.draw_mode(frame, current_gesture,
                        position=(10, label_y_start + 25))

        if detected_shape_name and detected_shape_name != "unknown":
            Label.draw_shape_info(frame, detected_shape_name,
                                  position=(10, label_y_start + 50))

        Label.draw_undo_count(frame, history.get_depth())

        # Draw notification
        if notification_timer > 0:
            Label.draw_notification(frame, notification_text)
            notification_timer -= 1

        # Draw brush preview circle
        if current_gesture == "DRAW" and hands_found:
            cv2.circle(frame, index_pos, brush.get_draw_size(),
                       brush.get_draw_color(), 1)

        # ----- Show Frame -----
        cv2.imshow(window_name, frame)

        # ----- Handle Keyboard -----
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('c'):
            history.push(canvas.get_snapshot())
            canvas.clear()
            completed_shapes = []
            notification_text = "Canvas cleared"
            notification_timer = 30
        elif key == ord('u'):
            snapshot = history.undo()
            if snapshot is not None:
                canvas.restore_snapshot(snapshot)
                if completed_shapes:
                    completed_shapes.pop()
                notification_text = "Undo"
                notification_timer = 20
        elif key == ord('s'):
            merged = canvas.merge_with_frame(frame)
            path = file_manager.save_image(merged)
            if path:
                notification_text = "Saved!"
                notification_timer = 45
        elif key == ord('+') or key == ord('='):
            brush.increase_size()
        elif key == ord('-'):
            brush.decrease_size()

    # =========================================================================
    # Cleanup
    # =========================================================================
    hand_detector.release()
    cap.release()
    cv2.destroyAllWindows()
    print("[AirSketch] Goodbye!")


if __name__ == "__main__":
    main()
