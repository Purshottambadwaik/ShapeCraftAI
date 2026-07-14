"""
AirSketch AI - File Manager
Handles saving drawings and images to disk.
"""

import os
import cv2
from datetime import datetime
from config import OUTPUT_IMAGE_DIR, OUTPUT_VIDEO_DIR, IMAGE_FORMAT


class FileManager:
    """
    Manages saving images and creating output directories.
    """

    def __init__(self, image_dir=OUTPUT_IMAGE_DIR, video_dir=OUTPUT_VIDEO_DIR):
        """
        Initialize FileManager and ensure output directories exist.

        Args:
            image_dir: Path to save images.
            video_dir: Path to save videos.
        """
        self.image_dir = image_dir
        self.video_dir = video_dir
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create output directories if they don't exist."""
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)

    def _generate_filename(self, prefix="airsketch", ext=IMAGE_FORMAT):
        """
        Generate a timestamped filename.

        Args:
            prefix: Filename prefix.
            ext: File extension.

        Returns:
            str: Generated filename like 'airsketch_20240714_142530.png'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}{ext}"

    def save_image(self, image, filename=None):
        """
        Save an image to the output directory.

        Args:
            image: NumPy array (BGR image).
            filename: Optional custom filename. Auto-generated if None.

        Returns:
            str: Full path to the saved file, or None on failure.
        """
        if filename is None:
            filename = self._generate_filename()

        filepath = os.path.join(self.image_dir, filename)

        try:
            success = cv2.imwrite(filepath, image)
            if success:
                print(f"[FileManager] Saved: {filepath}")
                return filepath
            else:
                print(f"[FileManager] Failed to save: {filepath}")
                return None
        except Exception as e:
            print(f"[FileManager] Error saving image: {e}")
            return None

    def save_canvas(self, canvas, frame=None, filename=None):
        """
        Save the canvas overlay, optionally merged with a frame.

        Args:
            canvas: The drawing canvas (NumPy array).
            frame: Optional video frame to merge with canvas.
            filename: Optional custom filename.

        Returns:
            str: Full path to the saved file, or None on failure.
        """
        if frame is not None:
            # Merge canvas with frame
            merged = cv2.addWeighted(frame, 1, canvas, 1, 0)
            return self.save_image(merged, filename)
        else:
            return self.save_image(canvas, filename)

    def get_saved_images(self):
        """
        List all saved images in the output directory.

        Returns:
            list: List of file paths.
        """
        if not os.path.exists(self.image_dir):
            return []
        files = [
            os.path.join(self.image_dir, f)
            for f in os.listdir(self.image_dir)
            if f.endswith(IMAGE_FORMAT) or f.endswith('.jpg')
        ]
        return sorted(files)
