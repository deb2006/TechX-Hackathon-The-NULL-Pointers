from deepface import DeepFace
import cv2
import numpy as np
from typing import Dict, Optional
import config

class EmotionDetector:
    def __init__(self):
        self.last_emotion = None
        self.emotion_confidence = 0.0
    
    def detect_emotion(self, frame: np.ndarray) -> Dict:
        """Detect emotion from frame"""
        response = {
            "emotion_detected": False,
            "dominant_emotion": None,
            "confidence": 0.0,
            "all_emotions": {}
        }
        
        try:
            # DeepFace emotion analysis
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            if isinstance(result, list):
                result = result[0]
            
            emotions = result.get('emotion', {})
            dominant_emotion = result.get('dominant_emotion', '').lower()
            
            if dominant_emotion:
                confidence = emotions.get(dominant_emotion.capitalize(), 0) / 100.0
                
                response["emotion_detected"] = True
                response["dominant_emotion"] = dominant_emotion
                response["confidence"] = confidence
                response["all_emotions"] = {k.lower(): v/100.0 for k, v in emotions.items()}
                
                self.last_emotion = dominant_emotion
                self.emotion_confidence = confidence
        
        except Exception as e:
            print(f"Emotion detection error: {e}")
        
        return response
    
    def verify_emotion(self, frame: np.ndarray, required_emotion: str) -> Dict:
        """Verify if detected emotion matches required"""
        emotion_result = self.detect_emotion(frame)
        
        verified = False
        if (emotion_result["emotion_detected"] and 
            emotion_result["dominant_emotion"] == required_emotion.lower() and
            emotion_result["confidence"] >= config.EMOTION_CONFIDENCE_THRESHOLD):
            verified = True
        
        return {
            **emotion_result,
            "required_emotion": required_emotion,
            "emotion_verified": verified
        }
