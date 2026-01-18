from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import io
import base64
from PIL import Image
import numpy as np
import cv2
from captcha_generator import generate_captcha
from reco_main import validate_writing
import os

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
            'captcha_text': captcha_text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate-captcha', methods=['POST'])
def api_validate_captcha():
    """Validate the user's handwritten CAPTCHA"""
    try:
        data = request.json
        session_id = data.get('session_id')
        drawing_data = data.get('drawing')  # Base64 encoded image

        if session_id not in sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 400

        # Decode the drawing
        drawing_bytes = base64.b64decode(drawing_data.split(',')[1])
        drawing_image = Image.open(io.BytesIO(drawing_bytes))

        # Convert to format expected by validator
        drawing_np = np.array(drawing_image)

        # Save temporarily for validation
        temp_path = f'temp_drawing_{session_id}.png'
        cv2.imwrite(temp_path, drawing_np)

        # Validate
        captcha_text = sessions[session_id]['captcha_text']
        success = validate_writing(temp_path, captcha_text)

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True,
            'validated': success,
            'expected': captcha_text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
