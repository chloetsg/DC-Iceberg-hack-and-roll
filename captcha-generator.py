from PIL import Image, ImageDraw, ImageFont
import random
import string

def create_captcha(text, width=250, height=100):
    # Create a blank image
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
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

    sizes = [random.randint(25,40) for i in text]
    shapes = ['arc', 'line']

    for i, char in enumerate(text):
        font = ImageFont.truetype(random.choice(valid_fonts), sizes[i]) #set font
        char_color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))
        # Random vertical jitter
        draw.text((0 + i*random.randint(40,50), random.randint(0,100-sizes[i])), char, font=font, fill=char_color)

    # Add some random "scribble" lines before the text
    for _ in range(random.randint(10,15)):
        shape = random.choice(shapes)
        if shape == 'line':
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(random.randint(2,5))]
            draw.line(points, fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)), width=random.randint(1,5), joint="curve")
        elif shape == 'arc':
            # Define a random bounding box for the arc
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(x1, width), random.randint(y1, height)
            points = [x1, y1, x2, y2]
            start_angle = random.randint(0, 360)
            end_angle = random.randint(0, 360)            
            arc_color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
            draw.arc(points, start=start_angle, end=end_angle, fill=arc_color, width=3)

    # Add random dots as noise
    for _ in range(2000):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(0, 0, 0))
    
    return img

# Usage
valid_characters = "23456789abdefghijmnpqrtyABDEFGHJLMNPQRTY"
captcha_text = ''.join(random.choices(valid_characters, k=5))
print(captcha_text)
image = create_captcha(captcha_text)
image.save("captcha.png")