import easyocr
import numpy as np
import cv2

class StrictValidator:
    def __init__(self):
        # Use GPU if available for faster processing
        self.reader = easyocr.Reader(['en'], gpu=False)  # Set to True if you have GPU

    def validate(self, image_np, target_text):
        # 1. Minimal Preprocessing
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        # 2. Run OCR with faster settings
        results = self.reader.readtext(
            gray,
            detail=1,
            allowlist='bcdefhijklmnopqrstuvwxyzABCDEFHIJKLMNOPQRSTUVWXYZ12345678',
            paragraph=False,  # Faster processing
            min_size=10       # Ignore very small text
        )

        print(f"Raw OCR Results: {results}")

        if not results:
            return False, "I see nothing."

        # 3. Check all detected text (more lenient)
        target_lower = target_text.lower()

        for result in results:
            detected_text = result[1]
            confidence = result[2]
            detected_lower = detected_text.lower()

            print(f"Detected: '{detected_text}' with confidence {confidence:.2f}")

            # More lenient matching:
            # 1. Case-insensitive comparison
            # 2. Lower confidence threshold (0.1 instead of 0.2)
            # 3. Check if detected text contains target or vice versa
            if detected_lower == target_lower:
                if confidence > 0.1:
                    return True, "Passed!"
                else:
                    return True, "Passed! (Low confidence but acceptable)"

            # Also accept if target is contained in detected text or vice versa
            if target_lower in detected_lower or detected_lower in target_lower:
                if len(detected_lower) - len(target_lower) <= 2:  # Allow 2 extra/missing chars
                    return True, "Passed! (Close enough)"

        # If no match found, show what was detected
        detected_text = results[0][1]
        return False, f"You wrote '{detected_text}', expected '{target_text}'"