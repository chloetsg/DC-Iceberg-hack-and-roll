"""
Vercel-optimized version using Google Cloud Vision API for OCR
This avoids the 250MB size limit by using cloud services
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import io
import base64
from PIL import Image
import os

# Lightweight captcha generator (no heavy dependencies)
from captcha_generator import generate_captcha

app = Flask(__name__)
CORS(app)

# Store current session data (in production, use Redis or database)
sessions = {}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/generate-captcha', methods=['GET'])
def api_generate_captcha():
    """Generate a new CAPTCHA"""
    try:
        captcha_text, location, captcha_image = generate_captcha()

        # Convert PIL image to base64
        img_buffer = io.BytesIO()
        captcha_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        # Store in session (use session ID in production)
        session_id = str(len(sessions))
        sessions[session_id] = {
            'captcha_text': captcha_text,
            'location': location
        }

        return jsonify({
            'success': True,
            'session_id': session_id,
            'captcha_image': f'data:image/png;base64,{img_base64}',
            'captcha_text': captcha_text  # For testing; remove in production
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate-captcha', methods=['POST'])
def api_validate_captcha():
    """
    Validate the user's handwritten CAPTCHA
    Uses simple comparison for now - can be upgraded to use:
    1. Google Cloud Vision API (pay-per-use)
    2. Tesseract OCR (lighter than EasyOCR)
    3. External microservice running EasyOCR
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        drawing_data = data.get('drawing')  # Base64 encoded image

        if session_id not in sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 400

        captcha_text = sessions[session_id]['captcha_text']

        # Get OCR service URL from environment variable
        ocr_service_url = os.environ.get('OCR_SERVICE_URL', '')

        if ocr_service_url:
            # Use external OCR microservice (Railway/Render)
            success = validate_with_external_api(drawing_data, captcha_text, ocr_service_url)
        else:
            # Fallback to simple validation for demo
            print("Warning: OCR_SERVICE_URL not set. Using simple validation.")
            success = simple_validation(drawing_data)

        return jsonify({
            'success': True,
            'validated': success,
            'expected': captcha_text,
            'message': 'Demo mode: Validation simplified for Vercel deployment'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def simple_validation(drawing_data):
    """
    Simple validation - checks if user actually drew something
    Replace this with real OCR in production
    """
    try:
        # Decode the image
        drawing_bytes = base64.b64decode(drawing_data.split(',')[1])
        drawing_image = Image.open(io.BytesIO(drawing_bytes))

        # Check if image has any non-black pixels
        pixels = list(drawing_image.convert('RGB').getdata())
        non_black = sum(1 for p in pixels if sum(p) > 30)

        # If more than 100 non-black pixels, consider it a valid attempt
        return non_black > 100
    except:
        return False

# Optional: Google Cloud Vision API integration
def validate_with_google_vision(drawing_data, expected_text):
    """
    Use Google Cloud Vision API for OCR
    Requires: pip install google-cloud-vision
    And GOOGLE_APPLICATION_CREDENTIALS environment variable
    """
    try:
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()

        # Decode image
        image_bytes = base64.b64decode(drawing_data.split(',')[1])
        image = vision.Image(content=image_bytes)

        # Perform OCR
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            detected_text = texts[0].description.strip().lower()
            expected_lower = expected_text.lower()

            # Fuzzy matching
            return detected_text == expected_lower or expected_lower in detected_text

        return False
    except Exception as e:
        print(f"Google Vision API error: {e}")
        return False

# Optional: External microservice validation
def validate_with_external_api(drawing_data, expected_text, ocr_service_url):
    """
    Call an external microservice that runs EasyOCR
    You can deploy EasyOCR on:
    - Railway (unlimited bandwidth)
    - Render (512MB RAM free tier)
    - Your own server
    """
    import requests

    try:
        response = requests.post(
            f'{ocr_service_url}/validate',
            json={
                'image': drawing_data,
                'expected': expected_text
            },
            timeout=30  # Increased timeout for OCR processing
        )

        if response.status_code == 200:
            return response.json().get('validated', False)

        print(f"OCR service returned status {response.status_code}")
        return False
    except requests.exceptions.Timeout:
        print("OCR service timeout - may be cold starting")
        return False
    except Exception as e:
        print(f"External API error: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
