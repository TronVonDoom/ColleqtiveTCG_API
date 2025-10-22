"""Quick verification of energy card rarities"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "pokemontcg" / "pokemontcg.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name, set_id, number, supertype, rarity 
    FROM cards 
    WHERE supertype = 'Energy' 
    LIMIT 10
""")

print("\nSample Energy Cards:")
print("="*100)
for card in cursor.fetchall():
    print(f"{card[0]:<20} | {card[1]:<25} | {card[2]:<10} | {card[3]:>4} | Rarity: {card[5]}")

# Count total energy cards with Energy rarity
cursor.execute("SELECT COUNT(*) FROM cards WHERE supertype = 'Energy' AND rarity = 'Energy'")
count = cursor.fetchone()[0]
print(f"\n✓ Total Energy cards with rarity 'Energy': {count}")

conn.close()
