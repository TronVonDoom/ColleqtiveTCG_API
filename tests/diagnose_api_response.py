"""
Quick diagnostic to show what the API returns
"""
import sqlite3
import json
from pathlib import Path

# Simulate what the API does
DB_PATH = Path(__file__).parent.parent / "pokemon_tcg.db"
HOSTED_IMAGES_BASE = "https://www.colleqtivetcg.com/tcg-images/pokemon"

def build_card_images(card_data):
    """Build images object from card database columns with hosted URLs"""
    set_id = card_data.get('set_id', '')
    number = card_data.get('number', '')
    
    if set_id and number:
        card_data['images'] = {
            'small': f"{HOSTED_IMAGES_BASE}/images/cards/{set_id}/{number}.png",
            'large': f"{HOSTED_IMAGES_BASE}/images/cards/{set_id}/{number}_hires.png"
        }
    
    card_data.pop('image_small', None)
    card_data.pop('image_large', None)
    
    return card_data

def build_set_images(set_data):
    """Build images object from set database columns with hosted URLs"""
    set_id = set_data.get('id', '')
    
    if set_id:
        set_data['images'] = {
            'symbol': f"{HOSTED_IMAGES_BASE}/images/sets/symbols/{set_id}_symbol.png",
            'logo': f"{HOSTED_IMAGES_BASE}/images/sets/logos/{set_id}_logo.png"
        }
    
    set_data.pop('symbol_url', None)
    set_data.pop('logo_url', None)
    
    return set_data

# Test with actual database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get one card
print("=" * 80)
print("SAMPLE CARD API RESPONSE")
print("=" * 80)
cursor.execute("SELECT * FROM cards LIMIT 1")
row = cursor.fetchone()
if row:
    card = dict(zip(row.keys(), row))
    build_card_images(card)
    print("\nCard ID:", card.get('id'))
    print("Card Name:", card.get('name'))
    print("\nIMAGES OBJECT:")
    print(json.dumps(card.get('images', {}), indent=2))

# Get one set
print("\n" + "=" * 80)
print("SAMPLE SET API RESPONSE")
print("=" * 80)
cursor.execute("SELECT * FROM sets LIMIT 1")
row = cursor.fetchone()
if row:
    set_data = dict(zip(row.keys(), row))
    build_set_images(set_data)
    print("\nSet ID:", set_data.get('id'))
    print("Set Name:", set_data.get('name'))
    print("\nIMAGES OBJECT:")
    print(json.dumps(set_data.get('images', {}), indent=2))

conn.close()

print("\n" + "=" * 80)
print("HOW TO ACCESS IN JAVASCRIPT:")
print("=" * 80)
print("""
// For cards:
const smallImage = card.images.small;
const largeImage = card.images.large;

// For sets:
const setLogo = set.images.logo;
const setSymbol = set.images.symbol;

// NOT this (old way):
const smallImage = card.image_small;  // ❌ This won't work anymore
const setLogo = set.logo_url;          // ❌ This won't work anymore
""")
