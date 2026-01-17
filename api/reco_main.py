import cv2
from api.validator import StrictValidator  # Assuming you saved the class in validator.py


def validate_writing(img_path, captcha_text):
    # 1. Initialize the validator
    # (This takes a few seconds to load the AI model)
    my_validator = StrictValidator()

    # 2. Load an image from your computer
    # cv2.imread loads the image as a NumPy array automatically
    image_path = img_path
    image_np = cv2.imread(image_path)

    # Check if image loaded correctly
    if image_np is None:
        print("Error: Could not find image file.")
    else:
        # 3. Put the image into the validator
        # Target text is what you EXPECTED them to write
        success, message = my_validator.validate(image_np, target_text=captcha_text)

        print(f"Result: {success}")
        print(f"Message: {message}")
    
    return success
