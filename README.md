# ROI Video Analyzer v2.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | [简体中文](README_ZH.md)

A PyQt5 desktop application for video ROI (Region of Interest) grayscale analysis and threshold-based binarization.

> Perform real-time grayscale statistics on any ROI in a video, generate mean intensity curves, apply threshold binarization, and export results as CSV or PNG.

![](roi_gray_plot.png)

## Features

| Feature | Description |
|----------|-------------|
| Video Playback Control | Supports multiple formats (MP4/AVI/MOV/MKV, etc.), frame-by-frame stepping and continuous playback |
| Interactive ROI | Draw ROI by mouse drag, move ROI, resize via bottom-right handle, zoom with Ctrl + Mouse Wheel |
| Real-time Grayscale Statistics | Mean / Min / Max / Binary result displayed in four real-time statistic cards |
| Grayscale Mean Curve | Calculates ROI grayscale mean frame-by-frame and renders the curve in real time using pyqtgraph |
| Threshold Export | Pixels above threshold → 1, otherwise → 0; exports CSV with custom column names |
| PNG Export | Generates a 300 DPI grayscale mean curve image using matplotlib |
| Dark Theme | Full Catppuccin Mocha QSS theme covering all UI components |
| Dual Processing Engines | ffmpegcv preferred (high-performance ROI cropping), OpenCV fallback for compatibility |

## Installation

```bash
git clone https://github.com/zhuyuhang4/ROI_Video_Analyzer_v2.git
cd ROI_Video_Analyzer_v2
conda create -n py38 python=3.8
conda activate py38
pip install -r requirements.txt
```

### Dependencies

```text
opencv-python==4.10.0.84
PyQt5==5.15.11
pyqtgraph==0.13.3
ffmpegcv==0.3.15
numpy>=1.24.3
matplotlib>=3.7.1
pyinstaller==6.18.0
```

## Usage

```bash
python main.py
```

### Workflow

1. **Open Video** — Click "Open Video" and select a file.
2. **Draw ROI** — Drag the mouse to create a region of interest. The ROI can be moved and resized using the bottom-right handle.
3. **View Statistics** — The side panel displays real-time grayscale mean, minimum, maximum, and threshold results.
4. **Adjust Threshold** — Move the threshold slider (0–255). The preview bar visually separates dark and bright regions.
5. **Export CSV** — Click "Threshold Processing → Export CSV". Frames are processed sequentially and saved.
6. **Export PNG** — Click "Export ROI Grayscale Plot PNG" to generate a 300 DPI grayscale mean curve image.
7. **Compute Curve** — Click "Compute Mean Curve" to render the ROI grayscale trend below the video panel.

### Shortcuts

| Action | Shortcut |
|----------|----------|
| Zoom Video | `Ctrl + Mouse Wheel` |
| Draw ROI | Mouse Drag |
| Move ROI | Drag Inside ROI |
| Resize ROI | Drag Bottom-right Handle |

## Project Structure

```text
main.py                 # Application entry point
app.py                  # VideoPlayer main window (toolbar + video panel + side panel layout)
video_label.py          # VideoLabel — video rendering, ROI interaction, zoom & pan
side_panel.py           # Right-side control panel (statistics cards, threshold settings, export actions)
threshold_widget.py     # Threshold widget (slider/spinbox synchronization, preview bar, column name input)
export_worker.py        # Background processing thread (ffmpegcv preferred, OpenCV fallback)
styles.py               # Catppuccin Mocha dark-theme QSS stylesheet
build.bat               # Windows build script
docs/                   # Architecture documentation and Mermaid diagrams
```

## Packaging

```bash
# Single executable
python build_simple.py

# Windows batch script
build.bat
```

The output files will be generated in the `dist/` directory.

## Technical Highlights

- **Dual-engine fallback**: ExportWorker prioritizes ffmpegcv ROI cropping via `crop_xywh`; automatically falls back to OpenCV on failure.
- **Even-dimension ROI alignment**: ffmpegcv requires even width and height; dimensions are automatically adjusted.
- **Signal debouncing**: Threshold slider and spinbox are synchronized using `blockSignals` to prevent recursive updates.
- **Safe thread termination**: Background threads are stopped safely using a flag variable combined with `wait()`.
- **CSV encoding**: Uses `utf-8-sig`, allowing direct opening in Microsoft Excel without garbled characters.

## License

MIT
