from turtle import width
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import os

loc_dict = {
    "amk hub": "ang mo kio",
    "clementi" : "clementi",
    "hillion" : "bukit panjang",
    "imm" : "jurong east",
    "jewel" : "changi airport",
    "junction 8" : "bishan",
    "jurong point" : "boon lay",
    "kallang wave" : "stadium",
    "mbs" : "bayfront",
    "nex" : "serangoon",
    "northpoint" : "yishun",
    "plaza sing" : "dhoby ghaut",
    "singpost centre" : "paya lebar",
    "star vista" : "buona vista",
    "sun plaza" : "sembawang",
    "tampines1" : "tampines",
    "velocity" : "novena",
    "vivo" : "harbourfront",
    "waterway point" : "punggol",
    "white sands" : "pasir ris"
}

def read_bg(folder_path):
    valid_extensions = ('.jpg', '.jpeg')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

    if not files:
        raise FileNotFoundError("No images found in the specified folder.")

    bg_path = os.path.join(folder_path, random.choice(files))
    bg_image = Image.open(bg_path).convert('RGB')
    location = bg_path.split("\\")[-1].split(".")[0]

    return bg_image, bg_image.width, bg_image.height, loc_dict[location]

def create_captcha(text):
    # Create a blank image
    img, width, height, location = read_bg("./mall-images")
    draw = ImageDraw.Draw(img)
    
    valid_fonts = ["arialbd.ttf", "ariblk.ttf", 
                   "calibri.ttf", "calibrib.ttf",
                   "segoeui.ttf", "segoeuib.ttf",
                   "tahoma.ttf", "tahomabd.ttf",
                   "verdanab.ttf", "verdana.ttf",
                   "times.ttf", "timesbd.ttf",
                   "georgia.ttf", "georgiab.ttf",
                   "cambriab.ttf",
                   "pala.ttf", "palab.ttf",
                   "comic.ttf", "comicbd.ttf",
                   "consolab.ttf",
                   "cour.ttf", "courbd.ttf",
                   "impact.ttf"]

    sizes = [random.randint(*sorted([int(0.25*width), int(0.4*height)])) for i in text]
    shapes = ['arc', 'line']

    for i, char in enumerate(text):
        font = ImageFont.truetype(random.choice(valid_fonts), sizes[i]) #set font
        char_color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))
        # Random vertical jitter
        draw.text((0 + i*random.randint(sizes[i],sizes[i]+10), random.randint(0,height-sizes[i])), char, font=font, fill=char_color)

    # Add some random "scribble" lines before the text
    for _ in range(random.randint(20,50)):
        shape = random.choice(shapes)
        if shape == 'line':
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(random.randint(2,10))]
            draw.line(points, fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)), width=random.randint(1,int(0.005*width)), joint="curve")
        elif shape == 'arc':
            # Define a random bounding box for the arc
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(x1, width), random.randint(y1, height)
            points = [x1, y1, x2, y2]
            start_angle = random.randint(0, 360)
            end_angle = random.randint(0, 360)            
            arc_color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
            draw.arc(points, start=start_angle, end=end_angle, fill=arc_color, width=random.randint(1,int(0.005*width)))

    # Add random dots as noise
    for _ in range(int(0.005 * width * height)):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(0, 0, 0))
    
    return img, location

# Usage
def generate_captcha():
    valid_characters = "23456789abdefghijmnqrtyABDEFGHJLMNQRTY"
    captcha_text = ''.join(random.choices(valid_characters, k=5))

    image, location = create_captcha(captcha_text)
    image.save("captcha.png")

    return captcha_text, location, image