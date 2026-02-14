from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
import json
from datetime import datetime
import asyncio

import config
from challenge import challenge_manager
from liveness import LivenessDetector
from emotion import EmotionDetector
from voice import VoiceVerifier
from blockchain import blockchain_manager

app = FastAPI(title="Proof of Life API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global detector instances per connection
detectors = {}

@app.get("/")
async def root():
    return {"status": "Proof of Life API", "version": "1.0.0"}

@app.get("/challenge")
async def create_challenge():
    """Generate new verification challenge"""
    challenge = challenge_manager.create_challenge()
    
    return {
        "challenge_id": challenge["challenge_id"],
        "nonce": challenge["nonce"],
        "required_emotion": challenge["required_emotion"],
        "expires_at": challenge["expires_at"].isoformat(),
        "validity_seconds": config.CHALLENGE_EXPIRY_SECONDS
    }

@app.get("/challenge/{challenge_id}")
async def get_challenge_status(challenge_id: str):
    """Get challenge verification status"""
    challenge = challenge_manager.get_challenge(challenge_id)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge_manager.is_expired(challenge_id):
        raise HTTPException(status_code=410, detail="Challenge expired")
    
    return {
        "challenge_id": challenge_id,
        "status": challenge["status"],
        "verifications": challenge["verifications"],
        "expires_at": challenge["expires_at"].isoformat()
    }

@app.post("/verify/voice/{challenge_id}")
async def verify_voice(challenge_id: str, audio: UploadFile = File(...)):
    """Verify voice nonce"""
    challenge = challenge_manager.get_challenge(challenge_id)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge_manager.is_expired(challenge_id):
        raise HTTPException(status_code=410, detail="Challenge expired")
    
    # Read audio data
    audio_data = await audio.read()
    
    # Verify voice
    verifier = VoiceVerifier()
    result = verifier.verify_nonce(audio_data, challenge["nonce"])
    
    # Update challenge
    challenge_manager.update_verification(challenge_id, "voice", result["voice_verified"])
    
    return result

@app.post("/mint/{challenge_id}")
async def mint_token(challenge_id: str, user_address: str):
    """Mint blockchain access token"""
    challenge = challenge_manager.get_challenge(challenge_id)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge["status"] != "verified":
        raise HTTPException(status_code=400, detail="Challenge not fully verified")
    
    # Mint token
    token_result = blockchain_manager.mint_access_token(user_address)
    
    return token_result

@app.websocket("/ws/verify/{challenge_id}")
async def websocket_verify(websocket: WebSocket, challenge_id: str):
    """WebSocket endpoint for real-time verification"""
    await websocket.accept()
    
    challenge = challenge_manager.get_challenge(challenge_id)
    if not challenge:
        await websocket.send_json({"error": "Challenge not found"})
        await websocket.close()
        return
    
    # Initialize detectors for this session
    liveness_detector = LivenessDetector()
    emotion_detector = EmotionDetector()
    
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_json()
            
            if data.get("type") == "frame":
                # Decode base64 frame
                frame_data = base64.b64decode(data["frame"].split(",")[1])
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Verify liveness
                liveness_result = liveness_detector.verify_liveness(frame)
                
                # Verify emotion
                emotion_result = emotion_detector.verify_emotion(frame, challenge["required_emotion"])
                
                # Update challenge verifications
                if liveness_result["liveness_verified"]:
                    challenge_manager.update_verification(challenge_id, "liveness", True)
                
                if emotion_result["emotion_verified"]:
                    challenge_manager.update_verification(challenge_id, "emotion", True)
                
                # Send status update
                updated_challenge = challenge_manager.get_challenge(challenge_id)
                
                response = {
                    "type": "verification_update",
                    "liveness": liveness_result,
                    "emotion": emotion_result,
                    "verifications": updated_challenge["verifications"],
                    "status": updated_challenge["status"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_json(response)
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for challenge {challenge_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        # Cleanup
        liveness_detector.reset()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
