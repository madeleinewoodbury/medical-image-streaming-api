# Medical Image Streaming API

A FastAPI-based backend service for streaming and processing medical DICOM images in real-time using WebRTC technology. This API provides advanced image segmentation capabilities using computer vision algorithms including Watershed and Active Contours (Snakes) methods.

## Table of Contents

- [Frontend Application](#frontend-application)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Image Management](#image-management)
  - [Image Processing & Streaming](#image-processing--streaming)
  - [Stream Management](#stream-management)
- [Image Processing Algorithms](#image-processing-algorithms)
  - [Watershed Segmentation](#watershed-segmentation)
  - [Active Contours (Snakes)](#active-contours-snakes)
- [Project Structure](#project-structure)
- [Development](#development)
  - [Running in Development Mode](#running-in-development-mode)
  - [Adding New Segmentation Algorithms](#adding-new-segmentation-algorithms)
- [Contributing](#contributing)
- [License](#license)
- [Related Projects](#related-projects)

## Frontend Application

The frontend implementation is available in a separate repository: [Medical Image Streaming App](https://github.com/madeleinewoodbury/medical-image-streaming-app)

## Features

- **DICOM Image Processing**: Upload and process medical DICOM (.dcm) files
- **Real-time Streaming**: WebRTC-based video streaming of processed images
- **Image Segmentation**: Two advanced segmentation algorithms:
  - Watershed segmentation with customizable thresholds
  - Active Contours (Snakes) with adjustable parameters
- **REST API**: Clean RESTful endpoints for image management and processing
- **Cross-Origin Support**: CORS-enabled for web application integration

## Technology Stack

- **FastAPI**: Modern Python web framework for building APIs
- **WebRTC (aiortc)**: Real-time communication for video streaming
- **OpenCV**: Computer vision and image processing
- **scikit-image**: Advanced image processing algorithms
- **PyDICOM**: DICOM medical image format handling
- **NumPy**: Numerical computing for image data
- **Uvicorn**: ASGI server for FastAPI

## Prerequisites

- Python 3.12+
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/madeleinewoodbury/medical-image-streaming-api
cd medical-image-streaming/api
```

2. Create and activate a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- **GET** `/` - Returns a simple health check message

### Image Management
- **POST** `/images` - Upload multiple DICOM images
  - Accepts: `multipart/form-data` with DICOM files (.dcm)
  - Returns: Success confirmation
- **GET** `/images` - Check if images are available for processing

### Image Processing & Streaming

#### Watershed Segmentation
- **POST** `/watershed` - Start watershed segmentation stream
  - **Parameters:**
    - `offer`: WebRTC SDP offer (required)
    - `threshold_ratio`: Threshold ratio for segmentation (default: 0.5)
    - `kernel_size`: Morphological kernel size (default: 3)
    - `image_delay`: Delay between frames in seconds (default: 1)

#### Active Contours (Snakes) Segmentation
- **POST** `/snakes` - Start snakes segmentation stream
  - **Parameters:**
    - `offer`: WebRTC SDP offer (required)
    - `kernel_size`: Morphological kernel size (default: 3)
    - `x`: Initial contour center X coordinate (default: 100)
    - `y`: Initial contour center Y coordinate (default: 100)
    - `radius`: Initial contour radius (default: 50)
    - `image_delay`: Delay between frames in seconds (default: 1)

### Stream Management
- **POST** `/stop-stream` - Stop all active streams and clean up connections

## Image Processing Algorithms

### Watershed Segmentation
The watershed algorithm treats the image like a topographic surface and finds watershed lines that separate different regions. The implementation includes:
- Gaussian blur for noise reduction
- Morphological operations (opening and closing)
- Otsu's thresholding for binary image creation
- Distance transform for marker initialization
- Canny edge detection for improved segmentation

### Active Contours (Snakes)
The active contours method uses energy minimization to fit a contour to object boundaries. Features include:
- User-defined initial contour position and size
- Configurable energy parameters (alpha, beta, gamma)
- Real-time contour evolution visualization
- Elliptical initialization for medical image analysis

## Project Structure

```
api/
├── main.py                 # FastAPI application and WebRTC handling
├── requirements.txt        # Python dependencies
├── models/
│   ├── ImageProcessor.py   # Abstract base class and segmentation algorithms
│   ├── ImageStreamTrack.py # WebRTC video stream track implementation
│   └── __init__.py
├── routes/
│   ├── images.py          # Image upload and management endpoints
│   └── __init__.py
├── uploads/               # Directory for uploaded DICOM files
│   └── *.dcm             # DICOM image files
├── test_main.http        # HTTP test requests
└── venv/                 # Virtual environment (created after setup)
```

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Segmentation Algorithms
1. Create a new class inheriting from `ImageProcessor` in `models/ImageProcessor.py`
2. Implement the `apply_segmentation()` method
3. Add a new endpoint in `main.py` following the existing patterns

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Related Projects

- [Medical Image Streaming Frontend](https://github.com/madeleinewoodbury/medical-image-streaming-app) - React-based web application for interacting with this API