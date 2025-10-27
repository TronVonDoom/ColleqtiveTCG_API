#!/usr/bin/env python3
"""
Convert placeholder-card-back.png to WebP format
"""

from PIL import Image
from pathlib import Path

def convert_placeholder_to_webp():
    """Convert the placeholder PNG to WebP"""
    
    # Path to placeholder
    base_path = Path(__file__).parent.parent / 'tcg-images' / 'pokemon' / 'en' / 'cards'
    png_path = base_path / 'placeholder-card-back.png'
    webp_path = base_path / 'placeholder-card-back.webp'
    
    print("[CONVERT] Converting placeholder image to WebP...")
    print(f"  Source: {png_path}")
    print(f"  Target: {webp_path}")
    
    if not png_path.exists():
        print(f"  [ERROR] PNG file not found: {png_path}")
        return False
    
    if webp_path.exists():
        print(f"  [INFO] WebP already exists, will overwrite")
    
    try:
        # Open PNG
        img = Image.open(png_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            # For images with transparency, create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as WebP with high quality
        img.save(webp_path, 'WEBP', quality=95, method=6)
        
        # Get file sizes
        png_size = png_path.stat().st_size / 1024
        webp_size = webp_path.stat().st_size / 1024
        savings = ((png_size - webp_size) / png_size) * 100
        
        print(f"\n  [SUCCESS] Conversion complete!")
        print(f"  PNG size:  {png_size:.2f} KB")
        print(f"  WebP size: {webp_size:.2f} KB")
        print(f"  Savings:   {savings:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Conversion failed: {e}")
        return False

if __name__ == '__main__':
    success = convert_placeholder_to_webp()
    exit(0 if success else 1)
