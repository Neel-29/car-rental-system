#!/usr/bin/env python3
"""
Download the dlib facial landmark predictor model.
This is required for the fatigue detection system.
"""

import os
import urllib.request
import bz2

def download_model():
    """Download and extract the dlib facial landmark model."""
    model_url = "http://dlib.net/files/shape_predictor_70_face_landmarks.dat.bz2"
    compressed_file = "models/shape_predictor_70_face_landmarks.dat.bz2"
    model_file = "models/shape_predictor_70_face_landmarks.dat"
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    if os.path.exists(model_file):
        print("✓ Model file already exists")
        return True
    
    try:
        print("📥 Downloading dlib facial landmark model...")
        print(f"   URL: {model_url}")
        print(f"   Saving to: {compressed_file}")
        
        # Download the compressed file
        urllib.request.urlretrieve(model_url, compressed_file)
        print("✓ Download completed")
        
        print("📦 Extracting compressed file...")
        with bz2.BZ2File(compressed_file, 'rb') as source:
            with open(model_file, 'wb') as target:
                target.write(source.read())
        
        # Remove the compressed file
        os.remove(compressed_file)
        print("✓ Extraction completed")
        print(f"✓ Model saved to: {model_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("\n📋 Manual download instructions:")
        print("1. Go to: http://dlib.net/files/shape_predictor_70_face_landmarks.dat.bz2")
        print("2. Download the file")
        print("3. Extract it using 7-Zip or similar tool")
        print("4. Place 'shape_predictor_70_face_landmarks.dat' in the 'models' folder")
        return False

if __name__ == "__main__":
    print("🚀 Dlib Model Downloader")
    print("=" * 40)
    
    if download_model():
        print("\n✅ Model setup completed successfully!")
        print("   You can now run the car rental system with fatigue detection.")
    else:
        print("\n⚠️  Model download failed.")
        print("   Please follow the manual instructions above.")
