"""
Web-compatible version of video.py that streams hand detection results
"""
import cv2
import mediapipe as mp
import time
import base64
import json
from threading import Thread, Event
import numpy as np

class HandGestureDetector:
    def __init__(self):
        # Configuration
        self.SWAP_THRESHOLD = 0.05
        self.RESET_TIME = 1.0
        self.SUCCESS_DISPLAY_DURATION = 3.0
        self.FLATNESS_TOLERANCE = 0.15  # Normalized for web coords

        # MediaPipe setup
        try:
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
        except Exception as e:
            print(f"Error initializing MediaPipe: {e}")
            import traceback
            traceback.print_exc()
            raise

        # State variables
        self.last_state = "NEUTRAL"
        self.cycle_count = 0
        self.last_move_time = time.time()
        self.success_trigger_time = None
        self.challenge_completed = False
        self.is_running = False
        self.stop_event = Event()

        # Camera
        self.cap = None

    def is_valid_hand(self, landmarks, label):
        """Validate hand position and orientation"""
        # Check flatness (index MCP and pinky MCP should be at similar y)
        idx_mcp_y = landmarks.landmark[5].y
        pinky_mcp_y = landmarks.landmark[17].y

        if abs(idx_mcp_y - pinky_mcp_y) > self.FLATNESS_TOLERANCE:
            return False, "Keep Hand Flat!"

        # Check palm orientation
        thumb_tip_x = landmarks.landmark[4].x
        pinky_tip_x = landmarks.landmark[20].x

        if label == "Left":
            if thumb_tip_x <= pinky_tip_x:
                return False, "Rotate Palm Up"
        else:
            if thumb_tip_x >= pinky_tip_x:
                return False, "Rotate Palm Up"

        return True, "OK"

    def get_status(self):
        """Get current detection status as JSON"""
        return {
            'cycle_count': self.cycle_count,
            'completed': self.challenge_completed,
            'success_time': self.success_trigger_time,
            'last_state': self.last_state
        }

    def process_frame_from_browser(self, frame_data):
        """
        Process a frame sent from browser (base64 encoded)
        Returns detection results as JSON
        """
        try:
            # Decode base64 image
            import numpy as np
            from io import BytesIO
            from PIL import Image

            # Remove data URL prefix if present
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]

            img_bytes = base64.b64decode(frame_data)
            img = Image.open(BytesIO(img_bytes))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Process frame
            return self._process_frame(frame)

        except Exception as e:
            print(f"Error processing frame: {e}")
            return {'error': str(e)}

    def _process_frame(self, frame):
        """Internal frame processing logic"""
        # Check if already completed
        if self.success_trigger_time is not None:
            elapsed = time.time() - self.success_trigger_time
            if elapsed > self.SUCCESS_DISPLAY_DURATION:
                self.challenge_completed = True
                return {
                    'status': '67 ACTIVATED!',
                    'cycle_count': self.cycle_count,
                    'completed': True,
                    'color': 'green'
                }

            remaining = int(self.SUCCESS_DISPLAY_DURATION - elapsed) + 1
            return {
                'status': '67 ACTIVATED!',
                'cycle_count': self.cycle_count,
                'completed': False,
                'countdown': remaining,
                'color': 'green'
            }

        # Normal detection logic
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        status_text = "Show 2 Hands"
        status_color = "gray"
        hands_detected = 0

        if results.multi_hand_landmarks:
            hands_detected = len(results.multi_hand_landmarks)

            if hands_detected == 2:
                valid_hands_count = 0
                hand_data = []

                for idx, hl in enumerate(results.multi_hand_landmarks):
                    lbl = results.multi_handedness[idx].classification[0].label
                    is_good, msg = self.is_valid_hand(hl, lbl)

                    if is_good:
                        valid_hands_count += 1
                        hand_data.append({
                            'label': lbl,
                            'wrist_y': hl.landmark[0].y
                        })

                if valid_hands_count == 2:
                    # Both hands valid, check for alternating motion
                    left_wrist = None
                    right_wrist = None

                    for hand in hand_data:
                        if hand['label'] == "Left":
                            left_wrist = hand['wrist_y']
                        else:
                            right_wrist = hand['wrist_y']

                    if left_wrist is not None and right_wrist is not None:
                        mid = (left_wrist + right_wrist) / 2
                        left_up = left_wrist < (mid - self.SWAP_THRESHOLD)
                        right_up = right_wrist < (mid - self.SWAP_THRESHOLD)
                        left_down = left_wrist > (mid + self.SWAP_THRESHOLD)
                        right_down = right_wrist > (mid + self.SWAP_THRESHOLD)

                        curr = "NEUTRAL"
                        if left_up and right_down:
                            curr = "LEFT_UP"
                        elif right_up and left_down:
                            curr = "RIGHT_UP"

                        if curr != "NEUTRAL" and curr != self.last_state:
                            self.cycle_count += 1
                            self.last_move_time = time.time()
                            self.last_state = curr

                        if time.time() - self.last_move_time > self.RESET_TIME:
                            self.cycle_count = 0
                            self.last_state = "NEUTRAL"

                        status_text = f"Reps: {self.cycle_count}"
                        status_color = "yellow"

                        if self.cycle_count >= 2:
                            self.success_trigger_time = time.time()
                            print("67 DETECTED - Starting Cooldown")
                else:
                    status_text = "Fix Hand Position!"
                    status_color = "red"
            elif hands_detected == 1:
                status_text = "Show 2 Hands (1 detected)"
                status_color = "orange"

        return {
            'status': status_text,
            'cycle_count': self.cycle_count,
            'hands_detected': hands_detected,
            'completed': False,
            'color': status_color
        }

    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()
        self.hands.close()

# Global detector instance
detector = None

def get_detector():
    """Get or create detector instance"""
    global detector
    if detector is None:
        detector = HandGestureDetector()
    return detector

def reset_detector():
    """Reset detector for new session"""
    global detector
    if detector:
        detector.cleanup()
    detector = HandGestureDetector()
    return detector
