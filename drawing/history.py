"""
AirSketch AI - History (Undo Stack)
Manages canvas state snapshots for undo/redo functionality.
"""

from config import MAX_UNDO_STEPS


class History:
    """
    Stores canvas snapshots for undo support.
    Each snapshot is a copy of the canvas surface at a point in time.
    """

    def __init__(self, max_steps=MAX_UNDO_STEPS):
        """
        Initialize the history stack.

        Args:
            max_steps: Maximum number of undo states to store.
        """
        self.max_steps = max_steps
        self.stack = []

    def push(self, canvas_snapshot):
        """
        Save a canvas state to the undo stack.

        Args:
            canvas_snapshot: A deep copy of the canvas surface (np.array).
        """
        self.stack.append(canvas_snapshot)

        # Trim stack if it exceeds max size
        if len(self.stack) > self.max_steps:
            self.stack = self.stack[-self.max_steps:]

    def undo(self):
        """
        Pop the last state from the stack.

        Returns:
            np.array: Previous canvas state, or None if stack is empty.
        """
        if self.can_undo():
            return self.stack.pop()
        return None

    def can_undo(self):
        """
        Check if there are any states to undo.

        Returns:
            bool: True if undo is possible.
        """
        return len(self.stack) > 0

    def clear(self):
        """Clear all history."""
        self.stack = []

    def get_depth(self):
        """
        Get the number of stored undo states.

        Returns:
            int: Number of snapshots in the stack.
        """
        return len(self.stack)
