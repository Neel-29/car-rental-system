# Models Directory

This directory contains the AI models required for the fatigue detection system.

## Required Files

### shape_predictor_70_face_landmarks.dat
This is the dlib facial landmark predictor model required for eye detection and fatigue monitoring.

**Download Instructions:**
1. Go to: https://github.com/davisking/dlib-models
2. Download `shape_predictor_70_face_landmarks.dat.bz2`
3. Extract the `.bz2` file using 7-Zip or similar tool
4. Place `shape_predictor_70_face_landmarks.dat` in this directory

**Alternative Download:**
- Direct link: https://github.com/davisking/dlib-models/raw/master/shape_predictor_70_face_landmarks.dat.bz2
- File size: ~99.7 MB (compressed), ~99.7 MB (uncompressed)

## Usage
The system will automatically detect if the model file is present and enable/disable fatigue detection accordingly.

## Note
Without this model file, the fatigue detection features will be disabled, but the rest of the car rental system will function normally.
