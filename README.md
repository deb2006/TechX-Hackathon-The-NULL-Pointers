🛡️ Proof of Life — Real-Time Human Liveness Detection System
"Proof of life in a synthetic world."
As deepfakes become indistinguishable from reality, security demands live, human-only verification.

🚀 Overview
Proof of Life is a real-time AI-powered liveness detection system designed to verify that a real human is physically present during authentication.
This system prevents:
Deepfake attacks
Replay video spoofing
Static image authentication bypass
Bot-based identity fraud
It generates a time-bound JWT Proof-of-Life token after successful verification.

🎯 Core Verification Challenges
The system verifies human presence through:

Challenge	Requirement
👁️ Blink Detection	Minimum 2 real blinks
😊 Smile Detection	Detects natural facial smile
👤 Face Presence	Live face must be continuously detected
⏱️ Timeout	Must complete within session time

Only after completing all checks is a 5-minute secure JWT token issued.

🧠 System Architecture
Camera (Browser)
        ↓
Frontend (Vanilla JS)
        ↓
MediaPipe (Google Colab AI Model)
        ↓
FastAPI Backend (Replit)
        ↓
JWT Token Generation

🔹 Frontend
HTML5
CSS3 (Dark Theme UI)
Vanilla JavaScript
WebRTC Camera Access
Real-time UI feedback

🔹 AI Layer
MediaPipe Face Mesh
Facial Landmark Detection
Eye Aspect Ratio (EAR) Blink Logic
Smile Probability Detection

🔹 Backend
FastAPI
JWT Authentication
Token Expiry (5 Minutes)
REST API Validation Endpoint

✨ Features
🌙 Modern dark theme UI
⚡ Real-time facial landmark processing
📊 Live progress tracking
🔐 Secure JWT token generation
⏳ Time-bound authentication session
🧠 Anti-spoof liveness logic
📸 How It Works

User opens the web interface
Camera access is requested
System verifies:
Face presence
2 natural blinks
Smile gesture
Backend validates session
JWT token is issued (valid for 5 minutes)

🛠️ Setup Instructions


1️⃣ Start the AI Model (Google Colab)
Open your MediaPipe Colab notebook
Run all cells
Start ngrok
Copy the generated public HTTPS URL

2️⃣ Update Frontend
In script.js, replace:


js
const COLAB_URL = "YOUR_COLAB_URL_HERE";

With:

js
const COLAB_URL = "https://your-ngrok-url.ngrok.io";

3️⃣ Start Backend (Replit / Local)
If running locally:
bash
pip install fastapi uvicorn python-jose
uvicorn main:app --reload

4️⃣ Launch Frontend
Simply open:
diff
index.html
Allow camera permissions when prompted.

🔐 JWT Token Format
json

{
  "user_id": "verified_human",
  "issued_at": "timestamp",
  "expires_at": "timestamp + 5min",
  "proof_level": "liveness_verified"
}


🧪 Security Considerations
Detects eye closure duration (not image spoof)
Prevents static photo replay
Smile must be dynamic (not printed image)
JWT expires after 5 minutes
Session resets if face disappears

🌍 Real-World Applications
Crypto wallet login
Web3 authentication
Online exam verification
Remote KYC systems
Secure document access
High-security enterprise dashboards

📦 Future Improvements
Head movement challenge (turn left/right)
Voice-based liveness
Multi-modal biometric fusion
Blockchain-based Proof-of-Life registry
Hardware security integration
