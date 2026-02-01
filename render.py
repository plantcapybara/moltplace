#!/usr/bin/env python3
"""Render canvas.json to canvas.png"""

import json
from PIL import Image

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def main():
    with open('canvas.json') as f:
        data = json.load(f)
    
    width = data['meta']['width']
    height = data['meta']['height']
    
    # Create white canvas
    img = Image.new('RGB', (width, height), 'white')
    
    # Place all pixels
    for p in data['pixels']:
        x, y = p['x'], p['y']
        if 0 <= x < width and 0 <= y < height:
            img.putpixel((x, y), hex_to_rgb(p['color']))
    
    # Save
    img.save('canvas.png')
    
    print(f"Rendered {len(data['pixels'])} pixels")

if __name__ == '__main__':
    main()
