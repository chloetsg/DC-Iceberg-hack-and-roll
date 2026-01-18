from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import io
import base64
from PIL import Image
import numpy as np
import cv2
from captcha_generator import generate_captcha
from reco_main import validate_writing
from video_stream import get_detector, reset_detector
import os

app = Flask(__name__)
CORS(app)

# Store current session data (in production, use Redis or database)
sessions = {}
# Store hand detection sessions
hand_sessions = {}

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

@app.route('/api/start-hand-detection', methods=['POST'])
def api_start_hand_detection():
    """Initialize hand detection session"""
    try:
        data = request.json
        session_id = data.get('session_id')

        # Reset detector for new session
        detector = reset_detector()
        hand_sessions[session_id] = detector

        return jsonify({
            'success': True,
            'message': 'Hand detection started'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/process-hand-frame', methods=['POST'])
def api_process_hand_frame():
    """Process a video frame for hand detection"""
    try:
        data = request.json
        session_id = data.get('session_id')
        frame_data = data.get('frame')  # Base64 encoded frame

        if session_id not in hand_sessions:
            # Create new detector if session doesn't exist
            detector = get_detector()
            hand_sessions[session_id] = detector
        else:
            detector = hand_sessions[session_id]

        # Process the frame
        result = detector.process_frame_from_browser(frame_data)

        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        print(f"Error processing hand frame: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stop-hand-detection', methods=['POST'])
def api_stop_hand_detection():
    """Stop hand detection session"""
    try:
        data = request.json
        session_id = data.get('session_id')

        if session_id in hand_sessions:
            hand_sessions[session_id].cleanup()
            del hand_sessions[session_id]

        return jsonify({
            'success': True,
            'message': 'Hand detection stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
