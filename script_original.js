let canvas, ctx;
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let sessionId = null;
let cursorTeleportInterval = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    generateNewCaptcha();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('start-btn').addEventListener('click', startDrawing);
    document.getElementById('clear-btn').addEventListener('click', clearCanvas);
    document.getElementById('submit-btn').addEventListener('click', submitAnswer);
    document.getElementById('modal-close').addEventListener('click', closeModal);
}

function generateNewCaptcha() {
    console.log('Generating new CAPTCHA...');

    fetch('/api/generate-captcha')
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('CAPTCHA data received:', data);
            if (data.success) {
                sessionId = data.session_id;
                const imgElement = document.getElementById('captcha-image');
                imgElement.src = data.captcha_image;
                imgElement.style.display = 'block';
                console.log('CAPTCHA generated successfully:', data.captcha_text);
            } else {
                console.error('CAPTCHA generation failed:', data.error);
                showModal('Error', 'Failed to generate CAPTCHA: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error generating CAPTCHA:', error);
            showModal('Error', 'Failed to connect to server: ' + error.message);
        });
}

function startDrawing() {
    // Hide captcha screen, show canvas screen
    document.getElementById('captcha-screen').style.display = 'none';
    document.getElementById('canvas-screen').style.display = 'block';

    // Copy captcha to reference
    const captchaImg = document.getElementById('captcha-image').src;
    document.getElementById('captcha-reference').src = captchaImg;

    // Setup canvas
    canvas = document.getElementById('drawing-canvas');
    ctx = canvas.getContext('2d');

    // Configure drawing settings
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Add mouse event listeners
    canvas.addEventListener('mousedown', startDraw);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDraw);
    canvas.addEventListener('mouseleave', stopDraw);

    // Add touch event listeners for mobile
    canvas.addEventListener('touchstart', handleTouch);
    canvas.addEventListener('touchmove', handleTouch);
    canvas.addEventListener('touchend', stopDraw);

    // Start cursor teleport effect
    startCursorTeleport();
}

function startDraw(e) {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    lastX = e.clientX - rect.left;
    lastY = e.clientY - rect.top;
}

function draw(e) {
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(currentX, currentY);
    ctx.stroke();

    lastX = currentX;
    lastY = currentY;
}

function stopDraw() {
    isDrawing = false;
}

function handleTouch(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 'mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function startCursorTeleport() {
    // Simulate cursor teleport effect (web version)
    // In the desktop version, this runs an executable
    // Here we can add visual effects or just note it
    console.log('Cursor teleport effect would start here (desktop feature)');

    // Optional: Add a visual indicator
    cursorTeleportInterval = setInterval(() => {
        // Could add visual effects here if needed
    }, 6000); // 5-8 seconds average
}

function stopCursorTeleport() {
    if (cursorTeleportInterval) {
        clearInterval(cursorTeleportInterval);
        cursorTeleportInterval = null;
    }
}

function submitAnswer() {
    // Stop cursor effect
    stopCursorTeleport();

    // Get canvas image data
    const drawingData = canvas.toDataURL('image/png');

    // Show loading modal
    showModal('Validating...', 'Please wait while we validate your handwriting.');

    // Send to server for validation
    fetch('/api/validate-captcha', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            drawing: drawingData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.validated) {
                showModal('Success!', 'CAPTCHA Passed! Now complete the 67 hand gesture challenge.', () => {
                    // Move to video screen for 67 challenge
                    startVideoChallenge();
                });
            } else {
                showModal('Failed', `Validation failed. Expected: '${data.expected}'. Please try again!`, () => {
                    // Clear canvas and restart cursor effect
                    clearCanvas();
                    startCursorTeleport();
                    closeModal();
                });
            }
        } else {
            showModal('Error', 'Validation error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showModal('Error', 'Failed to validate. Please try again.');
    });
}

function resetToStart() {
    // Reset canvas
    if (canvas) {
        clearCanvas();
    }

    // Show captcha screen, hide canvas screen
    document.getElementById('captcha-screen').style.display = 'block';
    document.getElementById('canvas-screen').style.display = 'none';

    // Generate new CAPTCHA
    generateNewCaptcha();

    closeModal();
}

function showModal(title, message, callback) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').textContent = message;
    document.getElementById('modal').style.display = 'flex';

    // Store callback for when modal is closed
    document.getElementById('modal').dataset.callback = callback ? callback.toString() : '';
}

function closeModal() {
    const modal = document.getElementById('modal');
    const callbackStr = modal.dataset.callback;

    modal.style.display = 'none';

    // Execute callback if exists
    if (callbackStr) {
        try {
            const callback = eval('(' + callbackStr + ')');
            if (typeof callback === 'function') {
                callback();
            }
        } catch (e) {
            console.error('Callback error:', e);
        }
    }
}

// ==================== VIDEO CHALLENGE (67 HAND GESTURE) ====================
// Using Python backend for hand detection

let videoStream = null;
let detectionInterval = null;
let videoElement = null;
let canvasElement = null;

function startVideoChallenge() {
    console.log('=== STARTING VIDEO CHALLENGE (Python Backend) ===');

    // Hide canvas screen, show video screen
    document.getElementById('canvas-screen').style.display = 'none';
    document.getElementById('video-screen').style.display = 'block';

    closeModal();

    console.log('Initializing Python-based hand detection...');
    initializeHandDetection();
}

async function initializeHandDetection() {
    console.log('Initializing Python-based hand detection...');

    videoElement = document.getElementById('video-feed');
    canvasElement = document.getElementById('video-canvas');

    try {
        // Start hand detection session on server
        console.log('Starting hand detection session on server...');
        const startResponse = await fetch('/api/start-hand-detection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const startData = await startResponse.json();
        if (!startData.success) {
            throw new Error(startData.error);
        }

        console.log('Server-side hand detection started');

        // Request camera access
        console.log('Requesting camera access...');
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: 640,
                height: 480,
                facingMode: 'user'
            }
        });

        console.log('Camera access granted');
        videoStream = stream;
        videoElement.srcObject = stream;

        // Wait for video to be ready
        await new Promise((resolve) => {
            videoElement.onloadedmetadata = () => {
                videoElement.play();
                console.log('Video playing');
                resolve();
            };
        });

        // Create a hidden canvas to capture frames
        const captureCanvas = document.createElement('canvas');
        captureCanvas.width = 640;
        captureCanvas.height = 480;
        const captureCtx = captureCanvas.getContext('2d');

        // Start sending frames to Python backend
        console.log('Starting frame processing loop...');
        detectionInterval = setInterval(async () => {
            try {
                // Capture current video frame
                captureCtx.drawImage(videoElement, 0, 0, 640, 480);
                const frameData = captureCanvas.toDataURL('image/jpeg', 0.8);

                // Send to Python backend
                const response = await fetch('/api/process-hand-frame', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        frame: frameData
                    })
                });

                const data = await response.json();
                if (data.success) {
                    updateHandDetectionUI(data.result);
                } else {
                    console.error('Frame processing error:', data.error);
                }
            } catch (err) {
                console.error('Error in frame processing loop:', err);
            }
        }, 100); // Process 10 frames per second

        console.log('Hand detection fully initialized!');

    } catch (err) {
        console.error('Initialization error:', err);
        showModal('Error', `Failed to initialize: ${err.message}. Please check camera permissions and refresh.`);
    }
}

function updateHandDetectionUI(result) {
    // Update UI based on Python backend results
    const statusElement = document.getElementById('gesture-status');
    const repCountElement = document.getElementById('rep-count');

    // Handle completion
    if (result.completed) {
        console.log('67 ACTIVATED! Challenge complete.');
        completeChallenge();
        return;
    }

    // Handle countdown mode
    if (result.countdown !== undefined) {
        statusElement.innerHTML = '<span class="success-message">' + result.status + '</span>';
        repCountElement.textContent = `Closing in ${result.countdown}...`;
        repCountElement.style.color = '#00ff00';
        return;
    }

    // Normal status update
    statusElement.textContent = result.status;
    repCountElement.textContent = `Reps: ${result.cycle_count}`;

    // Set colors based on status
    const colorMap = {
        'gray': '#888888',
        'yellow': '#ffff00',
        'red': '#ff0000',
        'green': '#00ff00',
        'orange': '#ffaa00'
    };
    statusElement.style.color = colorMap[result.color] || '#888888';
    repCountElement.style.color = '#667eea';

    // Log progress occasionally
    if (result.cycle_count > 0 && Math.random() < 0.2) {
        console.log(`Hand detection: ${result.status}, Reps: ${result.cycle_count}`);
    }
}

async function completeChallenge() {
    // Stop detection interval
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }

    // Stop camera stream
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }

    // Stop server-side detection
    try {
        await fetch('/api/stop-hand-detection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
    } catch (err) {
        console.error('Error stopping hand detection:', err);
    }

    showModal('Success!', '67 Challenge Complete! You passed all tests!', () => {
        resetToStart();
    });
}
