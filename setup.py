#!/usr/bin/env python3
"""
Setup script for Car Rental System
This script helps initialize the application and create necessary directories.
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def create_directories():
    """Create necessary directories for the application."""
    directories = [
        'templates',
        'static/css',
        'static/js',
        'Fatigue-Detection-System-Based-On-Behavioural-Characteristics-Of-Driver/models',
        'uploads',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def install_requirements():
    """Install Python requirements."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Installed Python requirements")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def download_model():
    """Download the dlib facial landmark model."""
    model_path = "Fatigue-Detection-System-Based-On-Behavioural-Characteristics-Of-Driver/models/shape_predictor_70_face_landmarks.dat"
    
    if os.path.exists(model_path):
        print("✓ Model file already exists")
        return True
    
    print("⚠️  Model file not found. Please download 'shape_predictor_70_face_landmarks.dat'")
    print("   from: http://dlib.net/files/shape_predictor_70_face_landmarks.dat.bz2")
    print("   Extract it and place in: Fatigue-Detection-System-Based-On-Behavioural-Characteristics-Of-Driver/models/")
    return False

def create_env_file():
    """Create a basic .env file if it doesn't exist."""
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("SECRET_KEY=your-secret-key-change-this-in-production\n")
            f.write("DATABASE_URL=sqlite:///car_rental.db\n")
            f.write("DEBUG=True\n")
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python version {sys.version.split()[0]} is compatible")
    return True

def main():
    """Main setup function."""
    print("🚗 Car Rental System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install requirements
    print("\n📦 Installing requirements...")
    if not install_requirements():
        print("⚠️  Please install requirements manually: pip install -r requirements.txt")
    
    # Create .env file
    print("\n⚙️  Setting up configuration...")
    create_env_file()
    
    # Check for model file
    print("\n🤖 Checking AI model...")
    download_model()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Download the dlib model file if not already done")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("4. Register as admin with username: admin, password: admin123")
    
    print("\n🔧 Configuration:")
    print("- Edit .env file for production settings")
    print("- Update SECRET_KEY for security")
    print("- Configure database URL for production")

if __name__ == "__main__":
    main()
