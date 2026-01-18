"""
Test script to verify video_stream.py works correctly
"""
from video_stream import HandGestureDetector
import base64
import cv2

def test_detector():
    print("Testing HandGestureDetector...")

    try:
        # Initialize detector
        detector = HandGestureDetector()
        print("[OK] Detector initialized successfully")

        # Test with a dummy frame (black image)
        import numpy as np
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Convert to base64
        _, buffer = cv2.imencode('.jpg', dummy_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{frame_base64}"

        # Process frame
        result = detector.process_frame_from_browser(frame_data)
        print("[OK] Frame processed successfully")
        print(f"  Result: {result}")

        # Cleanup
        detector.cleanup()
        print("[OK] Detector cleaned up successfully")

        print("\n[SUCCESS] All tests passed!")
        return True

    except Exception as e:
        print(f"[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_detector()
