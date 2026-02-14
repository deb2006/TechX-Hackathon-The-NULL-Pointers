import secrets
import string
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
import config

class ChallengeManager:
    def __init__(self):
        self.challenges: Dict[str, Dict] = {}
    
    def generate_nonce(self) -> str:
        """Generate random nonce word"""
        words = [
            "phoenix", "crystal", "thunder", "shadow", "prism",
            "quantum", "nebula", "cipher", "zenith", "echo",
            "matrix", "pulse", "vertex", "axiom", "nexus"
        ]
        return random.choice(words)
    
    def generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def create_challenge(self) -> Dict:
        """Create new verification challenge"""
        challenge_id = self.generate_challenge_id()
        nonce = self.generate_nonce()
        required_emotion = random.choice(config.REQUIRED_EMOTIONS)
        
        challenge = {
            "challenge_id": challenge_id,
            "nonce": nonce,
            "required_emotion": required_emotion,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=config.CHALLENGE_EXPIRY_SECONDS),
            "status": "pending",
            "verifications": {
                "liveness": False,
                "emotion": False,
                "voice": False
            }
        }
        
        self.challenges[challenge_id] = challenge
        return challenge
    
    def get_challenge(self, challenge_id: str) -> Optional[Dict]:
        """Retrieve challenge by ID"""
        return self.challenges.get(challenge_id)
    
    def update_verification(self, challenge_id: str, verification_type: str, status: bool):
        """Update verification status"""
        if challenge_id in self.challenges:
            self.challenges[challenge_id]["verifications"][verification_type] = status
            
            # Check if all verifications passed
            verifications = self.challenges[challenge_id]["verifications"]
            if all(verifications.values()):
                self.challenges[challenge_id]["status"] = "verified"
    
    def is_expired(self, challenge_id: str) -> bool:
        """Check if challenge expired"""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return True
        return datetime.utcnow() > challenge["expires_at"]
    
    def cleanup_expired(self):
        """Remove expired challenges"""
        expired = [cid for cid, c in self.challenges.items() if self.is_expired(cid)]
        for cid in expired:
            del self.challenges[cid]

challenge_manager = ChallengeManager()
