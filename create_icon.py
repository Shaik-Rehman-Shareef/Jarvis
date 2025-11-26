# Create a simple icon placeholder
# This creates a default icon file if a custom one is not available

from PIL import Image, ImageDraw, ImageFont
import os

def create_jarvis_icon():
    """Create a simple JARVIS icon"""
    
    # Create assets directory if it doesn't exist
    os.makedirs("assets", exist_ok=True)
    
    # Create icon sizes
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        # Create image with dark blue background
        img = Image.new('RGBA', size, (0, 50, 100, 255))
        draw = ImageDraw.Draw(img)
        
        # Calculate font size based on image size
        font_size = max(size[0] // 3, 12)
        
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw "J" in the center
        text = "J"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw text with white color
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Add a subtle border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(100, 150, 200, 255), width=1)
        
        images.append(img)
    
    # Save as ICO file
    icon_path = "assets/jarvis_icon.ico"
    images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"Created icon: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_jarvis_icon()
