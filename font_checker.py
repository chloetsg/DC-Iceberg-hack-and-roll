import os
from PIL import ImageFont

def check_fonts(font_list):
    installed = []
    missing = []
    
    # Standard Windows Font path
    win_font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')

    for font_name in font_list:
        try:
            # Pillow looks in system folders automatically, but we can 
            # also check the specific path for absolute certainty.
            full_path = os.path.join(win_font_path, font_name)
            
            # Attempt to load the font
            ImageFont.truetype(font_name, 10) 
            installed.append(font_name)
        except OSError:
            missing.append(font_name)
            
    return installed, missing

# Your list of strings
my_fonts = ["arialbd.ttf", "ariblk.ttf", 
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

available, unavailable = check_fonts(my_fonts)

print(f"✅ Ready to use: {available}")
print(f"❌ Missing/Invalid: {unavailable}")