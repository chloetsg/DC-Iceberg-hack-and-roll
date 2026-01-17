from api.reco_main import validate_writing
from api.video import perform_67
import api.captcha_generator as captcha_generator
import api.canvas as canvas
import io
from flask import Flask, jsonify, request
import base64

app = Flask(__name__)

@app.route('/api/get_captcha', methods=['GET'])
def get_captcha():
    # create captcha here
    captcha_text, location, image = captcha_generator.generate_captcha()

    # display captcha.png
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    byte_im= buffer.getvalue()

    return jsonify({"image": base64.b64encode(byte_im).decode('utf-8')})
    # run canvas.py, receive submitted handwriting image as "my_drawing.png"
@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    encoded_data = data.get('drawing').split(',')[1] # Remove the "data:image/png;base64," part
    captcha_text = data.get('text')

    # 1. Convert Base64 string back to an image file for your validator
    img_bytes = base64.b64decode(encoded_data)
    img = Image.open(io.BytesIO(img_bytes))
    
    # Save temporarily to pass to your existing function 
    # (Vercel allows writing to the /tmp folder)
    temp_path = "/tmp/my_drawing.png"
    img.save(temp_path)

    # 2. Run your existing validation logic
    from reco_main import validate_writing
    is_valid = validate_writing(temp_path, captcha_text)

    if is_valid:
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