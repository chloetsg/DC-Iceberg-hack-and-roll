import cv2
import numpy as np

# --- Configuration ---
CANVAS_SIZE = (600, 800) # Height, Width
PEN_COLOR = (255, 255, 255) # White
PEN_THICKNESS = 5

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

while True:
    cv2.imshow("Draw Here", canvas)
    
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