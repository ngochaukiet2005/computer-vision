# Smart Parking CV Backend

## Overview

This backend implements a Computer Vision pipeline for intelligent parking spot detection and management. The system processes real-time video streams to classify parking spots as empty or occupied, supporting multi-camera/multi-floor deployments.

## Architecture

### Core Components

1. **Pipeline (core_cv/pipeline.py)**
   - Main orchestrator that processes video frames
   - Integrates preprocessing, feature extraction, and classification
   - Manages spot status smoothing to reduce false positives

2. **Preprocessing (core_cv/preprocessing.py)** - Chapter 2
   - Grayscale conversion
   - CLAHE (Contrast Limited Adaptive Histogram Equalization) for lighting normalization
   - Gaussian blur for noise reduction
   - Standardized image resizing to 64x128 pixels

3. **Feature Extraction (core_cv/feature_extraction.py)** - Chapter 3
   - HOG (Histogram of Oriented Gradients) descriptor
   - Captures vehicle shape and edge information
   - Window size: 64x128, Block size: 16x16, Cell size: 8x8

4. **Segmentation (core_cv/segmentation.py)** - Chapter 4
   - Variance-based background detection
   - Early exit optimization for clearly empty spots
   - Reduces SVM computation time

5. **Classification (train_svm.py)** - Chapter 5
   - SVM (Support Vector Machine) model
   - Trained on extracted parking lot images
   - Supports data augmentation (flips, brightness adjustment)
   - Linear kernel with automatic C parameter tuning

### API

- **FastAPI** with WebSocket support
- `/upload-config-multi` - Configure cameras and parking spots
- `/ws/parking` - Real-time parking state WebSocket
  - `sync_frame` action: Update parking states
  - `car_enter` action: Find nearest empty spot

## Installation

### 1. Requirements

- Python 3.8+
- pip or conda

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Training Data Setup

```bash
# Create training data directories
mkdir -p data/train/occupied
mkdir -p data/train/empty
mkdir -p data/raw_videos
```

Place sample parking lot images in:
- `data/train/occupied/` - Images showing parking spots with cars
- `data/train/empty/` - Images showing empty parking spots

Each image should be approximately 64x128 pixels or will be resized automatically.

### 4. Train SVM Model

```bash
python core_cv/train_svm.py
```

This will:
- Load training images from `data/train/occupied` and `data/train/empty`
- Apply preprocessing and extract HOG features
- Augment data (horizontal flips, brightness adjustments)
- Train SVM with automatic hyperparameter tuning
- Save model to `models/svm_parking_model.xml`

### 5. Extract Frames (Optional)

If you have raw parking lot video, extract frames for manual labeling:

```bash
python extract_frames.py
```

Extracts one frame every 30 frames and saves to `data/raw_frames/`

## Running the Server

```bash
python main.py
```

Server starts at `http://localhost:8000`

## API Usage

### Upload Configuration

```python
# POST /upload-config-multi
{
  "config": {
    "camera_1": [
      {"id": "A-01", "box": [10, 20, 40, 50], "status": "empty"},
      {"id": "A-02", "box": [60, 20, 40, 50], "status": "empty"}
    ]
  },
  "video_camera_1": <video_file>
}
```

### WebSocket Events

Connect to `ws://localhost:8000/ws/parking`

**Send (sync_frame):**
```json
{"action": "sync_frame"}
```

**Receive:**
```json
{
  "status": "success",
  "parking_state": {
    "camera_1": [
      {"id": "A-01", "status": "occupied", "box": [10, 20, 40, 50]}
    ]
  }
}
```

**Send (car_enter):**
```json
{"action": "car_enter"}
```

**Receive:**
```json
{
  "status": "success",
  "parking_state": {...},
  "closest_empty_spot": "A-02"
}
```

## Configuration

### Spot Status Smoothing

The pipeline uses asymmetric smoothing to reduce flickering:
- Detects occupied spots: 2 consecutive frames with cars (fast response)
- Clears occupied spots: 5 consecutive empty frames (prevents false clearing)

Configurable in `core_cv/pipeline.py`:
```python
self.history_size = 5  # Number of frames for voting
```

### Background Detection

Variance threshold for empty spot detection (optimizable):
```python
is_flat_background(gray_image, variance_threshold=150)
```

## Performance Considerations

- **Real-time processing**: Skips frames to maintain synchronization with 25 FPS video
- **Multi-camera support**: Independent pipelines per camera
- **Memory**: Maintains spot history per camera (minimal overhead)

## Troubleshooting

### Model not loading
- Ensure `models/svm_parking_model.xml` exists
- Run `python core_cv/train_svm.py` to generate it

### Poor accuracy
- Collect more training images (100+ per class)
- Ensure images are properly labeled (correct folder)
- Check video quality and lighting conditions

### Performance issues
- Reduce frame skip rate in websocket_endpoint
- Profile using `cProfile` module
- Consider reducing image size from 64x128

## File Structure

```
backend/
├── core_cv/
│   ├── __init__.py
│   ├── pipeline.py          # Main CV pipeline
│   ├── preprocessing.py     # Ch2: Image preprocessing
│   ├── feature_extraction.py # Ch3: HOG descriptor
│   ├── segmentation.py      # Ch4: Background detection
│   └── train_svm.py        # Ch5: Model training
├── data/
│   ├── train/
│   │   ├── occupied/        # Training images with cars
│   │   └── empty/           # Training images without cars
│   └── raw_videos/          # Raw video files
├── models/
│   └── svm_parking_model.xml # Trained SVM model
├── main.py                   # FastAPI server
├── extract_frames.py         # Video frame extraction tool
└── requirements.txt
```

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **opencv-python** - Computer vision library
- **numpy** - Numerical computations
- **scikit-image** - Image processing (optional but included)

## Future Improvements

1. Add real-time FPS monitoring
2. Implement parking lot capacity tracking
3. Add vehicle type classification (car/motorcycle/bus)
4. Support 3D point cloud for slope detection
5. Add mobile app notifications
6. Implement vehicle re-identification across cameras
