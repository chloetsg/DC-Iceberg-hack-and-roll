from api.reco_main import validate_writing
from api.video import perform_67
import api.captcha_generator as captcha_generator
from PIL import Image
import io
from flask import Flask, jsonify, request, session
import base64
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "DC_Iceberg")

def ocr_verify(image_path, api_key):
    with open(image_path, "rb") as f:
        payload = {
            'apikey': api_key,
            'language': 'eng',
            'isOverlayRequired': False,
            'FileType': 'PNG',
        }
        files = {'file': f}
        
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files=files,
            data=payload
        )
        
    result = response.json()
    
    # Extract the text from the result
    if result.get('ParsedResults'):
        return result['ParsedResults'][0]['ParsedText'].strip()
    return ""

@app.route('/api/get_captcha', methods=['GET'])
def get_captcha():
    # create captcha here
    captcha_text, location, image = captcha_generator.generate_captcha()
    session['captcha_text'] = captcha_text
    session['location'] = location

    # display captcha.png
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    byte_im= buffer.getvalue()

    return jsonify({"image": base64.b64encode(byte_im).decode('utf-8')})

@app.route('/api/verify', methods=['POST'])
def verify():
    captcha_text = session.get('captcha_text')
    encoded_data = request.json.get('drawing').split(',')[1]

    # 1. Convert Base64 string back to an image file for your validator
    img_bytes = base64.b64decode(encoded_data)
    img = Image.open(io.BytesIO(img_bytes))
    
    # Save temporarily to pass to your existing function 
    # (Vercel allows writing to the /tmp folder)
    temp_path = "/tmp/my_drawing.png"
    img.save(temp_path)

    # 2. Run your existing validation logic
    detected_text = ocr_verify("/tmp/my_drawing.png", "K87453151788957")
    #is_valid = validate_writing(temp_path, captcha_text)

    if detected_text.lower() == captcha_text.lower():
        return jsonify({"status": "SUCCESS"})
    else:
        return jsonify({"status": "FAIL"})


    """
    canvas()
    # validates captcha answer
    stage1 = validate_writing(r"my_drawing.png", captcha_text)

    if not stage1:
        return "FAIL"
    
    # validates location answer
    #stage2 = 
    """