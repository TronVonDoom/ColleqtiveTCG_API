"""
Quick test to verify Pokemon TCG API connectivity
"""
import requests
import time

API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
BASE_URL = 'https://api.pokemontcg.io/v2'
headers = {'X-Api-Key': API_KEY}

print("Testing Pokemon TCG API connectivity...")
print("=" * 60)

# Test 1: Simple ping
print("\n1. Testing API availability (types endpoint)...")
start = time.time()
try:
    response = requests.get(f'{BASE_URL}/types', headers=headers, timeout=10)
    elapsed = time.time() - start
    print(f"   ✓ Response received in {elapsed:.2f} seconds")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Data: {data}")
except requests.exceptions.Timeout:
    print(f"   ✗ TIMEOUT after 10 seconds")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 2: Test without API key
print("\n2. Testing without API key...")
start = time.time()
try:
    response = requests.get(f'{BASE_URL}/types', timeout=10)
    elapsed = time.time() - start
    print(f"   ✓ Response received in {elapsed:.2f} seconds")
    print(f"   Status: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"   ✗ TIMEOUT after 10 seconds")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 3: Small cards request
print("\n3. Testing cards endpoint (1 card)...")
start = time.time()
try:
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params={'pageSize': 1},
        timeout=10
    )
    elapsed = time.time() - start
    print(f"   ✓ Response received in {elapsed:.2f} seconds")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            card = data['data'][0]
            print(f"   Card: {card.get('name')} ({card.get('id')})")
except requests.exceptions.Timeout:
    print(f"   ✗ TIMEOUT after 10 seconds")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("If all tests timeout, check your network/firewall/VPN")
print("If tests work but sync fails, the issue is in the sync script")
print("=" * 60)
