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

    # Use consistent, readable size for all characters
    font_size = 50

    # Calculate proper spacing to avoid overlap
    x_position = 30  # Start with some margin from the left

    for i, char in enumerate(text):
        try:
            font = ImageFont.truetype(random.choice(valid_fonts), font_size)
        except:
            # Fallback to default font if custom fonts not available
            font = ImageFont.load_default()

        # Use darker, more visible colors
        char_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))

        # Centered vertical position with slight jitter
        y_position = (height - font_size) // 2 + random.randint(-10, 10)

        # Draw the character
        draw.text((x_position, y_position), char, font=font, fill=char_color)

        # Move x_position to the right
        try:
            char_bbox = draw.textbbox((x_position, y_position), char, font=font)
            char_width = char_bbox[2] - char_bbox[0]
        except:
            char_width = font_size // 2

        x_position += char_width + random.randint(10, 20)

    # Add minimal noise - just a few light lines
    for _ in range(3):
        points = [(random.randint(0, width), random.randint(0, height)) for _ in range(2)]
        draw.line(points, fill=(200, 200, 200), width=1)

    return img

def generate_captcha():
    """Generate a new CAPTCHA without the letter 'j' or 'J'"""
    valid_characters = "234578bdefhimnqrtyABDEFHILMNQRTY"
    captcha_text = ''.join(random.choices(valid_characters, k=5))

    image = create_captcha(captcha_text)

    return captcha_text, None, image
