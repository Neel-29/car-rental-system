from flask import Blueprint, request, jsonify, Response
import cv2
import base64
import json
from real_time_monitoring import fatigue_detector
import threading
import time

monitoring_bp = Blueprint('monitoring', __name__)

# Global variables for monitoring
monitoring_sessions = {}
monitoring_threads = {}

def generate_frames(session_id):
    """Generate video frames for streaming"""
    global fatigue_detector
    
    while session_id in monitoring_sessions and monitoring_sessions[session_id]['active']:
        try:
            result = fatigue_detector.process_frame()
            if result is None:
                break
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', result['frame'])
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Update session data
            monitoring_sessions[session_id]['data'] = {
                'blink_count': result['blink_count'],
                'drowsy': result['drowsy'],
                'ear': result['ear'],
                'avg_ear': result['avg_ear'],
                'face_detected': result['face_detected']
            }
            
            time.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            print(f"Error in frame generation: {e}")
            break

@monitoring_bp.route('/api/monitor/start_camera/<int:rental_id>', methods=['POST'])
def start_camera_monitoring(rental_id):
    """Start real-time camera monitoring"""
    try:
        # Start camera
        if not fatigue_detector.start_camera():
            return jsonify({"error": "Failed to start camera"}), 500
        
        # Calibrate system
        if not fatigue_detector.calibrate_system():
            fatigue_detector.stop_camera()
            return jsonify({"error": "Failed to calibrate system"}), 500
        
        # Create monitoring session
        session_id = f"session_{rental_id}_{int(time.time())}"
        monitoring_sessions[session_id] = {
            'rental_id': rental_id,
            'active': True,
            'data': {
                'blink_count': 0,
                'drowsy': False,
                'ear': 0.0,
                'avg_ear': 0.0,
                'face_detected': False
            }
        }
        
        fatigue_detector.is_running = True
        
        return jsonify({
            "session_id": session_id,
            "status": "started",
            "message": "Camera monitoring started successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitor/stop_camera/<session_id>', methods=['POST'])
def stop_camera_monitoring(session_id):
    """Stop real-time camera monitoring"""
    try:
        if session_id in monitoring_sessions:
            monitoring_sessions[session_id]['active'] = False
            del monitoring_sessions[session_id]
        
        fatigue_detector.stop_camera()
        fatigue_detector.is_running = False
        
        return jsonify({
            "status": "stopped",
            "message": "Camera monitoring stopped"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitor/video_feed/<session_id>')
def video_feed(session_id):
    """Stream video feed with fatigue detection"""
    if session_id not in monitoring_sessions:
        return "Session not found", 404
    
    return Response(generate_frames(session_id),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@monitoring_bp.route('/api/monitor/status/<session_id>')
def get_monitoring_status(session_id):
    """Get current monitoring status"""
    if session_id not in monitoring_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    status = fatigue_detector.get_status()
    session_data = monitoring_sessions[session_id]['data']
    
    return jsonify({
        "session_id": session_id,
        "active": monitoring_sessions[session_id]['active'],
        "blink_count": status['blink_count'],
        "drowsy": status['drowsy'],
        "ear": status['ear'],
        "avg_ear": status['avg_ear'],
        "face_detected": status['face_detected'],
        "calibrated": status['calibrated'],
        "is_running": status['is_running']
    })

@monitoring_bp.route('/api/monitor/reset/<session_id>', methods=['POST'])
def reset_monitoring(session_id):
    """Reset monitoring counters"""
    try:
        fatigue_detector.reset_counters()
        return jsonify({
            "status": "reset",
            "message": "Monitoring counters reset"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitor/ear_data/<session_id>')
def get_ear_data(session_id):
    """Get EAR history data for graphing"""
    if session_id not in monitoring_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    ear_history = fatigue_detector.get_ear_history()
    ear_stats = fatigue_detector.get_ear_statistics()
    
    return jsonify({
        "ear_history": ear_history,
        "statistics": ear_stats,
        "data_points": len(ear_history)
    })

@monitoring_bp.route('/api/monitor/alarm/stop', methods=['POST'])
def stop_alarm():
    """Stop the drowsiness alarm"""
    try:
        fatigue_detector.stop_alarm()
        return jsonify({
            "status": "stopped",
            "message": "Alarm stopped"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitor/alarm/test', methods=['POST'])
def test_alarm():
    """Test the alarm system"""
    try:
        fatigue_detector.play_alarm()
        # Stop after 2 seconds
        threading.Timer(2.0, fatigue_detector.stop_alarm).start()
        return jsonify({
            "status": "playing",
            "message": "Alarm test started"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitor/camera_test')
def test_camera():
    """Test camera availability"""
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return jsonify({
                    "available": True,
                    "message": "Camera is working"
                })
            else:
                return jsonify({
                    "available": False,
                    "message": "Camera opened but cannot read frames"
                })
        else:
            return jsonify({
                "available": False,
                "message": "Cannot open camera"
            })
    except Exception as e:
        return jsonify({
            "available": False,
            "message": f"Camera test failed: {str(e)}"
        })
