import cv2
import numpy as np
import mediapipe as mp
import base64
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# --- Optional: Keep your existing imports if you have these files ---
# from captcha_generator import generate_captcha
# from reco_main import validate_writing

app = FastAPI()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- The Gesture Detector Class ---
class HandGestureDetector:
    def __init__(self):
        # Configuration
        self.SWAP_THRESHOLD = 0.05
        self.RESET_TIME = 1.0
        self.FLATNESS_TOLERANCE = 0.08  # Slightly relaxed for better usability
        
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # State Variables
        self.last_state = "NEUTRAL"
        self.cycle_count = 0
        self.last_move_time = time.time()
        self.success = False
        self.success_trigger_time = None # For cooldown logic

    def close(self):
        """Clean up MediaPipe resources"""
        self.hands.close()
    
    def is_valid_hand(self, landmarks, label):
        """Check if hand is flat and palm is facing up"""
        # 1. Flatness Check (Index vs Pinky Knuckle Y-coord)
        idx_mcp_y = landmarks.landmark[5].y
        pinky_mcp_y = landmarks.landmark[17].y
        
        if abs(idx_mcp_y - pinky_mcp_y) > self.FLATNESS_TOLERANCE:
            return False, "Keep Hand Flat!"

        # 2. Palm Up Check (Thumb vs Pinky X-coord)
        thumb_tip_x = landmarks.landmark[4].x
        pinky_tip_x = landmarks.landmark[20].x
        
        # Logic assumes MIRRORED image (Selfie mode)
        # Left Hand on Screen (Physical Left): Thumb (4) > Pinky (20)
        if label == "Left":
            if thumb_tip_x > pinky_tip_x: 
                return False, "Rotate Palm Up"
        # Right Hand on Screen (Physical Right): Thumb (4) < Pinky (20)
        else:
            if thumb_tip_x < pinky_tip_x:
                return False, "Rotate Palm Up"
        
        return True, "OK"
    
    def process_frame(self, frame):
        """Process a single frame and return detection results"""
        
        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        
        # Default Status
        status = {
            "text": "Show 2 Hands",
            "color": "gray",
            "cycle_count": self.cycle_count,
            "success": self.success,
            "hands": []
        }
        
        # If success was already triggered, just return success state (Cooldown)
        if self.success:
            status['text'] = "67 ACTIVATED!"
            status['color'] = "green"
            return status

        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            valid_hands_count = 0
            hands_info = []
            
            # 1. Validate Individual Hands
            for idx, hl in enumerate(results.multi_hand_landmarks):
                label = results.multi_handedness[idx].classification[0].label
                is_good, msg = self.is_valid_hand(hl, label)
                
                # Store landmarks for frontend drawing
                landmarks_list = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in hl.landmark]
                
                hands_info.append({
                    'label': label,
                    'valid': is_good,
                    'message': msg,
                    'landmarks': landmarks_list
                })
                
                if is_good:
                    valid_hands_count += 1
            
            status['hands'] = hands_info
            
            # 2. Run Seesaw Logic only if both hands are valid
            if valid_hands_count == 2:
                left_w, right_w = None, None
                
                # Identify Left vs Right Wrist
                for idx, hl in enumerate(results.multi_hand_landmarks):
                    lbl = results.multi_handedness[idx].classification[0].label
                    if lbl == "Left": 
                        left_w = hl.landmark[0]
                    else: 
                        right_w = hl.landmark[0]
                
                if left_w and right_w:
                    # Calculate Midpoint
                    mid = (left_w.y + right_w.y) / 2
                    
                    # Determine Positions (Y increases downwards)
                    l_up = left_w.y < (mid - self.SWAP_THRESHOLD)
                    r_up = right_w.y < (mid - self.SWAP_THRESHOLD)
                    l_down = left_w.y > (mid + self.SWAP_THRESHOLD)
                    r_down = right_w.y > (mid + self.SWAP_THRESHOLD)

                    curr = "NEUTRAL"
                    if l_up and r_down: 
                        curr = "LEFT_UP"
                    elif r_up and l_down: 
                        curr = "RIGHT_UP"

                    # Count Cycles (Transitions)
                    if curr != "NEUTRAL" and curr != self.last_state:
                        self.cycle_count += 1
                        self.last_move_time = time.time()
                        self.last_state = curr

                    # Reset if too slow
                    if time.time() - self.last_move_time > self.RESET_TIME:
                        self.cycle_count = 0
                        self.last_state = "NEUTRAL"

                    # Update Status
                    status['text'] = f"Reps: {self.cycle_count}"
                    status['color'] = "yellow"
                    status['cycle_count'] = self.cycle_count
                    
                    # Check for Win Condition
                    if self.cycle_count >= 6: # Set to 6 transitions (3 full cycles)
                        self.success = True
                        status['success'] = True
                        status['text'] = "67 ACTIVATED!"
                        status['color'] = "green"
            else:
                status['text'] = "Fix Hand Position!"
                status['color'] = "red"
        
        return status

# --- WebSocket Endpoint ---
@app.websocket("/ws/hand-gesture")
async def hand_gesture_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Client Connected")
    
    # Initialize detector for this specific connection
    detector = HandGestureDetector()
    
    try:
        while True:
            # 1. Receive data
            data = await websocket.receive_text()
            
            try:
                # 2. Parse JSON
                frame_data = json.loads(data)
                
                # Expecting format: {"frame": "data:image/jpeg;base64,/9j/4AAQ..."}
                img_data_str = frame_data.get('frame')
                
                if not img_data_str:
                    continue

                # 3. Decode Base64
                # Split off the metadata header (data:image/jpeg;base64,)
                if ',' in img_data_str:
                    header, encoded = img_data_str.split(',', 1)
                else:
                    encoded = img_data_str

                img_bytes = base64.b64decode(encoded)
                nparr = np.frombuffer(img_bytes, np.uint8)
                
                # 4. Decode Image (Crucial Safety Check)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    print("Warning: Failed to decode frame image")
                    await websocket.send_json({"error": "Invalid image data"})
                    continue
                
                # 5. Process
                result = detector.process_frame(frame)
                
                # 6. Send Response
                await websocket.send_json(result)
                
            except json.JSONDecodeError:
                print("Error: Invalid JSON received")
            except Exception as e:
                print(f"Frame processing error: {e}")
                
    except WebSocketDisconnect:
        print("Client Disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        # 7. Cleanup Resources
        detector.close()
        print("Detector resources released")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)