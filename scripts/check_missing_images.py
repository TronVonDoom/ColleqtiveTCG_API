#!/usr/bin/env python3
"""
Check for missing card images and generate a report
"""

import sqlite3
import os
from pathlib import Path
from collections import defaultdict

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

def check_missing_images():
    """Check which card images are missing"""
    
    # Paths
    db_path = Path(__file__).parent.parent / 'pokemontcg' / 'pokemontcg.db'
    image_base = Path(__file__).parent.parent / 'tcg-images' / 'pokemon' / 'cards'
    
    print("🔍 Scanning for missing card images...")
    print(f"Database: {db_path}")
    print(f"Image base: {image_base}")
    print()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all cards with set info
    cursor.execute('''
        SELECT c.id, c.set_id, c.number, s.name, s.release_date
        FROM cards c
        JOIN sets s ON c.set_id = s.id
        ORDER BY s.release_date DESC, c.number
    ''')
    cards = cursor.fetchall()
    
    print(f"📊 Total cards in database: {len(cards)}")
    
    # Check which images exist
    missing_by_set = defaultdict(list)
    existing_count = 0
    total_missing = 0
    
    for card_id, set_id, card_number, set_name, release_date in cards:
        safe_number = sanitize_card_number(card_number)
        image_path = image_base / set_id / f'{safe_number}.webp'
        
        if not image_path.exists():
            missing_by_set[set_id].append({
                'card_id': card_id,
                'card_number': card_number,
                'safe_number': safe_number,
                'set_name': set_name,
                'release_date': release_date,
                'expected_path': str(image_path)
            })
            total_missing += 1
        else:
            existing_count += 1
    
    # Print summary
    print(f"✅ Existing images: {existing_count}")
    print(f"❌ Missing images: {total_missing}")
    print(f"📦 Sets with missing images: {len(missing_by_set)}")
    print(f"✨ Completion: {existing_count / len(cards) * 100:.2f}%")
    print()
    
    if missing_by_set:
        print("🔴 Sets with missing images (sorted by most missing):")
        print("-" * 80)
        
        sorted_sets = sorted(missing_by_set.items(), key=lambda x: len(x[1]), reverse=True)
        
        for set_id, missing_cards in sorted_sets[:20]:  # Top 20
            set_name = missing_cards[0]['set_name']
            release_date = missing_cards[0]['release_date']
            print(f"  {set_id:20} | {set_name:40} | {len(missing_cards):4} missing | {release_date}")
        
        if len(sorted_sets) > 20:
            print(f"\n  ... and {len(sorted_sets) - 20} more sets with missing images")
    
    conn.close()
    
    return missing_by_set

if __name__ == '__main__':
    missing = check_missing_images()
    print(f"\n✅ Scan complete!")
