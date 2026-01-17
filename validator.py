import easyocr
import numpy as np
import cv2

class StrictValidator:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def validate(self, image_np, target_text):
        # 1. Minimal Preprocessing (Don't fix their mistakes!)
        # Just convert to grayscale
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        # 2. Run OCR with 'detail=1' to get confidence scores
        results = self.reader.readtext(gray, detail=1, allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        # results format: [ ([[x,y]...], 'text', confidence), ... ]
        
        print(f"Raw OCR Results: {results}")

        if not results:
            return False, "I see nothing."

        # 3. Check the best match
        best_match = results[0]
        detected_text = best_match[1]
        confidence = best_match[2]

        print(f"Detected: '{detected_text}' with confidence {confidence:.2f}")

        # 4. The "Strict" Logic
        # - Text must match exactly
        # - Confidence must be high (The drawing must be neat)
        if target_text == detected_text:
            if confidence > 0.2: # Tune this
                return True, "Passed!"
            else:
                return False, f"I think that's '{target_text}', but your handwriting is too shaky (Conf: {confidence:.2f})."
            
        else:
            # Exact match required - case sensitive
            return False, f"You wrote '{detected_text}', expected '{target_text}'"
        
        #return False, f"You wrote '{detected_text}', expected '{target_text}'."