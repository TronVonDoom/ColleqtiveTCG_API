"""
Quick script to check if a set exists in Pokemon TCG API and if it has images
"""
import requests
import sys

API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
BASE_URL = 'https://api.pokemontcg.io/v2'
HEADERS = {'X-Api-Key': API_KEY} if API_KEY else {}

def check_set(set_id):
    """Check if a set exists and has image data"""
    print(f"\n🔍 Checking set: {set_id}")
    print("=" * 60)
    
    # Check set info
    print("\n1. Set Information:")
    response = requests.get(f"{BASE_URL}/sets/{set_id}", headers=HEADERS)
    
    if response.status_code == 404:
        print(f"   ❌ Set '{set_id}' NOT FOUND in Pokemon TCG API")
        return False
    elif response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        return False
    
    set_data = response.json().get('data', {})
    print(f"   ✅ Set exists: {set_data.get('name', 'Unknown')}")
    print(f"   Total cards: {set_data.get('total', 0)}")
    print(f"   Release date: {set_data.get('releaseDate', 'Unknown')}")
    
    # Check first few cards
    print("\n2. Sample Cards:")
    response = requests.get(
        f"{BASE_URL}/cards",
        headers=HEADERS,
        params={'q': f'set.id:{set_id}', 'pageSize': 5}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Error fetching cards: {response.status_code}")
        return False
    
    cards_data = response.json().get('data', [])
    
    if not cards_data:
        print(f"   ⚠️  No cards found for this set")
        return False
    
    print(f"   Found {len(cards_data)} sample cards:")
    
    has_images = False
    for card in cards_data[:3]:  # Check first 3
        name = card.get('name', 'Unknown')
        number = card.get('number', '?')
        images = card.get('images', {})
        small = images.get('small')
        large = images.get('large')
        
        print(f"\n   Card: {name} (#{number})")
        if small:
            print(f"      Small: ✅ {small}")
            has_images = True
        else:
            print(f"      Small: ❌ No URL")
        
        if large:
            print(f"      Large: ✅ {large}")
            has_images = True
        else:
            print(f"      Large: ❌ No URL")
    
    if not has_images:
        print("\n   ⚠️  WARNING: No cards have image URLs!")
        print("   This set may not have images available in the API")
    
    return has_images

def search_similar_sets(search_term):
    """Search for sets with similar names"""
    print(f"\n🔍 Searching for sets containing: '{search_term}'")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/sets", headers=HEADERS, params={'pageSize': 250})
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return
    
    all_sets = response.json().get('data', [])
    
    matches = [s for s in all_sets if search_term.lower() in s.get('name', '').lower() or 
                                       search_term.lower() in s.get('id', '').lower()]
    
    if not matches:
        print(f"   ❌ No sets found matching '{search_term}'")
        return
    
    print(f"   Found {len(matches)} matching sets:\n")
    for s in matches:
        print(f"   • {s.get('id', 'unknown'):15} - {s.get('name', 'Unknown')} ({s.get('releaseDate', 'N/A')})")

if __name__ == '__main__':
    # Check the problematic set
    set_id = 'me1'
    
    if len(sys.argv) > 1:
        set_id = sys.argv[1]
    
    exists = check_set(set_id)
    
    if not exists:
        print("\n" + "=" * 60)
        print("💡 Searching for similar sets...")
        search_similar_sets('mega')
        search_similar_sets('evolution')
    
    print("\n" + "=" * 60)
    print("Done!")
