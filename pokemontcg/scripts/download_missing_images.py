#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download missing card images from Pokemon TCG API
This script checks which images are missing on the server and downloads them
"""

import os
import sys
import requests
import time
import re
from pathlib import Path

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path to import from pokemontcg module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pokemontcg.config import API_KEY, BASE_URL

API_BASE = BASE_URL
HEADERS = {'X-Api-Key': API_KEY} if API_KEY else {}

# Base directory for images (adjust if needed)
IMAGES_BASE_DIR = Path(__file__).parent.parent.parent / 'tcg-images-download' / 'pokemon' / 'cards'

def get_cards_for_set(set_id):
    """Get all cards for a specific set from the API"""
    print(f"\n📦 Fetching cards for set: {set_id}")
    
    url = f"{API_BASE}/cards"
    # Use very small page size for problematic sets
    page_size = 50 if set_id in ['ecard3'] else (100 if set_id.startswith('ecard') else 250)
    params = {
        'q': f'set.id:{set_id}',
        'pageSize': page_size
    }
    
    print(f"   Using page size: {page_size}")
    
    all_cards = []
    page = 1
    max_retries = 5
    
    while True:
        params['page'] = page
        
        # Retry logic
        response = None
        for attempt in range(max_retries):
            try:
                print(f"   Fetching page {page} (attempt {attempt + 1}/{max_retries})...")
                response = requests.get(url, headers=HEADERS, params=params, timeout=120)
                
                if response.status_code == 200:
                    break
                elif response.status_code == 504:
                    print(f"   ⚠️  Timeout (504), waiting longer...")
                    time.sleep(10)
                else:
                    print(f"   ❌ Error fetching cards: {response.status_code}")
                    if attempt == max_retries - 1:
                        return all_cards
                    time.sleep(3)
            except requests.Timeout:
                print(f"   ⚠️  Request timeout, waiting longer...")
                time.sleep(10)
            except Exception as e:
                print(f"   ❌ Error: {e}")
                if attempt == max_retries - 1:
                    return all_cards
                time.sleep(3)
        
        if response is None or response.status_code != 200:
            break
        
        data = response.json()
        cards = data.get('data', [])
        
        if not cards:
            break
        
        all_cards.extend(cards)
        print(f"   Retrieved page {page}: {len(cards)} cards (Total so far: {len(all_cards)})")
        
        page += 1
        time.sleep(0.3)  # Rate limiting
        
        # Check if there are more pages - use the actual page size, not hardcoded 250
        total_count = data.get('totalCount', 0)
        if len(cards) < page_size or len(all_cards) >= total_count:
            print(f"   No more pages (total count: {total_count})")
            break
    
    print(f"✅ Total cards fetched: {len(all_cards)}")
    return all_cards

def sanitize_card_number(number):
    """Sanitize card number for filesystem - replace problematic characters"""
    # Replace characters that are invalid in Windows filenames
    # ? is invalid in Windows, so replace with something meaningful
    sanitized = number.replace('/', '_').replace(' ', '_').replace('?', 'question')
    # Also handle other potentially problematic characters
    sanitized = sanitized.replace('*', 'star').replace(':', '_').replace('<', '_').replace('>', '_')
    sanitized = sanitized.replace('|', '_').replace('"', '_').replace('\\', '_')
    return sanitized

def download_image(url, save_path):
    """Download an image from URL to save_path"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"   ❌ HTTP {response.status_code}: {url}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_and_download_missing_images(set_id, force_download=False):
    """Check for missing images and download them"""
    
    # Get all cards for this set
    cards = get_cards_for_set(set_id)
    
    if not cards:
        print(f"❌ No cards found for set {set_id}")
        return
    
    set_dir = IMAGES_BASE_DIR / set_id
    
    missing_small = []
    missing_large = []
    
    print(f"\n🔍 Checking for missing images...")
    
    for card in cards:
        number = sanitize_card_number(card.get('number', ''))
        images = card.get('images', {})
        
        small_url = images.get('small')
        large_url = images.get('large')
        
        small_path = set_dir / 'small' / f"{number}.png"
        large_path = set_dir / 'large' / f"{number}.png"
        
        # Check if images exist
        if force_download or not small_path.exists():
            if small_url:
                missing_small.append({
                    'card': card,
                    'number': number,
                    'url': small_url,
                    'path': small_path
                })
        
        if force_download or not large_path.exists():
            if large_url:
                missing_large.append({
                    'card': card,
                    'number': number,
                    'url': large_url,
                    'path': large_path
                })
    
    total_missing = len(missing_small) + len(missing_large)
    
    if total_missing == 0:
        print(f"✅ All images present for set {set_id}!")
        return
    
    print(f"\n📊 Missing images:")
    print(f"   Small: {len(missing_small)}")
    print(f"   Large: {len(missing_large)}")
    print(f"   Total: {total_missing}")
    
    # Ask for confirmation
    if not force_download:
        response = input(f"\n📥 Download {total_missing} missing images? (y/n): ")
        if response.lower() != 'y':
            print("❌ Download cancelled")
            return
    
    # Download missing small images
    if missing_small:
        print(f"\n📥 Downloading {len(missing_small)} small images...")
        for i, item in enumerate(missing_small, 1):
            card = item['card']
            name = card.get('name', 'Unknown')
            number = item['number']
            print(f"   [{i}/{len(missing_small)}] {name} (#{number})")
            
            if download_image(item['url'], item['path']):
                print(f"      ✅ Downloaded small image")
            else:
                print(f"      ❌ Failed to download small image")
            
            # Removed delay - images come from CDN, not API
            # time.sleep(0.1)  # Rate limiting
    
    # Download missing large images
    if missing_large:
        print(f"\n📥 Downloading {len(missing_large)} large images...")
        for i, item in enumerate(missing_large, 1):
            card = item['card']
            name = card.get('name', 'Unknown')
            number = item['number']
            print(f"   [{i}/{len(missing_large)}] {name} (#{number})")
            
            if download_image(item['url'], item['path']):
                print(f"      ✅ Downloaded large image")
            else:
                print(f"      ❌ Failed to download large image")
            
            # Removed delay - images come from CDN, not API
            # time.sleep(0.1)  # Rate limiting
    
    print(f"\n✅ Download complete!")
    print(f"   Images saved to: {set_dir}")

def find_all_missing_images():
    """Scan all sets and find missing images"""
    print("🔍 Scanning all sets for missing images...")
    print("=" * 60)
    
    # Get all sets
    response = requests.get(f"{API_BASE}/sets", headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch sets: {response.status_code}")
        return
    
    sets = response.json().get('data', [])
    print(f"📦 Found {len(sets)} sets")
    
    missing_by_set = {}
    
    for set_data in sets:
        set_id = set_data.get('id')
        set_name = set_data.get('name')
        
        print(f"\n🔍 Checking {set_name} ({set_id})...")
        
        # Get cards for this set
        cards = get_cards_for_set(set_id)
        
        if not cards:
            continue
        
        set_dir = IMAGES_BASE_DIR / set_id
        missing_count = 0
        
        for card in cards:
            number = sanitize_card_number(card.get('number', ''))
            small_path = set_dir / 'small' / f"{number}.png"
            large_path = set_dir / 'large' / f"{number}.png"
            
            if not small_path.exists() or not large_path.exists():
                missing_count += 1
        
        if missing_count > 0:
            missing_by_set[set_id] = {
                'name': set_name,
                'missing': missing_count,
                'total': len(cards)
            }
            print(f"   ⚠️  Missing {missing_count}/{len(cards)} cards")
        else:
            print(f"   ✅ All images present")
        
        time.sleep(0.2)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY - Sets with missing images:")
    print("=" * 60)
    
    if not missing_by_set:
        print("✅ All sets have complete images!")
    else:
        for set_id, info in sorted(missing_by_set.items(), key=lambda x: x[1]['missing'], reverse=True):
            print(f"   {info['name']} ({set_id}): {info['missing']}/{info['total']} missing")
    
    return missing_by_set

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Download missing Pokemon TCG card images')
    parser.add_argument('--set', type=str, help='Specific set ID to check (e.g., swsh12pt5gg)')
    parser.add_argument('--scan', action='store_true', help='Scan all sets and show summary')
    parser.add_argument('--force', action='store_true', help='Force re-download even if files exist')
    parser.add_argument('--download-all', action='store_true', help='Download all missing images for all sets')
    
    args = parser.parse_args()
    
    try:
        if args.scan:
            missing_by_set = find_all_missing_images()
            
        elif args.download_all:
            missing_by_set = find_all_missing_images()
            
            if missing_by_set:
                print(f"\n📥 Starting download for {len(missing_by_set)} sets...")
                for set_id in missing_by_set.keys():
                    check_and_download_missing_images(set_id, force_download=True)
            
        elif args.set:
            check_and_download_missing_images(args.set, force_download=args.force)
            
        else:
            # Interactive mode - ask for set ID
            print("🃏 Pokemon TCG Image Downloader")
            print("=" * 60)
            print("\nOptions:")
            print("1. Download missing images for a specific set")
            print("2. Scan all sets and show summary")
            print("3. Download ALL missing images")
            
            choice = input("\nEnter choice (1-3): ")
            
            if choice == '1':
                set_id = input("Enter set ID (e.g., swsh12pt5gg): ").strip()
                if set_id:
                    check_and_download_missing_images(set_id, force_download=args.force)
            elif choice == '2':
                find_all_missing_images()
            elif choice == '3':
                missing_by_set = find_all_missing_images()
                if missing_by_set:
                    response = input(f"\n📥 Download images for {len(missing_by_set)} sets? (y/n): ")
                    if response.lower() == 'y':
                        for set_id in missing_by_set.keys():
                            check_and_download_missing_images(set_id, force_download=True)
            
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
