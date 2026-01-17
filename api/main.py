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
    canvas()
    # validates captcha answer
    stage1 = validate_writing(r"my_drawing.png", captcha_text)

    if not stage1:
        return "FAIL"
    
    # validates location answer
    #stage2 = 



    pass