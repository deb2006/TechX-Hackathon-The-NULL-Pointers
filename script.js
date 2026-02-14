// Configuration
const SESSION_ID = Math.random().toString(36).substring(7);

// DOM Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// UI Elements
const stepBlink = document.getElementById('step-blink');
const stepSmile = document.getElementById('step-smile');
const stepVerify = document.getElementById('step-verify');
const cameraBadge = document.getElementById('camera-badge');
const faceStat = document.getElementById('face-stat');
const blinkStat = document.getElementById('blink-stat');
const smileStat = document.getElementById('smile-stat');
const faceGuide = document.getElementById('face-guide');
const faceRing = document.querySelector('.face-ring');
const faceMessage = document.getElementById('face-message');
const promptText = document.getElementById('prompt-text');
const verifyBtn = document.getElementById('verify-btn');
const tokenSection = document.getElementById('token-section');
const tokenValue = document.getElementById('token-value');
const tokenExpiry = document.getElementById('token-expiry');
const copyBtn = document.getElementById('copy-token');
const statusToast = document.getElementById('status-toast');
const toastMessage = document.getElementById('toast-message');
const sessionIdSpan = document.getElementById('session-id');

// State
let faceDetected = false;
let blinkCount = 0;
let blinksCompleted = false;
let smileCompleted = false;
let allCompleted = false;
let isProcessing = false;
let mediaStream = null;

// Set session ID
sessionIdSpan.textContent = SESSION_ID.substring(0, 8);

// Initialize camera
async function initCamera() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: { 
                width: 640, 
                height: 480, 
                frameRate: 30,
                facingMode: 'user'
            }
        });
        video.srcObject = mediaStream;
        
        await video.play();
        
        canvas.width = 320;
        canvas.height = 240;
        
        cameraBadge.textContent = 'Active';
        cameraBadge.style.background = '#34c759';
        
        showToast('Camera ready', 'success');
        startDetection();
    } catch (err) {
        cameraBadge.textContent = 'Error';
        cameraBadge.style.background = '#ff3b30';
        showToast('Unable to access camera', 'error');
        console.error(err);
    }
}

// Start frame capture
function startDetection() {
    setInterval(async () => {
        if (video.readyState === video.HAVE_ENOUGH_DATA && !isProcessing) {
            isProcessing = true;
            
            // Draw to canvas
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/jpeg', 0.7);
            
            try {
                // Try local backend first
                const response = await fetch('/api/check-frame', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        image: imageData,
                        session_id: SESSION_ID
                    })
                });
                
                const data = await response.json();
                updateUI(data.result, data.status);
                
            } catch (err) {
                console.log('Using Colab fallback');
                // Fallback to Colab
                try {
                    const response = await fetch('https://your-ngrok-url.ngrok-free.app/detect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            image: imageData,
                            session_id: SESSION_ID
                        })
                    });
                    
                    const data = await response.json();
                    updateUI(data, { 
                        blink_count: data.blink_count,
                        blinks_completed: data.blink_count >= 2,
                        smile_completed: data.smile_detected,
                        all_completed: data.blink_count >= 2 && data.smile_detected
                    });
                    
                } catch (colabErr) {
                    console.error('Colab error:', colabErr);
                }
            }
            
            isProcessing = false;
        }
    }, 200);
}

// Update UI
function updateUI(result, status) {
    // Face detection
    faceDetected = result.face_detected || false;
    
    if (faceDetected) {
        faceStat.innerHTML = '<span class="stat-dot"></span> Face detected';
        faceRing.classList.add('active');
        faceMessage.textContent = 'Face detected';
        faceGuide.style.opacity = '0.5';
    } else {
        faceStat.innerHTML = '<span class="stat-dot inactive"></span> No face';
        faceRing.classList.remove('active');
        faceMessage.textContent = 'Position your face here';
        faceGuide.style.opacity = '1';
    }
    
    // Blink count
    blinkCount = status.blink_count || 0;
    blinkStat.innerHTML = `<span class="stat-icon">👁️</span> ${blinkCount}/2`;
    
    blinksCompleted = status.blinks_completed || false;
    if (blinksCompleted) {
        stepBlink.setAttribute('data-completed', 'true');
    }
    
    // Smile detection
    smileCompleted = status.smile_completed || false;
    smileStat.innerHTML = `<span class="stat-icon">😊</span> ${smileCompleted ? '✓' : '—'}`;
    
    if (smileCompleted) {
        stepSmile.setAttribute('data-completed', 'true');
    }
    
    // All completed
    allCompleted = status.all_completed || false;
    
    // Update prompt text
    if (!faceDetected) {
        promptText.textContent = 'Position your face in the frame';
    } else if (!blinksCompleted) {
        const remaining = 2 - blinkCount;
        promptText.textContent = `Blink ${remaining} more time${remaining === 1 ? '' : 's'}`;
    } else if (!smileCompleted) {
        promptText.textContent = 'Show us your smile';
    } else if (allCompleted) {
        promptText.textContent = 'All checks passed! Ready to verify';
        stepVerify.setAttribute('data-completed', 'true');
        verifyBtn.disabled = false;
        showToast('Liveness check complete!', 'success');
    }
}

// Verify
async function verify() {
    verifyBtn.disabled = true;
    verifyBtn.querySelector('.btn-text').textContent = 'Generating token...';
    
    try {
        const response = await fetch('/api/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: SESSION_ID })
        });
        
        const data = await response.json();
        
        if (data.verified && data.token) {
            tokenValue.textContent = data.token;
            tokenExpiry.textContent = `Generated at ${new Date().toLocaleTimeString()} · Valid for 5 minutes`;
            tokenSection.style.display = 'block';
            
            verifyBtn.querySelector('.btn-text').textContent = 'Token Generated';
            verifyBtn.style.background = '#34c759';
            
            showToast('Verification successful!', 'success');
        } else {
            verifyBtn.disabled = false;
            verifyBtn.querySelector('.btn-text').textContent = 'Generate Proof-of-Life Token';
            showToast(data.message || 'Verification failed', 'error');
        }
    } catch (err) {
        verifyBtn.disabled = false;
        verifyBtn.querySelector('.btn-text').textContent = 'Generate Proof-of-Life Token';
        showToast('Connection error', 'error');
        console.error(err);
    }
}

// Copy token
copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(tokenValue.textContent);
    copyBtn.innerHTML = '<span>Copied!</span>';
    setTimeout(() => {
        copyBtn.innerHTML = '<span>Copy</span>';
    }, 2000);
});

// Show toast
function showToast(message, type = 'info') {
    toastMessage.textContent = message;
    
    if (type === 'success') {
        statusToast.style.background = 'rgba(52, 199, 89, 0.9)';
    } else if (type === 'error') {
        statusToast.style.background = 'rgba(255, 59, 48, 0.9)';
    } else {
        statusToast.style.background = 'rgba(29, 28, 30, 0.9)';
    }
    
    statusToast.style.display = 'flex';
    
    setTimeout(() => {
        statusToast.style.display = 'none';
    }, 3000);
}

// Cleanup
function cleanup() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
}

// Event listeners
verifyBtn.addEventListener('click', verify);
window.addEventListener('beforeunload', cleanup);

// Initialize
initCamera();