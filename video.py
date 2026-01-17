import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time


# --- Configuration ---
Identify_Action = "67676767676767676767676767"
FLAG = False
HISTORY_LENGTH = 30  # How many frames to keep for calculating average position (approx 1 sec at 30fps)
MOVEMENT_THRESHOLD = 0.03 # Normalized height (0.0-1.0). How far they must move from center to count as a bob.
DEBOUNCE_SECONDS = 1.5  # Time to wait after detection before detecting again

# --- Initialization ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Use models optimized for accuracy since we need precise multi-hand tracking
hands = mp_hands.Hands(
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Motion history buffers
y_history = deque(maxlen=HISTORY_LENGTH)

# State machine flags
went_up = False
went_down = False
last_detection_time = 0

# Helper to get average Y of both wrists
def get_avg_wrist_y(multi_hand_landmarks, multi_handedness):
    wrist_ys = []
    left_hand_present = False
    right_hand_present = False

    for idx, hand_landmarks in enumerate(multi_hand_landmarks):
        # Get handedness label (Left/Right)
        label = multi_handedness[idx].classification[0].label
        
        # Landmark 0 is the wrist
        wrist = hand_landmarks.landmark[0]
        
        # Basic sanity check: Left hand should be on left side of screen (x < 0.5)
        # Remember: Image is mirrored later, so Left hand looks like it's on the Left.
        if label == "Left" and wrist.x < 0.6:
            left_hand_present = True
            wrist_ys.append(wrist.y)
        elif label == "Right" and wrist.x > 0.4:
            right_hand_present = True
            wrist_ys.append(wrist.y)

    # Only proceed if we have one distinct left and one distinct right hand
    if left_hand_present and right_hand_present and len(wrist_ys) == 2:
        return np.mean(wrist_ys)
    return None

# --- Main Loop ---
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    # Flip for selfie mirror view
    image = cv2.flip(image, 1)
    H, W, _ = image.shape
    
    # Convert to RGB for MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    current_status_text = "Searching for 2 hands..."
    status_color = (100, 100, 100) # Grey

    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
        # Draw landmarks
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
        # 1. Get combined Y position of wrists
        avg_y = get_avg_wrist_y(results.multi_hand_landmarks, results.multi_handedness)

        if avg_y is not None:
            current_status_text = "Tracking motion..."
            status_color = (0, 255, 255) # Yellow
            y_history.append(avg_y)

            # Only analyze if we have enough history to establish a baseline
            if len(y_history) == HISTORY_LENGTH:
                # Calculate running average (baseline position)
                baseline_y = np.mean(y_history)
                
                # Remember: Y increases DOWNWARD in screen coordinates.
                # Moving UP means current Y is SMALLER than baseline.
                # Moving DOWN means current Y is LARGER than baseline.

                # Check UP movement
                if avg_y < (baseline_y - MOVEMENT_THRESHOLD):
                    went_up = True
                    # Reset 'down' flag if we go up, to ensure it's a consecutive cycle
                    if not went_down: went_down = False 

                # Check DOWN movement
                elif avg_y > (baseline_y + MOVEMENT_THRESHOLD):
                    went_down = True
                     # Reset 'up' flag if we go down first
                    if not went_up: went_up = False

                # Check for Action Trigger (Up AND Down occurred recently)
                if went_up and went_down:
                    current_time = time.time()
                    # Debounce check to prevent spamming detections
                    if (current_time - last_detection_time) > DEBOUNCE_SECONDS:
                        print(f"\nACTION DETECTED: {Identify_Action}!\n")
                        # Visual Feedback Trigger
                        cv2.rectangle(image, (0, 0), (W, H), (0, 255, 0), 20)
                        last_detection_time = current_time
                        # Reset flags
                        went_up = False
                        went_down = False
                        y_history.clear() # Clear history to restart baseline

                        FLAG = True

                        break

    # Status display
    # Draw baseline region if tracking
    if len(y_history) == HISTORY_LENGTH:
        base_y_pix = int(np.mean(y_history) * H)
        thresh_pix = int(MOVEMENT_THRESHOLD * H)
        # Draw a semi-transparent band showing the "neutral" zone
        overlay = image.copy()
        cv2.rectangle(overlay, (0, base_y_pix - thresh_pix), (W, base_y_pix + thresh_pix), (255, 255, 0), -1)
        cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
        cv2.line(image, (0, base_y_pix), (W, base_y_pix), (255, 0, 0), 2)

    # Show Trigger Status if recently detected
    if (time.time() - last_detection_time) < 1.0:
         cv2.putText(image, Identify_Action, (50, H // 2), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 5)
    else:
         cv2.putText(image, current_status_text, (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)


    cv2.imshow('Meme Gesture Detector', image)
    if cv2.waitKey(5) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()
print("DONE!!!")