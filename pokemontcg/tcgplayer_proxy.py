"""
TCGplayer Proxy Endpoints
Proxies requests to TCGCSV.com to avoid CORS issues in the browser
"""
from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any, Optional

# Create router for TCGplayer endpoints
router = APIRouter(prefix="/api/tcgplayer", tags=["tcgplayer"])

# Cache for TCGplayer data
tcgplayer_cache: Dict[str, Tuple[Any, datetime]] = {}
CACHE_DURATION = timedelta(hours=24)

def is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid"""
    if cache_key not in tcgplayer_cache:
        return False
    _, timestamp = tcgplayer_cache[cache_key]
    return datetime.now() - timestamp < CACHE_DURATION

async def fetch_from_tcgcsv(url: str) -> dict:
    """Fetch data from TCGCSV with proper headers"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers={'User-Agent': 'ColleqtiveTCG/1.0'},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ TCGCSV HTTP error {e.response.status_code} for URL: {url}")
            print(f"   Response: {e.response.text[:500]}")  # First 500 chars of response
            raise
        except Exception as e:
            print(f"❌ Error fetching from TCGCSV: {str(e)}")
            raise

@router.get("/groups")
async def get_tcgplayer_groups():
    """
    Get all Pokemon TCG groups (sets) from TCGplayer
    Cached for 24 hours
    """
    cache_key = 'groups'
    
    if is_cache_valid(cache_key):
        cached_data, _ = tcgplayer_cache[cache_key]
        return cached_data
    
    try:
        data = await fetch_from_tcgcsv('https://tcgcsv.com/tcgplayer/3/groups')
        tcgplayer_cache[cache_key] = (data, datetime.now())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching groups: {str(e)}")

@router.get("/groups/{group_id}/products")
async def get_tcgplayer_products(group_id: int):
    """
    Get all products (cards) for a specific TCGplayer group
    Cached for 24 hours
    """
    cache_key = f'products_{group_id}'
    
    if is_cache_valid(cache_key):
        cached_data, _ = tcgplayer_cache[cache_key]
        return cached_data
    
    try:
        # Correct TCGCSV format: /tcgplayer/{categoryId}/{groupId}/products
        data = await fetch_from_tcgcsv(f'https://tcgcsv.com/tcgplayer/3/{group_id}/products')
        tcgplayer_cache[cache_key] = (data, datetime.now())
        return data
    except httpx.HTTPStatusError as e:
        # If TCGCSV returns 404, it means no products for this group
        if e.response.status_code == 404:
            print(f"⚠️ No products found for group {group_id} on TCGCSV")
            return {"results": []}
        raise HTTPException(status_code=e.response.status_code, detail=f"TCGCSV error: {str(e)}")
    except Exception as e:
        print(f"❌ Error fetching products for group {group_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@router.get("/groups/{group_id}/prices")
async def get_tcgplayer_prices(group_id: int):
    """
    Get pricing data for all products in a TCGplayer group
    Cached for 24 hours
    """
    cache_key = f'prices_{group_id}'
    
    if is_cache_valid(cache_key):
        cached_data, _ = tcgplayer_cache[cache_key]
        return cached_data
    
    try:
        # Correct TCGCSV format: /tcgplayer/{categoryId}/{groupId}/prices
        data = await fetch_from_tcgcsv(f'https://tcgcsv.com/tcgplayer/3/{group_id}/prices')
        tcgplayer_cache[cache_key] = (data, datetime.now())
        return data
    except httpx.HTTPStatusError as e:
        # If TCGCSV returns 404, it means no prices for this group
        if e.response.status_code == 404:
            print(f"⚠️ No prices found for group {group_id} on TCGCSV")
            return {"results": []}
        raise HTTPException(status_code=e.response.status_code, detail=f"TCGCSV error: {str(e)}")
    except Exception as e:
        print(f"❌ Error fetching prices for group {group_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching prices: {str(e)}")

@router.get("/check-card-mapping/{set_id}/{card_number}")
async def check_card_mapping(set_id: str, card_number: str):
    """
    Check if a specific card from our database can be found in TCGplayer
    Returns mapping status and potential matches
    """
    try:
        # Load the set mapping
        import json
        from pathlib import Path
        
        mapping_path = Path(__file__).parent.parent / "data" / "pokemon" / "tcgplayer-set-mapping.json"
        with open(mapping_path, 'r') as f:
            set_mapping = json.load(f)
        
        if set_id not in set_mapping:
            raise HTTPException(status_code=404, detail=f"Set {set_id} not mapped to TCGplayer")
        
        group_id = set_mapping[set_id]['tcgplayerGroupId']
        
        # Load card data from our database
        cards_path = Path(__file__).parent.parent / "data" / "pokemon" / "cards" / "en" / f"{set_id}.json"
        with open(cards_path, 'r') as f:
            our_cards = json.load(f)
        
        # Find the specific card
        our_card = next((c for c in our_cards if c.get('number') == card_number), None)
        if not our_card:
            raise HTTPException(status_code=404, detail=f"Card {card_number} not found in set {set_id}")
        
        # Fetch TCGplayer products for this set
        tcg_products = await get_tcgplayer_products(group_id)
        tcg_cards = tcg_products.get('results', [])
        
        # Normalize and search for matches
        def normalize_name(name):
            return name.lower().replace('-', ' ').replace("'", "").replace('.', '').strip()
        
        our_name_normalized = normalize_name(our_card['name'])
        
        # Find potential matches
        exact_matches = [tc for tc in tcg_cards if normalize_name(tc['name']) == our_name_normalized]
        partial_matches = [tc for tc in tcg_cards if our_name_normalized in normalize_name(tc['name']) or normalize_name(tc['name']) in our_name_normalized]
        
        return {
            "set_id": set_id,
            "card_number": card_number,
            "card_name": our_card['name'],
            "tcgplayer_group_id": group_id,
            "tcgplayer_group_name": set_mapping[set_id]['tcgplayerGroupName'],
            "mapping_status": "found" if exact_matches else "not_found",
            "exact_matches": len(exact_matches),
            "exact_match_details": exact_matches[:5] if exact_matches else [],
            "partial_matches": len(partial_matches),
            "partial_match_details": partial_matches[:5] if partial_matches else [],
            "total_products_in_set": len(tcg_cards)
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking card mapping: {str(e)}")

@router.get("/unmapped-cards")
async def get_unmapped_cards(set_id: Optional[str] = None, limit: int = 100):
    """
    Get a list of cards that cannot be found in TCGplayer
    Optionally filter by set_id
    """
    try:
        import json
        from pathlib import Path
        
        # Load the set mapping
        mapping_path = Path(__file__).parent.parent / "data" / "pokemon" / "tcgplayer-set-mapping.json"
        with open(mapping_path, 'r') as f:
            set_mapping = json.load(f)
        
        cards_dir = Path(__file__).parent.parent / "data" / "pokemon" / "cards" / "en"
        
        # Determine which sets to check
        sets_to_check = [set_id] if set_id else list(set_mapping.keys())
        
        unmapped_cards = []
        
        for sid in sets_to_check:
            if sid not in set_mapping:
                continue
            
            cards_path = cards_dir / f"{sid}.json"
            if not cards_path.exists():
                continue
            
            with open(cards_path, 'r') as f:
                our_cards = json.load(f)
            
            group_id = set_mapping[sid]['tcgplayerGroupId']
            
            # Fetch TCGplayer products
            tcg_products = await get_tcgplayer_products(group_id)
            tcg_cards = tcg_products.get('results', [])
            
            if not tcg_cards:
                # If no TCGplayer products, all cards are unmapped
                for card in our_cards:
                    unmapped_cards.append({
                        "set_id": sid,
                        "set_name": set_mapping[sid]['setName'],
                        "card_id": card['id'],
                        "card_name": card['name'],
                        "card_number": card.get('number'),
                        "rarity": card.get('rarity'),
                        "reason": "no_tcgplayer_products"
                    })
                continue
            
            # Check each card
            def normalize_name(name):
                return name.lower().replace('-', ' ').replace("'", "").replace('.', '').strip()
            
            tcg_names = {normalize_name(tc['name']) for tc in tcg_cards}
            
            for card in our_cards:
                our_name = normalize_name(card['name'])
                if our_name not in tcg_names:
                    unmapped_cards.append({
                        "set_id": sid,
                        "set_name": set_mapping[sid]['setName'],
                        "card_id": card['id'],
                        "card_name": card['name'],
                        "card_number": card.get('number'),
                        "rarity": card.get('rarity'),
                        "reason": "name_not_found"
                    })
            
            # Limit results if needed
            if len(unmapped_cards) >= limit:
                break
        
        return {
            "total_unmapped": len(unmapped_cards),
            "limit": limit,
            "unmapped_cards": unmapped_cards[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching unmapped cards: {str(e)}")


@router.get("/card-variants/{group_id}/{card_name}")
async def get_card_variants(group_id: int, card_name: str, card_number: Optional[str] = None):
    """
    Get all variants (Normal, Holofoil, Reverse Holofoil, etc.) for a specific card
    Returns all TCGplayer products that match the card name with their individual pricing
    """
    try:
        # Fetch all products for this set
        products_response = await get_tcgplayer_products(group_id)
        products = products_response.get('results', [])
        
        if not products:
            return {
                "card_name": card_name,
                "card_number": card_number,
                "variants": []
            }
        
        # Fetch all prices for this set
        prices_response = await get_tcgplayer_prices(group_id)
        prices = prices_response.get('results', [])
        
        # Create a price lookup map
        price_map = {p['productId']: p for p in prices}
        
        # Normalize card name for matching
        def normalize_name(name):
            return name.lower().replace('-', ' ').replace("'", "").replace('.', '').strip()
        
        search_name = normalize_name(card_name)
        
        # Find all products that match this card
        matching_products = []
        
        for product in products:
            product_name = normalize_name(product['name'].split('-')[0].strip())
            
            # Check if names match
            name_matches = product_name == search_name or search_name in product_name
            
            # If card number provided, verify it matches
            if card_number and product.get('extendedData'):
                number_data = next((d for d in product['extendedData'] if d['name'] == 'Number'), None)
                if number_data and number_data.get('value') != card_number:
                    continue
            
            if name_matches:
                # Get pricing for this variant
                pricing = price_map.get(product['productId'])
                
                # Extract variant type from subTypeName in pricing
                variant_type = pricing.get('subTypeName', 'Normal') if pricing else 'Unknown'
                
                matching_products.append({
                    'product_id': product['productId'],
                    'name': product['name'],
                    'url': product.get('url', f"https://www.tcgplayer.com/product/{product['productId']}"),
                    'image_url': product.get('imageUrl'),
                    'variant_type': variant_type,
                    'pricing': {
                        'market_price': pricing.get('marketPrice'),
                        'low_price': pricing.get('lowPrice'),
                        'mid_price': pricing.get('midPrice'),
                        'high_price': pricing.get('highPrice'),
                        'direct_low_price': pricing.get('directLowPrice'),
                    } if pricing else None,
                    'extended_data': product.get('extendedData', [])
                })
        
        # Sort by market price (highest to lowest)
        matching_products.sort(
            key=lambda x: x['pricing']['market_price'] if x['pricing'] and x['pricing']['market_price'] else 0,
            reverse=True
        )
        
        return {
            "card_name": card_name,
            "card_number": card_number,
            "group_id": group_id,
            "total_variants": len(matching_products),
            "variants": matching_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching card variants: {str(e)}")


@router.get("/card-variants-by-set/{set_id}/{card_number}")
async def get_card_variants_by_set(set_id: str, card_number: str):
    """
    Get all variants for a card by set ID and card number
    This is a convenience endpoint that combines set mapping lookup with variant search
    """
    try:
        import json
        from pathlib import Path
        
        # Load the set mapping
        mapping_path = Path(__file__).parent.parent / "data" / "pokemon" / "tcgplayer-set-mapping.json"
        with open(mapping_path, 'r') as f:
            set_mapping = json.load(f)
        
        if set_id not in set_mapping:
            raise HTTPException(status_code=404, detail=f"Set {set_id} not found in mapping")
        
        # Load card data to get the card name
        cards_path = Path(__file__).parent.parent / "data" / "pokemon" / "cards" / "en" / f"{set_id}.json"
        with open(cards_path, 'r') as f:
            cards = json.load(f)
        
        card = next((c for c in cards if c.get('number') == card_number), None)
        if not card:
            raise HTTPException(status_code=404, detail=f"Card {card_number} not found in set {set_id}")
        
        group_id = set_mapping[set_id]['tcgplayerGroupId']
        
        # Get variants using the card name and number
        return await get_card_variants(group_id, card['name'], card_number)
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching card variants: {str(e)}")
