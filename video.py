import cv2
import mediapipe as mp
import time

def perform_67():
    # --- Configuration ---
    SWAP_THRESHOLD = 0.05
    RESET_TIME = 1.0
    SUCCESS_DISPLAY_DURATION = 3.0  # Seconds to keep showing text after success

    # --- Validation Thresholds ---
    FLATNESS_TOLERANCE = 1

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

    # State Variables
    last_state = "NEUTRAL"
    cycle_count = 0
    last_move_time = time.time()
    success_trigger_time = None  # ### NEW: Tracks when success happened

    # --- Validator Function ---
    def is_valid_hand(landmarks, label):
        # (Same as your existing function)
        idx_mcp_y = landmarks.landmark[5].y
        pinky_mcp_y = landmarks.landmark[17].y
        
        if abs(idx_mcp_y - pinky_mcp_y) > FLATNESS_TOLERANCE:
            return False, "Keep Hand Flat!"

        thumb_tip_x = landmarks.landmark[4].x
        pinky_tip_x = landmarks.landmark[20].x
        
        if label == "Left":
            if thumb_tip_x > pinky_tip_x: 
                return False, "Rotate Palm Up"
        else:
            if thumb_tip_x < pinky_tip_x:
                return False, "Rotate Palm Up"
        return True, "OK"

    # --- Main Loop ---
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success: continue

        image = cv2.flip(image, 1)
        H, W, _ = image.shape
        
        # ### NEW: Logic Branching
        # If we already succeeded, just show the success screen and count down
        if success_trigger_time is not None:
            elapsed = time.time() - success_trigger_time
            
            # 1. Check if time is up
            if elapsed > SUCCESS_DISPLAY_DURATION:
                print("Finished Success Display. Exiting...")
                break
            
            # 2. If not up, just display the static success text
            remaining = int(SUCCESS_DISPLAY_DURATION - elapsed) + 1
            cv2.putText(image, "67 ACTIVATED!", (50, H // 2), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 5)
            cv2.putText(image, f"Closing in {remaining}...", (50, H // 2 + 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Flat Hand Detector', image)
            if cv2.waitKey(5) & 0xFF == 27: break
            continue # Skip the rest of the loop (detection logic)

        # --- NORMAL DETECTION LOGIC (Only runs if success_trigger_time is None) ---
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        status_text = "Show 2 Hands"
        status_color = (100, 100, 100)
        
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            valid_hands_count = 0
            
            for idx, hl in enumerate(results.multi_hand_landmarks):
                lbl = results.multi_handedness[idx].classification[0].label
                is_good, msg = is_valid_hand(hl, lbl)
                
                if is_good:
                    valid_hands_count += 1
                    mp_drawing.draw_landmarks(image, hl, mp_hands.HAND_CONNECTIONS)
                else:
                    color = (0, 0, 255)
                    wrist = hl.landmark[0]
                    cx, cy = int(wrist.x * W), int(wrist.y * H)
                    cv2.putText(image, msg, (cx - 40, cy + 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    mp_drawing.draw_landmarks(image, hl, mp_hands.HAND_CONNECTIONS, 
                                            mp_drawing.DrawingSpec(color=color))

            if valid_hands_count == 2:
                left_w, right_w = None, None
                for idx, hl in enumerate(results.multi_hand_landmarks):
                    lbl = results.multi_handedness[idx].classification[0].label
                    if lbl == "Left": left_w = hl.landmark[0]
                    else: right_w = hl.landmark[0]
                
                if left_w and right_w:
                    mid = (left_w.y + right_w.y) / 2
                    l_up = left_w.y < (mid - SWAP_THRESHOLD)
                    r_up = right_w.y < (mid - SWAP_THRESHOLD)
                    l_down = left_w.y > (mid + SWAP_THRESHOLD)
                    r_down = right_w.y > (mid + SWAP_THRESHOLD)

                    curr = "NEUTRAL"
                    if l_up and r_down: curr = "LEFT_UP"
                    elif r_up and l_down: curr = "RIGHT_UP"

                    if curr != "NEUTRAL" and curr != last_state:
                        cycle_count += 1
                        last_move_time = time.time()
                        last_state = curr

                    if time.time() - last_move_time > RESET_TIME:
                        cycle_count = 0
                        last_state = "NEUTRAL"

                    status_text = f"Reps: {cycle_count}"
                    status_color = (255, 255, 0)
                    
                    # ### NEW: Trigger Success Mode
                    if cycle_count >= 2:
                        success_trigger_time = time.time() # Start the timer
                        print("67 DETECTED - Starting Cooldown")
                        # No break here! The next loop iteration will catch the success_trigger_time
            else:
                status_text = "Fix Hand Position!"
                status_color = (0, 0, 255)

        cv2.putText(image, status_text, (20, 60), cv2.FONT_HERSHEY_PLAIN, 1.5, status_color, 3)
        cv2.imshow('Flat Hand Detector', image)
        if cv2.waitKey(5) & 0xFF == 27: break

    cap.release()
    cv2.destroyAllWindows()

    return True