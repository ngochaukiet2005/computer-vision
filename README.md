# Smart Parking Guidance System - Computer Vision

## Project Overview

A real-time computer vision system for intelligent parking spot detection and management. The system analyzes live video streams from multiple cameras to classify parking spots as occupied or empty, providing drivers with automated parking guidance.

### Key Features

- 🎥 **Multi-camera support**: Process multiple parking areas simultaneously
- 🚗 **Real-time detection**: Sub-second response to parking spot status changes  
- 🧠 **Intelligent routing**: Guide drivers to nearest available spot
- 🔧 **Configurable UI**: Draw parking spot regions directly on video
- 💻 **Clean architecture**: Separation of ML pipeline and web application
- 📊 **No black-box AI**: Uses explainable classical CV + SVM (no opaque deep learning)

## Technology Stack

### Backend
- **Framework**: FastAPI + WebSocket
- **CV Library**: OpenCV 4.9
- **ML**: SVM (scikit-image compatible)
- **Language**: Python 3.8+

### Frontend  
- **Framework**: Vue 3 + Vite
- **Styling**: CSS3 with glassmorphism UI
- **Real-time**: WebSocket integration

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone repository**
```bash
git clone <repository>
cd computer-vision
```

2. **Backend setup**
```bash
cd backend
pip install -r requirements.txt
python core_cv/train_svm.py      # Train parking detection model
python main.py                     # Start API server
```

3. **Frontend setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Access application**
Open browser to `http://localhost:5173`

## Project Structure

```
computer-vision/
├── backend/                 # Python FastAPI server
│   ├── core_cv/            # Computer vision pipeline
│   │   ├── preprocessing.py # Ch2: Image preprocessing
│   │   ├── feature_extraction.py # Ch3: HOG features
│   │   ├── segmentation.py # Ch4: Background detection
│   │   ├── pipeline.py      # Main CV pipeline
│   │   └── train_svm.py    # Ch5: SVM model training
│   ├── data/               # Training and video data
│   ├── models/             # Trained ML models
│   ├── main.py             # FastAPI application
│   ├── extract_frames.py   # Utility: extract video frames
│   └── README.md           # Backend documentation
│
├── frontend/               # Vue 3 application
│   ├── src/
│   │   ├── App.vue         # Main application UI
│   │   ├── components/     # Vue components
│   │   └── services/       # WebSocket client
│   └── README.md           # Frontend documentation
│
├── notebooks/              # Jupyter Notebooks for research & experiments
│   ├── 01_preprocessing_exploration.ipynb
│   ├── 02_svm_training_analysis.ipynb
│   ├── 03_cv_pipeline_demo.ipynb
│   ├── 04_background_analysis.ipynb
│   └── README.md           # Notebook documentation
│
├── docs/                   # Documentation and requirements
│   ├── srs_content.txt    # Software Requirements Specification
│   └── pdf_content.txt    # Assignment requirements
│
└── README.md              # This file
```

## How It Works

### 1. System Setup
- User draws parking spot regions on video frames (bounding boxes)
- Configures camera locations and spot identifiers
- Uploads video stream to system

### 2. Processing Pipeline
```
Video Frame → Preprocessing → Feature Extraction → Segmentation → Classification
```

**Stage 1 - Preprocessing (Chapter 2)**
- Convert to grayscale
- Apply CLAHE (adaptive histogram equalization)
- Gaussian blur for noise reduction

**Stage 2 - Feature Extraction (Chapter 3)**
- Compute HOG (Histogram of Oriented Gradients) descriptors
- Captures vehicle shape information

**Stage 3 - Segmentation (Chapter 4)**
- Variance-based background detection
- Early exit for obviously empty spots

**Stage 4 - Classification (Chapter 5)**
- SVM model predicts: "occupied" or "empty"
- Asymmetric smoothing reduces false positives

### 3. Real-time Guidance
- System maintains live parking spot status
- When user requests parking spot ("Car Entering")
- System finds and recommends nearest empty spot
- Frontend displays guidance with highlighted spot

## Features Implemented

### Functional Requirements ✅
- [x] Multi-camera management
- [x] Parking spot configuration with bounding boxes
- [x] Real-time visualization
- [x] Multi-floor/zone support
- [x] Real-time "Car Entering" event trigger
- [x] Automated spot assignment logic
- [x] Live WebSocket updates

### Technical Requirements ✅
- [x] Python with OpenCV/scikit-image
- [x] 4+ CV techniques from curriculum
- [x] Real data training (not synthetic)
- [x] Explainable classification (SVM, not black-box DL)
- [x] Reproducible setup with README
- [x] Original source code

## Configuration

### Training Data Preparation

1. **Collect parking lot video** (minimum 1-2 minutes)
2. **Extract frames**: `python backend/extract_frames.py`
3. **Label frames**: Organize into `data/train/occupied/` and `data/train/empty/`
4. **Train model**: `python backend/core_cv/train_svm.py`

### Adjustable Parameters

**Preprocessing**
```python
# In core_cv/preprocessing.py
CLAHE clipLimit: 2.0         # Increase for more contrast
Blur kernel: (3,3)           # Increase for more smoothing
```

**Feature Extraction**
```python
# In core_cv/feature_extraction.py
HOG window: 64x128           # Adjust for spot size
Cell size: 8x8               # Smaller = more detail
```

**Segmentation**
```python
# In core_cv/segmentation.py
variance_threshold: 150      # Lower = easier to detect as empty
```

**Classification**
```python
# In core_cv/pipeline.py
history_size: 5              # Frames for status smoothing
occ_count >= 2              # Frames needed to mark occupied
```

## Performance Characteristics

- **Latency**: 50-100ms per frame (varies with camera count)
- **Throughput**: 25 FPS per camera supported
- **Memory**: ~200MB base + ~50MB per camera
- **GPU**: Not required (CPU-based processing)

## Documentation

- [Backend Documentation](./backend/README.md) - Setup, API, configuration
- [Notebooks Exploration](./notebooks/README.md) - Research and experiments
- [Technical Details](./backend/TECHNICAL.md) - CV techniques explained
- [Assignment Requirements](./docs/pdf_content.txt) - Course requirements
- [System Specification](./docs/srs_content.txt) - Detailed SRS

## Development Notes

### Key Design Decisions

1. **Classical CV over Deep Learning**
   - More explainable for assignment requirements
   - Faster inference on CPU
   - Less training data required
   - Meets course curriculum objectives

2. **SVM over Other Classifiers**
   - Proven effectiveness for parking detection
   - Handles high-dimensional HOG features well
   - Fast inference, good generalization

3. **WebSocket over REST**
   - Real-time updates without polling
   - Efficient for continuous video processing
   - Natural fit for streaming video data

4. **Vue 3 Frontend**
   - Component-based architecture
   - Easy to extend features
   - Good performance for video handling

## Testing

### Manual Testing
1. Start backend: `python backend/main.py`
2. Start frontend: `npm run dev`
3. Upload sample video
4. Draw parking spots on video
5. Verify real-time spot detection

### Automated Testing
```bash
# Run backend tests
cd backend
python -m pytest tests/

# Run frontend tests
cd frontend  
npm run test
```

## Troubleshooting

**Model not found error**
- Solution: Run `python backend/core_cv/train_svm.py`

**Poor detection accuracy**
- Solution: Collect more training images (100+ per class)
- Ensure consistent lighting conditions
- Verify parking spot boundaries are accurate

**WebSocket connection failed**
- Solution: Check backend is running on port 8000
- Verify firewall allows WebSocket connections

**Video playback lag**
- Solution: Reduce video resolution
- Increase frame skip in `main.py` websocket_endpoint
- Check system CPU/memory usage

## Future Improvements

- [ ] Add vehicle type classification (car/motorcycle/bus)
- [ ] Implement vehicle re-identification across cameras
- [ ] Add 3D point cloud support for slope detection
- [ ] Mobile app for parking notifications
- [ ] Historical analytics dashboard
- [ ] Integration with parking payment systems

## Academic Notes

This project fulfills the course assignment requirements by:

1. ✅ Implementing 4+ image processing techniques from curriculum
2. ✅ Demonstrating understanding of:
   - Image preprocessing (Chapter 2)
   - Edge detection & features (Chapter 3)
   - Image segmentation (Chapter 4)
   - Classification methods (Chapter 5)
3. ✅ Using real parking lot data
4. ✅ Explaining technique selection rationale
5. ✅ Providing reproducible code with documentation
6. ✅ Building complete system (not just pipeline)

## License

This project is created for educational purposes as part of computer vision course assignment.

## Contributors

- Computer Vision Course Team
- Project Development Team

---

**Last Updated**: April 2026
