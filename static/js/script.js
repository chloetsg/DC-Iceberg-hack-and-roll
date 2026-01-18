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

let hands;
let videoStream = null;
let lastState = "NEUTRAL";
let cycleCount = 0;
let lastMoveTime = Date.now();
let successTriggerTime = null;

const SWAP_THRESHOLD = 0.05;
const RESET_TIME = 1000; // 1 second
const SUCCESS_DISPLAY_DURATION = 3000; // 3 seconds

function startVideoChallenge() {
    // Hide canvas screen, show video screen
    document.getElementById('canvas-screen').style.display = 'none';
    document.getElementById('video-screen').style.display = 'block';

    closeModal();

    // Initialize MediaPipe Hands
    initializeHandDetection();
}

async function initializeHandDetection() {
    console.log('Initializing hand detection...');

    const videoElement = document.getElementById('video-feed');
    const canvasElement = document.getElementById('video-canvas');
    const canvasCtx = canvasElement.getContext('2d');

    // Set canvas size
    canvasElement.width = 640;
    canvasElement.height = 480;

    // Check if MediaPipe is loaded
    if (typeof Hands === 'undefined') {
        console.error('MediaPipe Hands not loaded!');
        showModal('Error', 'Failed to load hand detection library. Please refresh the page.');
        return;
    }

    // Initialize MediaPipe Hands
    hands = new Hands({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        }
    });

    hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5
    });

    hands.onResults((results) => onHandsResults(results, canvasCtx, canvasElement));

    console.log('Requesting camera access...');

    // Use native browser camera access instead of MediaPipe Camera utility
    try {
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

        // Send frames to MediaPipe Hands
        const sendFrame = async () => {
            if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
                await hands.send({image: videoElement});
            }
            requestAnimationFrame(sendFrame);
        };

        videoElement.onloadedmetadata = () => {
            console.log('Video metadata loaded, starting detection');
            sendFrame();
        };

    } catch (err) {
        console.error('Camera error:', err);
        showModal('Error', `Failed to access camera: ${err.message}. Please allow camera permissions and refresh.`);
    }
}

function onHandsResults(results, canvasCtx, canvasElement) {
    if (!results || !results.image) {
        console.error('No results or image from MediaPipe');
        return;
    }

    // Log hand detection
    if (results.multiHandLandmarks) {
        console.log(`Detected ${results.multiHandLandmarks.length} hand(s)`);
    }

    // If success has been triggered, show countdown
    if (successTriggerTime !== null) {
        const elapsed = Date.now() - successTriggerTime;

        if (elapsed > SUCCESS_DISPLAY_DURATION) {
            console.log('67 ACTIVATED! Challenge complete.');
            completeChallenge();
            return;
        }

        const remaining = Math.floor((SUCCESS_DISPLAY_DURATION - elapsed) / 1000) + 1;

        // Show success message in status display
        document.getElementById('gesture-status').innerHTML = '<span class="success-message">67 ACTIVATED!</span>';
        document.getElementById('rep-count').textContent = `Closing in ${remaining}...`;
        document.getElementById('rep-count').style.color = '#00ff00';

        return;
    }

    // Normal detection logic
    let statusText = 'Show 2 Hands';
    let statusColor = '#888';

    if (results.multiHandLandmarks && results.multiHandLandmarks.length === 2) {
        let validHandsCount = 0;
        const handData = [];

        for (let i = 0; i < results.multiHandLandmarks.length; i++) {
            const landmarks = results.multiHandLandmarks[i];
            const handedness = results.multiHandedness[i].label;

            const isValid = isValidHand(landmarks, handedness);

            if (isValid.valid) {
                validHandsCount++;
                handData.push({
                    label: handedness,
                    wrist: landmarks[0]
                });
            }
        }

        if (validHandsCount === 2) {
            // Both hands valid, check for alternating motion
            let leftWrist = null;
            let rightWrist = null;

            for (const hand of handData) {
                if (hand.label === 'Left') leftWrist = hand.wrist;
                else rightWrist = hand.wrist;
            }

            if (leftWrist && rightWrist) {
                const mid = (leftWrist.y + rightWrist.y) / 2;
                const leftUp = leftWrist.y < (mid - SWAP_THRESHOLD);
                const rightUp = rightWrist.y < (mid - SWAP_THRESHOLD);
                const leftDown = leftWrist.y > (mid + SWAP_THRESHOLD);
                const rightDown = rightWrist.y > (mid + SWAP_THRESHOLD);

                let currentState = "NEUTRAL";
                if (leftUp && rightDown) currentState = "LEFT_UP";
                else if (rightUp && leftDown) currentState = "RIGHT_UP";

                if (currentState !== "NEUTRAL" && currentState !== lastState) {
                    cycleCount++;
                    lastMoveTime = Date.now();
                    lastState = currentState;
                }

                if (Date.now() - lastMoveTime > RESET_TIME) {
                    cycleCount = 0;
                    lastState = "NEUTRAL";
                }

                statusText = `Reps: ${cycleCount}`;
                statusColor = '#ffff00';

                if (cycleCount >= 2) {
                    successTriggerTime = Date.now();
                    console.log('67 DETECTED - Starting Cooldown');
                }
            }
        } else {
            statusText = 'Fix Hand Position!';
            statusColor = '#ff0000';
        }
    }

    // Update status display
    document.getElementById('gesture-status').textContent = statusText;
    document.getElementById('gesture-status').style.color = statusColor;
    document.getElementById('rep-count').textContent = `Reps: ${cycleCount}`;
    document.getElementById('rep-count').style.color = '#667eea';
}

function isValidHand(landmarks, label) {
    const FLATNESS_TOLERANCE = 0.1;

    // Check if hand is flat (index MCP and pinky MCP should be at similar y)
    const idxMcpY = landmarks[5].y;
    const pinkyMcpY = landmarks[17].y;

    if (Math.abs(idxMcpY - pinkyMcpY) > FLATNESS_TOLERANCE) {
        return {valid: false, message: 'Keep Hand Flat!'};
    }

    // Check palm orientation (thumb and pinky tip positions)
    const thumbTipX = landmarks[4].x;
    const pinkyTipX = landmarks[20].x;

    if (label === 'Left') {
        if (thumbTipX > pinkyTipX) {
            return {valid: false, message: 'Rotate Palm Up'};
        }
    } else {
        if (thumbTipX < pinkyTipX) {
            return {valid: false, message: 'Rotate Palm Up'};
        }
    }

    return {valid: true, message: 'OK'};
}

function completeChallenge() {
    // Stop camera stream
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }

    showModal('Success!', '67 Challenge Complete! You passed all tests!', () => {
        resetToStart();
    });
}

// MediaPipe drawing utilities
const HAND_CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [0, 9], [9, 10], [10, 11], [11, 12],
    [0, 13], [13, 14], [14, 15], [15, 16],
    [0, 17], [17, 18], [18, 19], [19, 20],
    [5, 9], [9, 13], [13, 17]
];

function drawConnectors(ctx, landmarks, connections, style) {
    ctx.strokeStyle = style.color;
    ctx.lineWidth = style.lineWidth;

    for (const connection of connections) {
        const start = landmarks[connection[0]];
        const end = landmarks[connection[1]];

        ctx.beginPath();
        ctx.moveTo(start.x * ctx.canvas.width, start.y * ctx.canvas.height);
        ctx.lineTo(end.x * ctx.canvas.width, end.y * ctx.canvas.height);
        ctx.stroke();
    }
}

function drawLandmarks(ctx, landmarks, style) {
    ctx.fillStyle = style.color;

    for (const landmark of landmarks) {
        ctx.beginPath();
        ctx.arc(
            landmark.x * ctx.canvas.width,
            landmark.y * ctx.canvas.height,
            style.radius,
            0,
            2 * Math.PI
        );
        ctx.fill();
    }
}
