import speech_recognition as sr
import io
from typing import Dict, Optional
import config

class VoiceVerifier:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio to text"""
        try:
            # Convert bytes to AudioData
            audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2)
            
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text.lower()
        
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def verify_nonce(self, audio_data: bytes, expected_nonce: str) -> Dict:
        """Verify spoken nonce word"""
        transcribed = self.transcribe_audio(audio_data)
        
        response = {
            "transcribed_text": transcribed,
            "expected_nonce": expected_nonce,
            "voice_verified": False
        }
        
        if transcribed:
            # Check if nonce word is in transcribed text
            if expected_nonce.lower() in transcribed:
                response["voice_verified"] = True
        
        return response
