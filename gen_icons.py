import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, path):
    img = Image.new('RGB', (size, size), color=(27, 58, 107)) # #1B3A6B TruthLens blue
    d = ImageDraw.Draw(img)
    # Just draw a simple white circle representing the "lens"
    margin = size // 5
    d.ellipse([margin, margin, size - margin, size - margin], outline="white", width=max(1, size // 16))
    # A small dot in the center
    center_r = max(2, size // 10)
    d.ellipse([size//2 - center_r, size//2 - center_r, size//2 + center_r, size//2 + center_r], fill="white")
    
    img.save(path)

os.makedirs('extension/icons', exist_ok=True)
create_icon(16, 'extension/icons/icon16.png')
create_icon(48, 'extension/icons/icon48.png')
create_icon(128, 'extension/icons/icon128.png')

print("Icons generated!")
