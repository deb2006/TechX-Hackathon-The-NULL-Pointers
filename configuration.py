"""Configuration settings for Proof of Life system"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server
HOST = "0.0.0.0"
PORT = 8000

# Challenge
CHALLENGE_EXPIRY_SECONDS = 120
NONCE_LENGTH = 6

# Liveness thresholds
BLINK_THRESHOLD = 0.21
HEAD_MOVEMENT_THRESHOLD = 0.05
MIN_BLINKS_REQUIRED = 2
MIN_HEAD_MOVEMENTS_REQUIRED = 1

# Emotion
REQUIRED_EMOTIONS = ["happy", "neutral", "surprise"]
EMOTION_CONFIDENCE_THRESHOLD = 0.25

# Voice
VOICE_CONFIDENCE_THRESHOLD = 0.7

# Blockchain
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))

# Token
TOKEN_VALIDITY_SECONDS = 120

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]
