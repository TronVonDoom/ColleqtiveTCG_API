import requests

API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
headers = {'X-Api-Key': API_KEY}

r = requests.get('https://api.pokemontcg.io/v2/sets', headers=headers)
sets = r.json()['data']

print("All E-Card sets:")
for s in sets:
    if 'card' in s['name'].lower() or 'e-card' in s['series'].lower() or s['id'].startswith('ecard'):
        print(f"{s['id']} - {s['name']} ({s['series']})")
