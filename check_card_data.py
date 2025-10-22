#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('pokemontcg/pokemontcg.db')
cursor = conn.cursor()

card_id = 'me1-6'

# Check attacks
cursor.execute('SELECT * FROM attacks WHERE card_id = ?', (card_id,))
attacks = cursor.fetchall()
print(f'Attacks found: {len(attacks)}')
for attack in attacks:
    print(f'  - Name: {attack[2]}, Damage: {attack[4]}, Cost: {attack[3]}')

# Check abilities  
cursor.execute('SELECT * FROM abilities WHERE card_id = ?', (card_id,))
abilities = cursor.fetchall()
print(f'\nAbilities found: {len(abilities)}')
for ability in abilities:
    print(f'  - Name: {ability[2]}, Type: {ability[4]}, Text: {ability[3][:50] if ability[3] else ""}...')

conn.close()
