import os
import sys
import threading
import cv2
import numpy as np
import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MIN_DRAW_DISTANCE, MIN_POINTS_FOR_SHAPE,
    CAMERA_WIDTH, CAMERA_HEIGHT
)
from hand_tracking.detector import HandDetector
from hand_tracking.landmarks import LandmarkHelper
from hand_tracking.gestures import GestureDetector
from drawing.canvas import Canvas
from drawing.brush import Brush
from drawing.smoother import PointSmoother
from drawing.history import History
from shapes.detector import ShapeDetector
from shapes.corrector import ShapeCorrector
from shapes.renderer import ShapeRenderer
from ui.labels import Label
from utils.fps import FPSCounter
from utils.helpers import distance

# Color mapping for UI to BGR
COLOR_MAP = {
    "Cyan": (255, 255, 0),
    "Magenta": (255, 0, 255),
    "Yellow": (0, 255, 255),
    "Red": (0, 0, 255),
    "Green": (0, 255, 0),
    "Blue": (255, 0, 0),
    "Orange": (0, 165, 255),
    "Pink": (180, 105, 255),
    "Purple": (200, 50, 150),
    "Lime": (0, 255, 128),
    "White": (255, 255, 255),
}

class VideoProcessor:
    def __init__(self):
        self.hand_detector = HandDetector()
        self.gesture_detector = GestureDetector()
        self.landmark_helper = LandmarkHelper()
        self.canvas = None
        self.brush = Brush()
        self.smoother = PointSmoother()
        self.history = History()
        self.shape_detector = ShapeDetector()
        self.fps_counter = FPSCounter()

        # State Variables
        self.current_stroke = []
        self.is_drawing = False
        self.prev_point = None
        self.last_gesture = "IDLE"
        self.completed_shapes = []
        self.notification_text = ""
        self.notification_timer = 0
        self.detected_shape_name = ""

        # UI parameters
        self.brush_color_bgr = (255, 255, 0) # default Cyan
        self.brush_size = 4
        
        # Flags
        self.clear_requested = False
        self.undo_requested = False
        
        self.lock = threading.Lock()

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        
        # Mirror image for natural user experience
        img = cv2.flip(img, 1)
        h, w = img.shape[:2]
        
        with self.lock:
            # Lazy init canvas matching camera capture dimensions
            if self.canvas is None:
                self.canvas = Canvas(width=w, height=h)
                
            self.brush.set_draw_color(self.brush_color_bgr)
            self.brush.set_draw_size(self.brush_size)
            
            # Process UI command flags
            if self.clear_requested:
                self.history.push(self.canvas.get_snapshot())
                self.canvas.clear()
                self.completed_shapes = []
                self.notification_text = "Canvas cleared"
                self.notification_timer = 30
                self.clear_requested = False
                
            if self.undo_requested:
                snapshot = self.history.undo()
                if snapshot is not None:
                    self.canvas.restore_snapshot(snapshot)
                    if self.completed_shapes:
                        self.completed_shapes.pop()
                    self.notification_text = "Undo"
                    self.notification_timer = 20
                else:
                    self.notification_text = "Nothing to undo"
                    self.notification_timer = 20
                self.undo_requested = False

        self.fps_counter.update()

        # ----- Hand Detection -----
        img, hands_found = self.hand_detector.find_hands(img, draw=True)
        current_gesture = "IDLE"

        if hands_found:
            hand_landmarks = self.hand_detector.get_hand_landmarks()
            if hand_landmarks:
                # Extract coordinates
                index_pos = self.landmark_helper.get_index_finger_tip(
                    hand_landmarks, w, h
                )
                fingers = self.gesture_detector.detect_fingers_up(hand_landmarks)
                current_gesture = self.gesture_detector.get_gesture_name(fingers)
                
                ix, iy = index_pos

                # Draw finger tip indicator
                tip_color = {
                    "DRAW": (0, 255, 0),
                    "ERASE": (0, 165, 255),
                    "SELECT": (255, 255, 0),
                    "STOP": (0, 0, 255),
                }.get(current_gesture, (128, 128, 128))
                cv2.circle(img, (ix, iy), 10, tip_color, -1)
                cv2.circle(img, (ix, iy), 12, (255, 255, 255), 1)

                # ===== DRAW MODE =====
                if current_gesture == "DRAW":
                    sx, sy = self.smoother.smooth(ix, iy)

                    if not self.is_drawing:
                        self.is_drawing = True
                        self.current_stroke = [(sx, sy)]
                        self.prev_point = (sx, sy)
                        self.history.push(self.canvas.get_snapshot())
                    else:
                        if self.prev_point is not None:
                            dist = distance(self.prev_point, (sx, sy))
                            if dist > MIN_DRAW_DISTANCE:
                                self.canvas.draw_line(
                                    self.prev_point, (sx, sy),
                                    self.brush.get_draw_color(),
                                    self.brush.get_draw_size()
                                )
                                self.current_stroke.append((sx, sy))
                                self.prev_point = (sx, sy)

                # ===== STOP / FIST — Detect Shape =====
                elif current_gesture == "STOP":
                    if self.is_drawing and len(self.current_stroke) >= MIN_POINTS_FOR_SHAPE:
                        self.canvas.commit_stroke()
                        shape_result = self.shape_detector.detect(self.current_stroke)
                        self.detected_shape_name = shape_result.shape_type
                        
                        if shape_result.shape_type != "unknown":
                            corrected = ShapeCorrector.correct(shape_result)
                            ShapeRenderer.erase_stroke(
                                self.canvas.surface, self.current_stroke,
                                thickness=self.brush.get_draw_size() + 10
                            )
                            draw_color = self.brush.get_draw_color()
                            ShapeRenderer.draw_shape(
                                self.canvas.surface, corrected,
                                draw_color, self.brush.get_draw_size()
                            )
                            ShapeRenderer.draw_label(self.canvas.surface, corrected)
                            self.completed_shapes.append((corrected, draw_color))
                            self.notification_text = f"{shape_result.shape_type.capitalize()} detected!"
                            self.notification_timer = 45
                        else:
                            self.notification_text = "Shape not recognized"
                            self.notification_timer = 30
                        
                        self.is_drawing = False
                        self.current_stroke = []
                        self.prev_point = None
                        self.smoother.reset()
                        
                    elif self.is_drawing:
                        self.canvas.commit_stroke()
                        self.is_drawing = False
                        self.current_stroke = []
                        self.prev_point = None
                        self.smoother.reset()

                # ===== ERASE MODE =====
                elif current_gesture == "ERASE":
                    if self.is_drawing:
                        self.canvas.commit_stroke()
                        self.is_drawing = False
                        self.current_stroke = []
                        self.prev_point = None
                        self.smoother.reset()

                    cv2.circle(self.canvas.surface, (ix, iy), 25, (0, 0, 0), -1)

                # ===== SELECT / PALM =====
                elif current_gesture == "SELECT":
                    if self.is_drawing:
                        self.canvas.commit_stroke()
                        self.is_drawing = False
                        self.current_stroke = []
                        self.prev_point = None
                        self.smoother.reset()

        else:
            # Handle user releasing hand abruptly
            if self.is_drawing:
                self.canvas.commit_stroke()
                self.is_drawing = False
                self.current_stroke = []
                self.prev_point = None
                self.smoother.reset()

        # Merge canvas drawing onto active frame
        if self.canvas is not None:
            img = self.canvas.merge_with_frame(img)

        # Draw Mode indicator on frame
        Label.draw_mode(img, current_gesture)
        
        # Draw FPS
        Label.draw_fps(img, f"FPS: {self.fps_counter.get_fps():.1f}")
        
        # Draw shape info
        Label.draw_shape_info(img, self.detected_shape_name)

        # Draw undo count
        Label.draw_undo_count(img, self.history.get_depth())

        # Render notifications
        if self.notification_timer > 0:
            Label.draw_notification(img, self.notification_text)
            self.notification_timer -= 1

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def main():
    st.set_page_config(page_title="ShapeCraft AI", layout="wide", page_icon="🎨")
    
    st.title("🎨 ShapeCraft AI (AirSketch AI Web)")
    st.write(
        "Draw shapes in the air with your index finger. "
        "Make a fist to recognize and correct it to perfect geometry!"
    )

    # Sidebar Controls
    st.sidebar.title("🎛️ Brush Controls")
    
    selected_color = st.sidebar.selectbox(
        "Select Brush Color",
        options=list(COLOR_MAP.keys()),
        index=0
    )
    brush_color_bgr = COLOR_MAP[selected_color]
    
    brush_size = st.sidebar.slider(
        "Brush Size",
        min_value=1,
        max_value=20,
        value=4,
        step=1
    )

    st.sidebar.markdown("---")
    st.sidebar.title("🛠️ Actions")
    
    clear_button = st.sidebar.button("🗑️ Clear Canvas", use_container_width=True)
    undo_button = st.sidebar.button("↩️ Undo Last", use_container_width=True)

    # WebRTC Streamer
    # Use standard STUN server to guarantee browser connectivity over various networks
    rtc_config = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    ctx = webrtc_streamer(
        key="airsketch-webrtc",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_config,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
    )

    # Sync Streamlit sidebar state to background worker thread
    if ctx.video_processor:
        with ctx.video_processor.lock:
            ctx.video_processor.brush_color_bgr = brush_color_bgr
            ctx.video_processor.brush_size = brush_size
            if clear_button:
                ctx.video_processor.clear_requested = True
            if undo_button:
                ctx.video_processor.undo_requested = True

    # Instructions Card
    st.markdown("### 🖐️ Gesture Instructions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("☝️ **DRAW**: Raise only index finger to paint.")
    with col2:
        st.error("✊ **STOP/DETECT**: Make a fist to finalize & snap to geometry.")
    with col3:
        st.warning("✌️ **ERASE**: Show index + middle finger to erase.")
    with col4:
        st.success("🖐️ **SELECT**: Show open palm to rest.")

if __name__ == "__main__":
    main()
