import cv2
import numpy as np
import dlib
from scipy.spatial import distance as dist
import threading
import time
import json
from flask import jsonify
import base64
import pygame
import os

class RealTimeFatigueDetector:
    def __init__(self):
        self.FACE_DOWNSAMPLE_RATIO = 0.45
        self.RESIZE_HEIGHT = 460
        self.thresh = 0.27
        self.modelPath = "models/shape_predictor_70_face_landmarks.dat"
        
        # Initialize dlib components
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.modelPath)
        
        # Eye landmark indices
        self.leftEyeIndex = [36, 37, 38, 39, 40, 41]
        self.rightEyeIndex = [42, 43, 44, 45, 46, 47]
        
        # Monitoring variables
        self.blinkCount = 0
        self.drowsy = 0
        self.state = 0
        self.blinkTime = 0.15
        self.drowsyTime = 1.5
        self.ALARM_ON = False
        
        # Calibration variables
        self.spf = 0.0
        self.drowsyLimit = 0
        self.falseBlinkLimit = 0
        self.calibrated = False
        
        # Real-time processing
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.landmarks = None
        self.ear_history = []
        self.max_ear_history = 50
        
        # Alarm system
        self.alarm_playing = False
        self.alarm_thread = None
        self.initialize_alarm()

    def initialize_alarm(self):
        """Initialize pygame for alarm sounds"""
        try:
            pygame.mixer.init()
            # Create a simple alarm sound if no audio file exists
            self.alarm_sound = self.create_alarm_sound()
        except Exception as e:
            print(f"Warning: Could not initialize audio system: {e}")
            self.alarm_sound = None

    def create_alarm_sound(self):
        """Create a simple alarm sound using pygame"""
        try:
            # Create a simple beep sound
            sample_rate = 22050
            duration = 0.5  # seconds
            frequency = 800  # Hz
            
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                arr[i][0] = 32767 * np.sin(2 * np.pi * frequency * i / sample_rate)
                arr[i][1] = arr[i][0]
            
            sound = pygame.sndarray.make_sound(arr.astype(np.int16))
            return sound
        except Exception as e:
            print(f"Warning: Could not create alarm sound: {e}")
            return None

    def play_alarm(self):
        """Play drowsiness alarm"""
        if not self.alarm_playing and self.alarm_sound:
            self.alarm_playing = True
            self.alarm_thread = threading.Thread(target=self._alarm_loop)
            self.alarm_thread.daemon = True
            self.alarm_thread.start()

    def stop_alarm(self):
        """Stop drowsiness alarm"""
        self.alarm_playing = False
        if self.alarm_thread:
            self.alarm_thread.join(timeout=1)

    def _alarm_loop(self):
        """Alarm loop that plays sound repeatedly"""
        while self.alarm_playing and self.alarm_sound:
            try:
                self.alarm_sound.play()
                time.sleep(0.5)  # Play every 0.5 seconds
            except Exception as e:
                print(f"Error playing alarm: {e}")
                break

    def eye_aspect_ratio(self, eye):
        """Calculate Eye Aspect Ratio (EAR)"""
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def get_landmarks(self, im):
        """Get facial landmarks using dlib"""
        imSmall = cv2.resize(im, None, 
                            fx = 1.0/self.FACE_DOWNSAMPLE_RATIO, 
                            fy = 1.0/self.FACE_DOWNSAMPLE_RATIO, 
                            interpolation = cv2.INTER_LINEAR)

        rects = self.detector(imSmall, 0)
        if len(rects) == 0:
            return None

        newRect = dlib.rectangle(int(rects[0].left() * self.FACE_DOWNSAMPLE_RATIO),
                                int(rects[0].top() * self.FACE_DOWNSAMPLE_RATIO),
                                int(rects[0].right() * self.FACE_DOWNSAMPLE_RATIO),
                                int(rects[0].bottom() * self.FACE_DOWNSAMPLE_RATIO))

        points = []
        [points.append((p.x, p.y)) for p in self.predictor(im, newRect).parts()]
        return points

    def check_eye_status(self, landmarks):
        """Check if eyes are open or closed"""
        if landmarks is None:
            return 0, 0.0
        
        leftEAR = self.eye_aspect_ratio([landmarks[i] for i in self.leftEyeIndex])
        rightEAR = self.eye_aspect_ratio([landmarks[i] for i in self.rightEyeIndex])
        ear = (leftEAR + rightEAR) / 2.0
        
        eyeStatus = 1 if ear >= self.thresh else 0
        return eyeStatus, ear

    def check_blink_status(self, eyeStatus):
        """Update blink and drowsiness status"""
        if self.state >= 0 and self.state <= self.falseBlinkLimit:
            if eyeStatus:
                self.state = 0
                # Stop alarm if eyes are open
                if self.drowsy:
                    self.stop_alarm()
                    self.drowsy = 0
            else:
                self.state += 1
        elif self.state >= self.falseBlinkLimit and self.state < self.drowsyLimit:
            if eyeStatus:
                self.blinkCount += 1 
                self.state = 0
            else:
                self.state += 1
        else:
            if eyeStatus:
                self.state = 0
                self.drowsy = 1
                self.blinkCount += 1
                # Play alarm for drowsiness
                self.play_alarm()
            else:
                self.drowsy = 1
                # Play alarm for drowsiness
                self.play_alarm()

    def calibrate_system(self):
        """Calibrate the system for optimal performance"""
        print("Calibrating fatigue detection system...")
        totalTime = 0.0
        validFrames = 0
        dummyFrames = 100
        
        if self.cap is None:
            return False
        
        for i in range(10):
            ret, frame = self.cap.read()
        
        while validFrames < dummyFrames:
            validFrames += 1
            t = time.time()
            ret, frame = self.cap.read()
            
            if not ret:
                break
                
            height, width = frame.shape[:2]
            IMAGE_RESIZE = np.float32(height)/self.RESIZE_HEIGHT
            frame = cv2.resize(frame, None, 
                            fx = 1/IMAGE_RESIZE, 
                            fy = 1/IMAGE_RESIZE, 
                            interpolation = cv2.INTER_LINEAR)

            adjusted = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            landmarks = self.get_landmarks(adjusted)
            timeLandmarks = time.time() - t

            if landmarks is not None:
                totalTime += timeLandmarks
        
        if validFrames > 0:
            self.spf = totalTime/validFrames
            self.drowsyLimit = self.drowsyTime/self.spf
            self.falseBlinkLimit = self.blinkTime/self.spf
            self.calibrated = True
            print(f"Calibration complete! SPF: {self.spf:.4f}s")
            return True
        return False

    def start_camera(self, camera_index=0):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            return False
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        return True

    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def process_frame(self):
        """Process a single frame for fatigue detection"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Store current frame
        self.current_frame = frame.copy()
        
        # Resize frame
        height, width = frame.shape[:2]
        IMAGE_RESIZE = np.float32(height)/self.RESIZE_HEIGHT
        frame = cv2.resize(frame, None, 
                        fx = 1/IMAGE_RESIZE, 
                        fy = 1/IMAGE_RESIZE, 
                        interpolation = cv2.INTER_LINEAR)

        # Preprocess frame
        adjusted = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        
        # Get landmarks
        landmarks = self.get_landmarks(adjusted)
        self.landmarks = landmarks
        
        if landmarks is not None:
            # Check eye status
            eyeStatus, ear = self.check_eye_status(landmarks)
            self.check_blink_status(eyeStatus)
            
            # Update EAR history
            self.ear_history.append(ear)
            if len(self.ear_history) > self.max_ear_history:
                self.ear_history.pop(0)
            
            # Draw landmarks on frame
            self.draw_landmarks(frame, landmarks)
            
            return {
                "frame": frame,
                "blink_count": self.blinkCount,
                "drowsy": bool(self.drowsy),
                "ear": ear,
                "avg_ear": np.mean(self.ear_history) if self.ear_history else 0.0,
                "landmarks": landmarks,
                "face_detected": True
            }
        else:
            return {
                "frame": frame,
                "blink_count": self.blinkCount,
                "drowsy": bool(self.drowsy),
                "ear": 0.0,
                "avg_ear": np.mean(self.ear_history) if self.ear_history else 0.0,
                "landmarks": None,
                "face_detected": False
            }

    def draw_landmarks(self, frame, landmarks):
        """Draw facial landmarks on frame"""
        if landmarks is None:
            return
        
        # Draw eye landmarks
        for i in self.leftEyeIndex:
            cv2.circle(frame, (landmarks[i][0], landmarks[i][1]), 2, (0, 0, 255), -1)
        
        for i in self.rightEyeIndex:
            cv2.circle(frame, (landmarks[i][0], landmarks[i][1]), 2, (0, 0, 255), -1)
        
        # Draw face rectangle
        if landmarks:
            x_coords = [p[0] for p in landmarks]
            y_coords = [p[1] for p in landmarks]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            cv2.rectangle(frame, (x_min, y_max), (x_max, y_min), (0, 255, 0), 2)

    def get_status(self):
        """Get current monitoring status"""
        return {
            "blink_count": self.blinkCount,
            "drowsy": bool(self.drowsy),
            "ear": self.ear_history[-1] if self.ear_history else 0.0,
            "avg_ear": np.mean(self.ear_history) if self.ear_history else 0.0,
            "face_detected": self.landmarks is not None,
            "calibrated": self.calibrated,
            "is_running": self.is_running
        }

    def reset_counters(self):
        """Reset all counters"""
        self.blinkCount = 0
        self.drowsy = 0
        self.state = 0
        self.ear_history = []
        self.stop_alarm()

    def get_ear_history(self):
        """Get EAR history for graphing"""
        return self.ear_history.copy()

    def get_ear_statistics(self):
        """Get EAR statistics"""
        if not self.ear_history:
            return {
                'min': 0.0,
                'max': 0.0,
                'avg': 0.0,
                'current': 0.0,
                'trend': 'stable'
            }
        
        current_ear = self.ear_history[-1] if self.ear_history else 0.0
        avg_ear = np.mean(self.ear_history)
        min_ear = np.min(self.ear_history)
        max_ear = np.max(self.ear_history)
        
        # Calculate trend (last 10 values vs previous 10)
        if len(self.ear_history) >= 20:
            recent_avg = np.mean(self.ear_history[-10:])
            previous_avg = np.mean(self.ear_history[-20:-10])
            if recent_avg > previous_avg * 1.05:
                trend = 'increasing'
            elif recent_avg < previous_avg * 0.95:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'min': float(min_ear),
            'max': float(max_ear),
            'avg': float(avg_ear),
            'current': float(current_ear),
            'trend': trend
        }

# Global detector instance
fatigue_detector = RealTimeFatigueDetector()
