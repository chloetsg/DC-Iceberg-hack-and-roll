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
    fetch('/api/generate-captcha')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                sessionId = data.session_id;
                document.getElementById('captcha-image').src = data.captcha_image;
                console.log('CAPTCHA generated:', data.captcha_text);
            } else {
                showModal('Error', 'Failed to generate CAPTCHA: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal('Error', 'Failed to connect to server');
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
                showModal('Success!', 'CAPTCHA Passed! Click OK to try another one.', () => {
                    // Generate new CAPTCHA and reset
                    resetToStart();
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
