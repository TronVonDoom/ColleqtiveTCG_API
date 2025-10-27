#!/usr/bin/env python3
"""
Download missing card images as WebP from Pokemon TCG API
"""

import sqlite3
import requests
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
import time

def sanitize_card_number(card_number):
    """Sanitize card number to match imageConfig.js logic"""
    if not card_number:
        return ''
    
    return (card_number
        .replace('/', '_')
        .replace(' ', '_')
        .replace('?', 'question')
        .replace('*', 'star')
        .replace(':', '_')
        .replace('<', '_')
        .replace('>', '_')
        .replace('|', '_')
        .replace('"', '_')
        .replace('\\', '_'))

def download_and_convert_to_webp(url, output_path, quality=95):
    """Download image from URL and convert to WebP"""
    try:
        # Download image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Open image from response
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary (WebP doesn't support all modes)
        if img.mode in ('RGBA', 'LA', 'P'):
            # For images with transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as WebP
        img.save(output_path, 'WEBP', quality=quality, method=6)
        
        return True, None
    except Exception as e:
        return False, str(e)

def download_missing_images(language='en'):
    """Download missing card images for specified language"""
    
    # Paths
    db_path = Path(__file__).parent.parent / 'pokemontcg' / 'pokemontcg.db'
    image_base = Path(__file__).parent.parent / 'tcg-images' / 'pokemon' / language / 'cards'
    
    print(f"🎴 Pokemon TCG Card Image Downloader (WebP) - Language: {language.upper()}")
    print("=" * 80)
    print()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all cards that have image URLs but missing local files
    cursor.execute('''
        SELECT c.id, c.set_id, c.number, c.name, c.image_large, s.name
        FROM cards c
        JOIN sets s ON c.set_id = s.id
        WHERE c.image_large IS NOT NULL
        ORDER BY s.release_date DESC, c.number
    ''')
    cards = cursor.fetchall()
    
    print(f"📊 Total cards in database: {len(cards)}")
    
    # Find missing images
    missing_cards = []
    for card_id, set_id, card_number, card_name, image_url, set_name in cards:
        safe_number = sanitize_card_number(card_number)
        image_path = image_base / set_id / f'{safe_number}.webp'
        
        if not image_path.exists() and image_url:
            missing_cards.append({
                'card_id': card_id,
                'set_id': set_id,
                'card_number': card_number,
                'safe_number': safe_number,
                'card_name': card_name,
                'set_name': set_name,
                'image_url': image_url,
                'image_path': image_path
            })
    
    print(f"❌ Missing images: {len(missing_cards)}")
    print()
    
    if not missing_cards:
        print("✅ All images are already downloaded!")
        conn.close()
        return
    
    # Ask for confirmation
    response = input(f"📥 Download {len(missing_cards)} missing images as WebP? (y/n): ")
    if response.lower() != 'y':
        print("❌ Download cancelled")
        conn.close()
        return
    
    print()
    print("🚀 Starting download...")
    print("-" * 80)
    
    # Download images
    success_count = 0
    failed_count = 0
    failed_cards = []
    
    for i, card in enumerate(missing_cards, 1):
        print(f"[{i}/{len(missing_cards)}] {card['set_id']}/{card['card_number']} - {card['card_name'][:40]}", end="... ")
        
        success, error = download_and_convert_to_webp(
            card['image_url'],
            card['image_path'],
            quality=95
        )
        
        if success:
            print("✅")
            success_count += 1
        else:
            print(f"❌ {error}")
            failed_count += 1
            failed_cards.append((card, error))
        
        # Rate limiting - be nice to the API
        time.sleep(0.3)
    
    print("-" * 80)
    print()
    print("📊 Download Summary:")
    print(f"   ✅ Successfully downloaded: {success_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📈 Success rate: {success_count / len(missing_cards) * 100:.2f}%")
    
    if failed_cards:
        print()
        print("❌ Failed downloads:")
        for card, error in failed_cards:
            print(f"   • {card['set_id']}/{card['card_number']} - {card['card_name']}")
            print(f"     Error: {error}")
    
    conn.close()
    print()
    print("✅ Download complete!")

if __name__ == '__main__':
    download_missing_images()
