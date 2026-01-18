# CAPTCHA Challenge Chrome Extension

A Chrome extension version of the Python CAPTCHA Challenge app. This extension displays a CAPTCHA, lets users draw their answer on a canvas, and validates the input.

## File Structure

```
captcha-extension/
├── manifest.json      # Chrome extension configuration
├── popup.html         # Main UI (replaces tkinter window)
├── app.js             # Main application logic (replaces main.py)
├── background.js      # Service worker for extension lifecycle
├── styles.css         # Styling (replaces tkinter styling)
├── icons/             # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md          # This file
```

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `captcha-extension` folder
5. The extension icon should appear in your toolbar

## How It Works

### Mapping from Python to JavaScript

| Python (main.py)           | JavaScript (app.js)           |
|----------------------------|-------------------------------|
| `CaptchaApp` class         | `CaptchaApp` class            |
| `tkinter` widgets          | HTML elements + CSS           |
| `Canvas` widget            | `<canvas>` element            |
| `PIL.Image`                | Canvas API                    |
| `cv2` (OpenCV)             | Canvas API / Tesseract.js     |
| `messagebox`               | `showMessage()` method        |
| `generate_captcha()`       | `generateCaptcha()` method    |
| `validate_writing()`       | `validateWriting()` method    |
| `perform_67()`             | `perform67()` method          |

## Implementing Validation

The current `validateWriting()` method is a placeholder. You have three options:

### Option 1: Use Tesseract.js (Browser OCR)

Add Tesseract.js to your extension:

```html
<!-- In popup.html -->
<script src="https://unpkg.com/tesseract.js@4/dist/tesseract.min.js"></script>
```

Then update `validateWriting()`:

```javascript
async validateWriting(imageData, expectedText) {
  const result = await Tesseract.recognize(imageData, 'eng');
  const recognized = result.data.text.trim().toUpperCase().replace(/\s/g, '');
  return recognized === expectedText.toUpperCase();
}
```

### Option 2: Backend API

Keep your Python validation running as a server and call it:

```javascript
async validateWriting(imageData, expectedText) {
  const response = await fetch('http://localhost:5000/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageData, expected: expectedText })
  });
  const result = await response.json();
  return result.success;
}
```

Python Flask server (`server.py`):
```python
from flask import Flask, request, jsonify
from reco_main import validate_writing
import base64

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    # Decode base64 image and save temporarily
    image_data = data['image'].split(',')[1]
    with open('temp.png', 'wb') as f:
        f.write(base64.b64decode(image_data))
    
    success = validate_writing('temp.png', data['expected'])
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(port=5000)
```

### Option 3: Cloud OCR API

Use Google Cloud Vision, AWS Textract, or similar:

```javascript
async validateWriting(imageData, expectedText) {
  const response = await fetch('https://vision.googleapis.com/v1/images:annotate?key=YOUR_API_KEY', {
    method: 'POST',
    body: JSON.stringify({
      requests: [{
        image: { content: imageData.split(',')[1] },
        features: [{ type: 'TEXT_DETECTION' }]
      }]
    })
  });
  const result = await response.json();
  const detected = result.responses[0].fullTextAnnotation?.text || '';
  return detected.toUpperCase().includes(expectedText.toUpperCase());
}
```

## Implementing the "67" Challenge

The original uses OpenCV with webcam for hand gesture detection. For the browser, use MediaPipe Hands:

```html
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
```

See [MediaPipe Hands documentation](https://google.github.io/mediapipe/solutions/hands.html) for implementation details.

## Limitations

- **Cursor Effect**: Chrome extensions cannot control the system cursor. The teleporting cursor effect is visual-only within the extension popup.
- **File System**: Extensions can't write to the file system directly. Use Chrome's storage API or send data to a server.
- **Subprocess**: Can't run external executables. Any Python processing must be done via API calls.

## Keyboard Shortcuts

- `Ctrl+B` - Bypass CAPTCHA (debug feature)

## Customization

- Edit `styles.css` to change colors and layout
- Modify `generateCaptcha()` to adjust CAPTCHA complexity
- Update the validation logic for your specific needs

## Next Steps

1. Replace placeholder icons with proper ones
2. Implement actual OCR validation
3. Add persistent storage for scores/progress
4. Consider adding difficulty levels
