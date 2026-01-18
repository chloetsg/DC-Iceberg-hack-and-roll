"""
Standalone OCR Microservice
Deploy this separately on Railway, Render, or your own server
This handles the heavy EasyOCR processing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import numpy as np
import cv2
from reco_main import validate_writing
import os

app = Flask(__name__)
CORS(app)  # Allow requests from Vercel frontend

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'OCR Microservice'})

@app.route('/validate', methods=['POST'])
def validate():
    """
    Validate handwritten text using EasyOCR

    Request:
    {
        "image": "data:image/png;base64,...",
        "expected": "abc123"
    }

    Response:
    {
        "success": true,
        "validated": true,
        "confidence": 0.85
    }
    """
    try:
        data = request.json
        image_data = data.get('image')
        expected_text = data.get('expected')

        if not image_data or not expected_text:
            return jsonify({
                'success': False,
                'error': 'Missing image or expected text'
            }), 400

        # Decode the image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to format expected by validator
        image_np = np.array(image)

        # Save temporarily for validation
        temp_path = f'/tmp/temp_drawing_{os.getpid()}.png'
        cv2.imwrite(temp_path, image_np)

        # Validate using EasyOCR
        validated = validate_writing(temp_path, expected_text)

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True,
            'validated': validated
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
