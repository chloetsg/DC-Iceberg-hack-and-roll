from reco_main import validate_writing
from video import perform_67



def main():

    # create captcha here
    captcha_text: str

    # display captcha.png

    # run canvas.py, receive submitted handwriting image as "my_drawing.png"

    # validates captcha answer
    stage1 = validate_writing(r"my_drawing.png", captcha_text)

    if not stage1:
        return "FAIL"
    
    # validates location answer
    #stage2 = 



    pass


main()