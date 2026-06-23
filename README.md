# 🍎 Fruit Ninja - Hand Tracking Game

A gesture-based fruit cutting game powered by hand tracking with MediaPipe and OpenCV.

## 📋 Project Structure

```
ninja-fruite/
├── main.py                 # Entry point
├── config.py              # Game configuration
├── venv/                  # Python virtual environment
├── requirements.txt       # Python dependencies
├── game/
│   ├── __init__.py
│   ├── game_engine.py     # Core game loop & FPS management
│   ├── fruit.py           # Fruit physics & rendering (TODO)
│   ├── bomb.py            # Bomb class (TODO)
│   ├── score_manager.py   # Score & lives tracking (TODO)
│   └── collision.py       # Collision detection (TODO)
├── vision/
│   ├── __init__.py
│   ├── hand_tracker.py    # MediaPipe hand detection wrapper
│   └── gesture_detector.py # Gesture recognition (TODO)
├── ui/
│   ├── __init__.py
│   ├── hud.py            # Score/lives display
│   ├── screens.py        # Menu/game over screens (TODO)
│   └── effects.py        # Slice effects (TODO)
├── assets/
│   ├── sounds/           # Audio files
│   └── images/           # Sprite assets
└── data/
    └── highscore.json    # High score persistence
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Webcam

### Installation

1. **Clone/navigate to project**
```bash
cd d:\myprojects\ninja-fruite
```

2. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running Stage 1 (Current)

```bash
python main.py
```

**Controls:**
- `Q` or `ESC`: Quit the game

## 📊 Development Stages

### ✅ Stage 1: Basic Foundation (COMPLETED)
- Display live camera feed
- Hand detection using MediaPipe (21-point skeleton)
- Render hand landmarks and connections
- Frame rate management (30 FPS)
- FPS counter display

### 📅 Stage 2: Fruit Physics (PLANNED)
- Spawn fruits randomly on screen
- Implement fruit physics (gravity, velocity)
- Fruit rendering with simple shapes
- Fruit removal on screen edges

### 📅 Stage 3: Gesture & Collision (PLANNED)
- Detect "slicing" gesture from hand velocity
- Implement collision detection
- Slice fruit on collision
- Slice visual effects

### 📅 Stage 4: Game Mechanics (PLANNED)
- Scoring system
- Lives system
- Bomb obstacles (lose 50 points)
- Combo multiplier
- Game over condition

### 📅 Stage 5: Polish & Audio (PLANNED)
- Menu screen
- Game over screen
- Sound effects (slice, bomb, background music)
- High score persistence
- Visual polish and effects

## 🛠 Key Technologies

- **OpenCV**: Camera capture, image processing
- **MediaPipe**: Real-time hand landmark detection
- **NumPy**: Mathematical operations and vectors
- **Pygame**: Game engine and audio

## 📝 Configuration

Edit `config.py` to customize:
- Screen resolution
- Target FPS
- Hand detection sensitivity
- Colors and sizes
- Game physics parameters

## 🐛 Troubleshooting

**Camera not detected:**
- Check webcam connection
- Verify no other application is using the camera
- Try camera index 1 in `game_engine.py`: `cv2.VideoCapture(1)`

**Poor hand detection:**
- Improve lighting conditions
- Check hand detection confidence thresholds in `config.py`
- Ensure hand is fully visible in camera frame

## 📖 References

- [MediaPipe Hand Tracking](https://mediapipe.dev/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [NumPy Documentation](https://numpy.org/)

## 📄 License

Educational project

---

**Current Status:** Stage 1 - Basic Foundation (Ready for testing)
