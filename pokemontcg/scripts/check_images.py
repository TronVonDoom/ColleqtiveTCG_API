import sqlite3
import json

# Check database structure
conn = sqlite3.connect('pokemon_tcg.db')
c = conn.cursor()

# Get tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables in database:", [t[0] for t in tables])

# Check if cards table exists and what columns it has
if ('cards',) in tables:
    c.execute("PRAGMA table_info(cards)")
    columns = c.fetchall()
    print("\nCards table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if image data exists
    c.execute("SELECT id, images_small, images_large FROM cards LIMIT 5")
    print("\nSample image data from database:")
    for row in c.fetchall():
        print(f"  {row[0]}: small={row[1]}, large={row[2]}")

conn.close()

# Check JSON data
print("\n" + "="*50)
print("Sample image data from JSON files:")
data = json.load(open('pokemontcg/pokemon-tcg-data/cards/en/base1.json', 'r', encoding='utf-8'))
for i, card in enumerate(data[:3]):
    print(f"\nCard {i+1}: {card['name']} ({card['id']})")
    if 'images' in card:
        print(f"  Small: {card['images'].get('small')}")
        print(f"  Large: {card['images'].get('large')}")
