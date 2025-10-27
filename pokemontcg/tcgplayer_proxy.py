"""
TCGplayer Proxy Endpoints
Proxies requests to TCGCSV.com to avoid CORS issues in the browser
"""
from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any

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
        response = await client.get(
            url,
            headers={'User-Agent': 'ColleqtiveTCG/1.0'},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

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
        data = await fetch_from_tcgcsv(f'https://tcgcsv.com/tcgplayer/3/groups/{group_id}/products')
        tcgplayer_cache[cache_key] = (data, datetime.now())
        return data
    except Exception as e:
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
        data = await fetch_from_tcgcsv(f'https://tcgcsv.com/tcgplayer/3/groups/{group_id}/prices')
        tcgplayer_cache[cache_key] = (data, datetime.now())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prices: {str(e)}")
