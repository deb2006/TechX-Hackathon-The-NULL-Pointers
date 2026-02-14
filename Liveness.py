import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple
import config

class LivenessDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks for blink detection
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # State tracking
        self.blink_count = 0
        self.head_movement_count = 0
        self.previous_nose_position = None
        self.eye_closed_frames = 0
        self.eye_open_frames = 0
        
    def calculate_ear(self, eye_landmarks) -> float:
        """Calculate Eye Aspect Ratio"""
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def detect_blink(self, landmarks) -> bool:
        """Detect eye blink"""
        left_eye_pts = np.array([[landmarks[i].x, landmarks[i].y] for i in self.LEFT_EYE])
        right_eye_pts = np.array([[landmarks[i].x, landmarks[i].y] for i in self.RIGHT_EYE])
        
        left_ear = self.calculate_ear(left_eye_pts)
        right_ear = self.calculate_ear(right_eye_pts)
        
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Blink detection logic
        blink_detected = False
        if avg_ear < config.BLINK_THRESHOLD:
            self.eye_closed_frames += 1
            self.eye_open_frames = 0
        else:
            if self.eye_closed_frames >= 2:  # Eye was closed for at least 2 frames
                blink_detected = True
                self.blink_count += 1
            self.eye_open_frames += 1
            self.eye_closed_frames = 0
        
        return blink_detected
    
    def detect_head_movement(self, landmarks) -> bool:
        """Detect significant head movement"""
        nose_tip = landmarks[1]  # Nose tip landmark
        current_position = np.array([nose_tip.x, nose_tip.y, nose_tip.z])
        
        movement_detected = False
        
        if self.previous_nose_position is not None:
            movement = np.linalg.norm(current_position - self.previous_nose_position)
            
            # Threshold for significant movement
            if movement > 0.05:  # Normalized coordinate space
                movement_detected = True
                self.head_movement_count += 1
        
        self.previous_nose_position = current_position
        return movement_detected
    
    def verify_liveness(self, frame: np.ndarray) -> Dict:
        """Main liveness verification"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        response = {
            "face_detected": False,
            "blink_detected": False,
            "head_movement_detected": False,
            "blink_count": self.blink_count,
            "head_movement_count": self.head_movement_count,
            "liveness_verified": False
        }
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            response["face_detected"] = True
            
            # Detect blink
            blink = self.detect_blink(face_landmarks.landmark)
            response["blink_detected"] = blink
            
            # Detect head movement
            movement = self.detect_head_movement(face_landmarks.landmark)
            response["head_movement_detected"] = movement
            
            # Check if liveness requirements met
            if (self.blink_count >= config.MIN_BLINKS_REQUIRED and 
                self.head_movement_count >= config.MIN_HEAD_MOVEMENTS_REQUIRED):
                response["liveness_verified"] = True
        
        return response
    
    def reset(self):
        """Reset detector state"""
        self.blink_count = 0
        self.head_movement_count = 0
        self.previous_nose_position = None
        self.eye_closed_frames = 0
        self.eye_open_frames = 0
