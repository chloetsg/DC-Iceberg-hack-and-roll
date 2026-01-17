// --- Configuration Constants (Matches your Python) ---
const SWAP_THRESHOLD = 0.05;
const RESET_TIME = 1000; // ms
const FLATNESS_TOLERANCE = 0.15; // Adjusted slightly for JS normalized coords

// --- State Variables ---
let lastState = "NEUTRAL";
let cycleCount = 0;
let lastMoveTime = Date.now();
let successTriggerTime = null;
let camera = null;

// --- DOM Elements ---
const videoElement = document.getElementById('inputVideo');
const canvasElement = document.getElementById('outputCanvas');
const canvasCtx = canvasElement.getContext('2d');
const statusText = document.getElementById('statusText');
const gestureContainer = document.getElementById('gestureContainer');

// --- 1. The Validator Function (Translated from Python) ---
function isValidHand(landmarks, label) {
    const idxMcpY = landmarks[5].y;
    const pinkyMcpY = landmarks[17].y;

    // Flatness Check
    if (Math.abs(idxMcpY - pinkyMcpY) > FLATNESS_TOLERANCE) {
        return { valid: false, msg: "Keep Hand Flat!" };
    }

    const thumbTipX = landmarks[4].x;
    const pinkyTipX = landmarks[20].x;

    // Palm Rotation Check
    // Note: JS coords are mirrored if we flip the canvas, but raw data assumes 
    // left/right based on the person's view usually.
    if (label === "Left") {
        if (thumbTipX > pinkyTipX) return { valid: false, msg: "Rotate Palm Up" };
    } else {
        if (thumbTipX < pinkyTipX) return { valid: false, msg: "Rotate Palm Up" };
    }

    return { valid: true, msg: "OK" };
}

// --- 2. The Main Processing Loop ---
function onResults(results) {
    // A. Draw Background
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Draw the video frame (Mirror it for natural feel)
    canvasCtx.translate(canvasElement.width, 0);
    canvasCtx.scale(-1, 1); 
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    
    // B. Success Mode Check
    if (successTriggerTime) {
        // Stop drawing skeleton, just show success message
        canvasCtx.restore(); // Restore to normal orientation for text
        
        canvasCtx.fillStyle = "rgba(0, 255, 0, 0.3)";
        canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        canvasCtx.fillStyle = "green";
        canvasCtx.font = "bold 50px Arial";
        canvasCtx.fillText("67 ACTIVATED!", 100, 240);
        
        // Optional: Stop camera after 3 seconds
        if (Date.now() - successTriggerTime > 3000) {
            camera.stop();
            alert("Congratulations! You passed all stages.");
        }
        return;
    }

    // C. Detection Logic
    let validHandsCount = 0;
    let leftW = null; 
    let rightW = null;

    if (results.multiHandLandmarks && results.multiHandLandmarks.length === 2) {
        
        for (const [index, landmarks] of results.multiHandLandmarks.entries()) {
            // MediaPipe JS provides labels in 'multiHandedness'
            // Be careful: MediaPipe often mirrors Left/Right labels in selfie mode
            const label = results.multiHandedness[index].label; 
            
            const check = isValidHand(landmarks, label);

            if (check.valid) {
                validHandsCount++;
                drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#00FF00', lineWidth: 5});
                
                // Store wrist for logic
                if (label === "Left") leftW = landmarks[0];
                if (label === "Right") rightW = landmarks[0];
                
            } else {
                drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#FF0000', lineWidth: 5});
            }
        }
    }

    canvasCtx.restore(); // Undo the mirroring for text drawing

    // D. Logic Branching
    if (validHandsCount === 2 && leftW && rightW) {
        // Calculate Logic
        const mid = (leftW.y + rightW.y) / 2;
        const lUp = leftW.y < (mid - SWAP_THRESHOLD);
        const rDown = rightW.y > (mid + SWAP_THRESHOLD);
        const rUp = rightW.y < (mid - SWAP_THRESHOLD);
        const lDown = leftW.y > (mid + SWAP_THRESHOLD);

        let curr = "NEUTRAL";
        // Note: Labels might be swapped depending on camera mirror settings. 
        // If logic feels backwards, swap these strings:
        if (lUp && rDown) curr = "LEFT_UP"; 
        if (rUp && lDown) curr = "RIGHT_UP";

        // State Machine
        if (curr !== "NEUTRAL" && curr !== lastState) {
            cycleCount++;
            lastMoveTime = Date.now();
            lastState = curr;
        }

        // Reset Timeout
        if (Date.now() - lastMoveTime > RESET_TIME) {
            cycleCount = 0;
            lastState = "NEUTRAL";
        }

        statusText.innerText = `Reps: ${cycleCount} | Status: Active`;
        statusText.style.color = "gold";

        // Trigger Success
        if (cycleCount >= 2) {
            successTriggerTime = Date.now();
        }

    } else {
        statusText.innerText = "Show 2 Hands Flat & Palms Up!";
        statusText.style.color = "red";
    }
}

// --- 3. Initialization Function ---
function startGestureGame() {
    // Show the container
    gestureContainer.style.display = "block";

    const hands = new Hands({locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    }});

    hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5
    });

    hands.onResults(onResults);

    camera = new Camera(videoElement, {
        onFrame: async () => {
            await hands.send({image: videoElement});
        },
        width: 640,
        height: 480
    });
    
    camera.start();
}

// --- 4. Modify your existing Submit Function ---
async function submitDrawing() {
    // ... existing canvas code ...
    
    // Replace the alert in your previous code with this:
    if (result.status === "SUCCESS") {
        document.getElementById("captchaModal").style.display = "none"; // Hide popup
        startGestureGame(); // START STAGE 3
    } else {
        alert("Try again!");
    }
}