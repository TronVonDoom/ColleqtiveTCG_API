import sqlite3

conn = sqlite3.connect('pokemontcg/pokemontcg.db')
cursor = conn.cursor()

# Check sv10 set
print("=== SV10 Set (Surging Sparks) ===")
cursor.execute("SELECT name, number, set_id FROM cards WHERE set_id = 'sv10' ORDER BY id LIMIT 15")
for row in cursor.fetchall():
    print(f"{row[0]}: #{row[1]} (Set: {row[2]})")

print("\n=== Cards that might have 001 ===")
cursor.execute("SELECT name, number, set_id FROM cards WHERE number IN ('1', '01', '001') LIMIT 10")
for row in cursor.fetchall():
    print(f"{row[0]}: #{row[1]} (Set: {row[2]})")

conn.close()
