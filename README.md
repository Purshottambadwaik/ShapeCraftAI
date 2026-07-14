# AirSketch AI - Smart Shape Recognition using Hand Gestures 🎨✋

> Draw in the air with your finger. AirSketch AI recognizes your shapes and corrects them to perfect geometry — in real time!

---

## 🎯 Features

### Core
- **Hand Detection** — MediaPipe-powered hand tracking
- **Air Drawing** — Draw on a virtual canvas using your index finger
- **Shape Recognition** — Automatically detects triangles, rectangles, squares, circles, lines, and pentagons
- **Shape Correction** — Converts rough hand-drawn shapes to perfect geometry

### Controls
- **Undo** — Revert your last drawing action
- **Clear Canvas** — Start fresh
- **Save Drawing** — Export to `outputs/images/`
- **Color Picker** — Choose from 11 vibrant colors
- **Brush Size** — Adjustable thickness

### UI
- **Toolbar** — Color palette, brush size controls, action buttons
- **Mode Indicator** — Shows current gesture mode (DRAW / STOP / ERASE / SELECT)
- **FPS Counter** — Real-time performance display
- **Shape Labels** — Shows the name of detected shapes

---

## 🖐️ Gesture Controls

| Gesture | Action |
|---------|--------|
| ☝️ Index finger only | **DRAW** — traces path on canvas |
| ✌️ Index + Middle up | **ERASE** — erases at finger position |
| ✊ Closed fist | **STOP** — finishes stroke & detects shape |
| 🖐️ Open palm (4+ fingers) | **SELECT** — interact with toolbar buttons |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `c` | Clear canvas |
| `u` | Undo last shape |
| `s` | Save drawing |
| `+` | Increase brush size |
| `-` | Decrease brush size |

---

## 📦 Installation

```bash
cd AirSketch_AI
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- Webcam
- `opencv-python >= 4.8.0`
- `mediapipe >= 0.10.0`
- `numpy >= 1.24.0`
- `scipy >= 1.10.0`

---

## 🚀 Usage

```bash
python main.py
```

1. Position your hand in front of the webcam
2. Raise your **index finger** to start drawing
3. Draw a shape in the air
4. Make a **fist** to stop drawing — AirSketch will recognize and correct the shape
5. Use **open palm** to interact with the toolbar (change colors, undo, save)

---

## 📁 Project Structure

```
AirSketch_AI/
│
├── main.py                  # Entry point
├── config.py                # All settings and constants
├── requirements.txt         # Dependencies
├── README.md                # This file
│
├── hand_tracking/           # Hand detection module
│   ├── detector.py          # MediaPipe hand detector
│   ├── landmarks.py         # Finger landmark extraction
│   └── gestures.py          # Gesture recognition
│
├── drawing/                 # Drawing engine
│   ├── canvas.py            # Drawing canvas overlay
│   ├── brush.py             # Brush properties
│   ├── smoother.py          # Point smoothing (EMA + moving average)
│   └── history.py           # Undo stack
│
├── shapes/                  # Shape analysis
│   ├── detector.py          # Shape classification
│   ├── corrector.py         # Perfect shape generation
│   ├── renderer.py          # Shape drawing & labels
│   └── geometry.py          # Geometry helper functions
│
├── ui/                      # User interface
│   ├── toolbar.py           # Top toolbar with buttons
│   ├── buttons.py           # Button component
│   └── labels.py            # Text overlays
│
├── utils/                   # Shared utilities
│   ├── helpers.py           # Generic helper functions
│   ├── colors.py            # Color palettes
│   ├── file_manager.py      # Image saving
│   └── fps.py               # FPS counter
│
├── outputs/                 # Saved outputs
│   ├── images/
│   └── videos/
│
├── assets/                  # Resources
│   ├── icons/
│   ├── sounds/
│   └── fonts/
│
└── docs/                    # Documentation
```

---

## 🔧 Architecture

```
Webcam → HandDetector → GestureDetector
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  DRAW      STOP     SELECT
                    │         │         │
                    ▼         ▼         ▼
               Canvas.draw  ShapeDetect Toolbar
                    │         │
                    ▼         ▼
               temp_surface ShapeCorrector
                              │
                              ▼
                        ShapeRenderer
                              │
                              ▼
                      Perfect Shape on Canvas
```

### Design Principles
- **Single Responsibility** — each module has exactly one job
- **No Cross-Module Dependencies** — hand_tracking never draws, shapes never handle webcam
- **Configuration Centralized** — all constants in `config.py`
- **Modular & Extensible** — easy to add new shapes, gestures, or UI elements

---

## 🛣️ Roadmap

- [x] Phase 1: Core drawing & shape detection
- [x] Phase 2: Undo, clear, save, color picker, brush size
- [x] Phase 3: Multiple shapes, labels, toolbar UI
- [ ] Phase 4: Train ML model for shape recognition (replacing OpenCV geometry)

---

## 📄 License

This project is for educational purposes.
