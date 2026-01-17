import cv2
import numpy as np
import json
import os

# --- Configuration ---
CANVAS_SIZE = (600, 800) # Height, Width
PEN_COLOR = (255, 255, 255) # White
PEN_THICKNESS = 5
CONFIG_FILE = "canvas_bounds.json"

# State variables
drawing = False
last_point = None

# --- Mouse Callback Function ---
# This function runs every time the mouse moves or clicks
def draw_event(event, x, y, flags, param):
    global drawing, last_point, canvas

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        last_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing and last_point:
            # Draw a line from the last point to the current point
            cv2.line(canvas, last_point, (x, y), PEN_COLOR, PEN_THICKNESS)
            last_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        last_point = None

# --- Main Setup ---
# Create a black image (Height, Width, 3 Channels)
canvas = np.zeros((CANVAS_SIZE[0], CANVAS_SIZE[1], 3), dtype="uint8")

cv2.namedWindow("Draw Here")
# Link the mouse to the window
cv2.setMouseCallback("Draw Here", draw_event)

print("Controls:")
print("  Draw: Left Mouse Button")
print("  Clear: 'c'")
print("  Save: 's'")
print("  Quit: 'q'")

# Get window position and save bounds for AHK scripts
window_shown = False

while True:
    cv2.imshow("Draw Here", canvas)

    # After first frame, get window position and save to config
    if not window_shown:
        cv2.waitKey(100)  # Wait for window to be fully created
        try:
            # Get window position (x, y) - top-left corner
            x, y = cv2.getWindowImageRect("Draw Here")[:2]

            # Calculate bounds
            bounds = {
                "left": x,
                "top": y,
                "right": x + CANVAS_SIZE[1],  # x + width
                "bottom": y + CANVAS_SIZE[0],  # y + height
                "width": CANVAS_SIZE[1],
                "height": CANVAS_SIZE[0]
            }

            # Save to JSON file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(bounds, f, indent=2)

            print(f"\nCanvas bounds saved to {CONFIG_FILE}")
            print(f"Position: ({x}, {y}), Size: {CANVAS_SIZE[1]}x{CANVAS_SIZE[0]}")
            window_shown = True
        except:
            pass  # Window might not be ready yet
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('c'):
        # Clear by setting all pixels to black (0)
        canvas[:] = 0 
    elif key == ord('s'):
        # Save the file
        filename = "my_drawing.png"
        cv2.imwrite(filename, canvas)
        print(f"Saved to {filename}!")

cv2.destroyAllWindows()