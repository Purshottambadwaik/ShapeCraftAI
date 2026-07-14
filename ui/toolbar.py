"""
AirSketch AI - Toolbar
Horizontal toolbar at the top of the frame with color picker,
brush size controls, and action buttons.
"""

import cv2
from config import (
    TOOLBAR_HEIGHT, TOOLBAR_PADDING, BUTTON_SIZE, BUTTON_SPACING,
    COLOR_TOOLBAR_BG, COLOR_TOOLBAR_BORDER, PALETTE_COLORS,
    DEFAULT_DRAW_COLOR, FONT, FONT_SCALE_SMALL, COLOR_WHITE
)
from ui.buttons import Button


class Toolbar:
    """
    Renders a toolbar with color buttons, brush size controls,
    and action buttons (clear, undo, save).
    """

    def __init__(self, frame_width):
        """
        Initialize the toolbar and create all buttons.

        Args:
            frame_width: Width of the video frame.
        """
        self.frame_width = frame_width
        self.height = TOOLBAR_HEIGHT
        self.buttons = []
        self.active_color = DEFAULT_DRAW_COLOR
        self.active_color_index = 0

        self._create_buttons()

    def _create_buttons(self):
        """Create all toolbar buttons."""
        x_offset = TOOLBAR_PADDING
        y_offset = TOOLBAR_PADDING + 5
        btn_size = BUTTON_SIZE - 15  # Slightly smaller for color buttons

        # --- Color Palette Buttons ---
        for i, color in enumerate(PALETTE_COLORS):
            btn = Button(
                x=x_offset, y=y_offset,
                w=btn_size, h=btn_size,
                color=color,
                action=f"color_{i}",
                is_color_button=True
            )
            if i == 0:
                btn.is_active = True
            self.buttons.append(btn)
            x_offset += btn_size + 4

        x_offset += BUTTON_SPACING

        # --- Brush Size Buttons ---
        btn_w = 35
        btn_h = btn_size

        # Decrease size
        btn_minus = Button(
            x=x_offset, y=y_offset,
            w=btn_w, h=btn_h,
            label="-",
            action="brush_decrease"
        )
        self.buttons.append(btn_minus)
        x_offset += btn_w + 4

        # Increase size
        btn_plus = Button(
            x=x_offset, y=y_offset,
            w=btn_w, h=btn_h,
            label="+",
            action="brush_increase"
        )
        self.buttons.append(btn_plus)
        x_offset += btn_w + BUTTON_SPACING

        # --- Action Buttons (right-aligned) ---
        action_btn_w = 55
        actions = [
            ("Undo", "undo"),
            ("Clear", "clear"),
            ("Save", "save"),
        ]

        # Calculate right-aligned position
        total_action_width = len(actions) * (action_btn_w + 4)
        action_x = self.frame_width - total_action_width - TOOLBAR_PADDING

        for label, action in actions:
            btn = Button(
                x=action_x, y=y_offset,
                w=action_btn_w, h=btn_h,
                label=label,
                action=action
            )
            self.buttons.append(btn)
            action_x += action_btn_w + 4

    def draw(self, frame, brush_size=4):
        """
        Draw the toolbar on the frame.

        Args:
            frame: The OpenCV frame.
            brush_size: Current brush size (displayed between +/- buttons).
        """
        # Draw toolbar background
        cv2.rectangle(
            frame,
            (0, 0),
            (self.frame_width, self.height),
            COLOR_TOOLBAR_BG,
            -1
        )

        # Draw bottom border
        cv2.line(
            frame,
            (0, self.height),
            (self.frame_width, self.height),
            COLOR_TOOLBAR_BORDER,
            2
        )

        # Draw all buttons
        for btn in self.buttons:
            btn.draw(frame)

        # Draw brush size indicator between +/- buttons
        # Find the brush_decrease and brush_increase buttons
        for i, btn in enumerate(self.buttons):
            if btn.action == "brush_decrease":
                minus_btn = btn
            elif btn.action == "brush_increase":
                plus_btn = btn

        # Draw brush size text above the +/- buttons
        size_text = f"Size: {brush_size}"
        text_x = minus_btn.x
        text_y = self.height - 5
        cv2.putText(
            frame, size_text, (text_x, text_y),
            FONT, 0.35, COLOR_WHITE, 1, cv2.LINE_AA
        )

    def handle_click(self, x, y):
        """
        Check if a click hits any button and return the action.

        Args:
            x, y: Click coordinates.

        Returns:
            tuple: (action_name, action_data) or (None, None).
                   action_data is the color tuple for color buttons.
        """
        if y > self.height:
            return (None, None)

        for btn in self.buttons:
            if btn.contains(x, y):
                action = btn.action

                if action and action.startswith("color_"):
                    # Color button clicked
                    color_idx = int(action.split("_")[1])
                    self._set_active_color(color_idx)
                    return ("set_color", PALETTE_COLORS[color_idx])

                return (action, None)

        return (None, None)

    def _set_active_color(self, index):
        """
        Set the active color button.

        Args:
            index: Index in PALETTE_COLORS.
        """
        for btn in self.buttons:
            if btn.is_color_button:
                btn.is_active = False

            if btn.action == f"color_{index}":
                btn.is_active = True

        self.active_color_index = index
        self.active_color = PALETTE_COLORS[index]

    def update_hover(self, x, y):
        """
        Update button hover states based on cursor position.

        Args:
            x, y: Cursor coordinates.
        """
        for btn in self.buttons:
            btn.is_hovered = btn.contains(x, y) and y <= self.height

    def is_in_toolbar(self, y):
        """
        Check if a y-coordinate is within the toolbar area.

        Args:
            y: Y coordinate.

        Returns:
            bool: True if in toolbar area.
        """
        return y <= self.height
