"""
Vercel-compatible CAPTCHA generator
Removed turtle import that causes issues on serverless
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import os

def create_captcha(text):
    # Create a blank white image
    width = 400
    height = 150
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    valid_fonts = ["arial.ttf", "arialbd.ttf", "ariblk.ttf",
                   "calibri.ttf", "calibrib.ttf",
                   "segoeui.ttf", "segoeuib.ttf",
                   "tahoma.ttf", "tahomabd.ttf",
                   "verdanab.ttf", "verdana.ttf",
                   "times.ttf", "timesbd.ttf"]

    sizes = [random.randint(*sorted([int(0.25*width), int(0.4*height)])) for i in text]
    shapes = ['arc', 'line']

    # Calculate proper spacing to avoid overlap
    x_position = 20  # Start with some margin from the left

    for i, char in enumerate(text):
        try:
            font = ImageFont.truetype(random.choice(valid_fonts), sizes[i])
        except:
            # Fallback to default font if custom fonts not available
            font = ImageFont.load_default()

        char_color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))

        # Random vertical jitter
        y_position = random.randint(0, height - sizes[i])

        # Draw the character
        draw.text((x_position, y_position), char, font=font, fill=char_color)

        # Move x_position to the right
        try:
            char_bbox = draw.textbbox((x_position, y_position), char, font=font)
            char_width = char_bbox[2] - char_bbox[0]
        except:
            char_width = sizes[i] // 2

        x_position += char_width + random.randint(5, 15)

    # Add some random "scribble" lines
    for _ in range(random.randint(5,10)):
        shape = random.choice(shapes)
        if shape == 'line':
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(random.randint(2,10))]
            draw.line(points, fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)), width=random.randint(1,int(0.005*width)), joint="curve")
        elif shape == 'arc':
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

    return img

def generate_captcha():
    """Generate a new CAPTCHA without the letter 'j' or 'J'"""
    valid_characters = "234578bdefhimnqrtyABDEFHILMNQRTY"
    captcha_text = ''.join(random.choices(valid_characters, k=5))

    image = create_captcha(captcha_text)

    return captcha_text, None, image
