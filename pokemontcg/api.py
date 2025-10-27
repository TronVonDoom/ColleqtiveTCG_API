"""
Pokemon TCG API - FastAPI application
Serves Pokemon TCG data from the local SQLite database
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import sqlite3
import json
from pathlib import Path
from fastapi.responses import RedirectResponse

# Import TCGplayer proxy router
from .tcgplayer_proxy import router as tcgplayer_router

app = FastAPI(
    title="Pokemon TCG API",
    description="API for querying Pokemon Trading Card Game data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include TCGplayer proxy routes
app.include_router(tcgplayer_router)

# Database path
DB_PATH = Path(__file__).parent / "pokemontcg.db"

# Hosted image base (Hostinger)
HOSTED_IMAGES_BASE = "https://www.colleqtivetcg.com/tcg-images/pokemon"


def build_card_images(card_data):
    """Build images object from card database columns with hosted URLs.
    
    Uses card numbers as-is to match file naming on server.
    Falls back to Pokemon card back placeholder if images don't exist.
    """
    set_id = card_data.get('set_id', '')
    number = card_data.get('number', '')
    
    if set_id and number:
        # Keep card number as-is - no leading zero stripping
        # Some cards have formats like "123/456" - just use the first part
        clean_number = number.split('/')[0]
        
        # Images are now stored directly in set folder without /small/ or /large/ subdirectories
        # Path structure: /tcg-images/pokemon/en/cards/{setId}/{number}.webp
        image_url = f"{HOSTED_IMAGES_BASE}/en/cards/{set_id}/{clean_number}.webp"
        card_data['images'] = {
            'small': image_url,
            'large': image_url  # Same file for both since we don't have separate sizes anymore
        }
    else:
        # Fallback to placeholder if no set_id or number
        card_data['images'] = {
            'small': f"{HOSTED_IMAGES_BASE}/en/cards/placeholder-card-back.webp",
            'large': f"{HOSTED_IMAGES_BASE}/en/cards/placeholder-card-back.webp"
        }
    
    # Clean up the old database columns
    card_data.pop('image_small', None)
    card_data.pop('image_large', None)
    
    return card_data


def build_set_images(set_data):
    """Build images object from set database columns with hosted URLs"""
    set_id = set_data.get('id', '')
    
    if set_id:
        # Images are stored in /tcg-images/pokemon/en/sets/{setId}/{type}.webp
        set_data['images'] = {
            'symbol': f"{HOSTED_IMAGES_BASE}/en/sets/{set_id}/symbol.webp",
            'logo': f"{HOSTED_IMAGES_BASE}/en/sets/{set_id}/logo.webp"
        }
    
    # Clean up the old database columns
    set_data.pop('symbol_url', None)
    set_data.pop('logo_url', None)
    
    return set_data


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    """Convert SQLite row to dictionary"""
    return dict(zip(row.keys(), row))


def to_camel_case(snake_str):
    """Convert snake_case string to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_keys_to_camel_case(data):
    """Recursively convert dictionary keys from snake_case to camelCase"""
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # Don't convert keys that should stay as-is
            if key in ['id', 'name', 'hp', 'level', 'number', 'artist', 'rarity', 'series', 'total', 'types', 'subtypes', 'supertypes']:
                new_key = key
            else:
                new_key = to_camel_case(key)
            new_dict[new_key] = convert_keys_to_camel_case(value)
        return new_dict
    elif isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    else:
        return data


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Pokemon TCG API",
        "version": "1.0.0",
        "endpoints": {
            "cards": "/cards",
            "card_by_id": "/cards/{card_id}",
            "sets": "/sets",
            "set_by_id": "/sets/{set_id}",
            "types": "/types",
            "subtypes": "/subtypes",
            "supertypes": "/supertypes",
            "rarities": "/rarities",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards")
        card_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sets")
        set_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cards": card_count,
            "sets": set_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/sets")
async def get_sets(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=250, description="Number of sets per page")
):
    """Get all Pokemon TCG sets with pagination"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM sets")
        total_count = cursor.fetchone()[0]
        
        # Calculate offset
        offset = (page - 1) * pageSize
        
        # Get sets
        cursor.execute("""
            SELECT * FROM sets 
            ORDER BY release_date DESC
            LIMIT ? OFFSET ?
        """, (pageSize, offset))
        
        sets = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Build images object with hosted URLs
        for s in sets:
            if s.get('legalities'):
                s['legalities'] = json.loads(s['legalities'])
            # Build images from symbol_url and logo_url with hosted URLs
            build_set_images(s)
        
        # Convert to camelCase for frontend compatibility
        sets = [convert_keys_to_camel_case(s) for s in sets]
        
        conn.close()
        
        return {
            "data": sets,
            "page": page,
            "pageSize": pageSize,
            "count": len(sets),
            "totalCount": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sets/{set_id}")
async def get_set(set_id: str):
    """Get a specific set by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sets WHERE id = ?", (set_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Set '{set_id}' not found")
        
        set_data = dict_from_row(row)
        
        # Parse JSON fields and build images with hosted URLs
        if set_data.get('legalities'):
            set_data['legalities'] = json.loads(set_data['legalities'])
        # Build images from symbol_url and logo_url with hosted URLs
        build_set_images(set_data)
        
        # Convert to camelCase for frontend compatibility
        set_data = convert_keys_to_camel_case(set_data)
        
        conn.close()
        
        return {"data": set_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cards")
async def get_cards(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=250, description="Number of cards per page"),
    name: Optional[str] = Query(None, description="Filter by card name (partial match)"),
    supertype: Optional[str] = Query(None, description="Filter by supertype"),
    subtype: Optional[str] = Query(None, description="Filter by subtype"),
    set_id: Optional[str] = Query(None, description="Filter by set ID"),
    rarity: Optional[str] = Query(None, description="Filter by rarity"),
    type: Optional[str] = Query(None, description="Filter by Pokemon type"),
    sort: Optional[str] = Query("newest", description="Sort order: newest, oldest, name-asc, name-desc")
):
    """Get Pokemon TCG cards with filtering and pagination"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        # Determine if we need to join with card_types or card_subtypes
        needs_type_join = type is not None
        needs_subtype_join = subtype is not None
        
        # Base table reference
        table_ref = "cards c"
        joins = []
        
        if needs_type_join:
            joins.append("INNER JOIN card_types ct ON c.id = ct.card_id")
            where_clauses.append("ct.type_name = ?")
            params.append(type)
        
        if needs_subtype_join:
            joins.append("INNER JOIN card_subtypes cs ON c.id = cs.card_id")
            where_clauses.append("cs.subtype_name = ?")
            params.append(subtype)
        
        if name:
            where_clauses.append("c.name LIKE ?")
            params.append(f"%{name}%")
        if supertype:
            where_clauses.append("c.supertype = ?")
            params.append(supertype)
        if set_id:
            where_clauses.append("c.set_id = ?")
            params.append(set_id)
        if rarity:
            where_clauses.append("c.rarity = ?")
            params.append(rarity)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        join_sql = " ".join(joins) if joins else ""
        
        # Get total count - use DISTINCT since joins might create duplicates
        count_query = f"SELECT COUNT(DISTINCT c.id) FROM {table_ref} {join_sql} WHERE {where_sql}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Calculate offset
        offset = (page - 1) * pageSize
        
        # Determine ORDER BY clause based on sort parameter
        if sort == "oldest":
            # Oldest sets first, then by card number
            order_by = """ORDER BY c.set_id ASC, 
                         CAST(
                             CASE 
                                 WHEN c.number GLOB '[0-9]*' 
                                 THEN SUBSTR(c.number, 1, INSTR(c.number || '/', '/') - 1)
                                 ELSE c.number 
                             END AS INTEGER
                         ),
                         c.number"""
        elif sort == "name-asc":
            # Alphabetical A-Z
            order_by = "ORDER BY c.name ASC, c.set_id"
        elif sort == "name-desc":
            # Alphabetical Z-A
            order_by = "ORDER BY c.name DESC, c.set_id"
        else:  # "newest" is default
            # Newest sets first, then by card number (need to join with sets to get release_date)
            order_by = """ORDER BY (SELECT s.release_date FROM sets s WHERE s.id = c.set_id) DESC,
                         CAST(
                             CASE 
                                 WHEN c.number GLOB '[0-9]*' 
                                 THEN SUBSTR(c.number, 1, INSTR(c.number || '/', '/') - 1)
                                 ELSE c.number 
                             END AS INTEGER
                         ),
                         c.number"""
        
        # Get cards - use DISTINCT to avoid duplicates from joins
        cards_query = f"""
            SELECT DISTINCT c.* FROM {table_ref} 
            {join_sql}
            WHERE {where_sql}
            {order_by}
            LIMIT ? OFFSET ?
        """
        cursor.execute(cards_query, params + [pageSize, offset])
        
        cards = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Parse JSON fields and build images
        for card in cards:
            card_id = card['id']
            
            # Fetch types from the card_types relationship table
            cursor.execute("SELECT type_name FROM card_types WHERE card_id = ?", (card_id,))
            type_rows = cursor.fetchall()
            if type_rows:
                card['types'] = [row[0] for row in type_rows]
            
            # Fetch subtypes from the card_subtypes relationship table
            cursor.execute("SELECT subtype_name FROM card_subtypes WHERE card_id = ?", (card_id,))
            subtype_rows = cursor.fetchall()
            if subtype_rows:
                card['subtypes'] = [row[0] for row in subtype_rows]
            
            # Fetch attacks from attacks table
            cursor.execute("SELECT name, cost, converted_energy_cost, damage, text FROM attacks WHERE card_id = ? ORDER BY id", (card_id,))
            attack_rows = cursor.fetchall()
            if attack_rows:
                card['attacks'] = []
                for attack_row in attack_rows:
                    attack_dict = {
                        'name': attack_row[0],
                        'cost': json.loads(attack_row[1]) if attack_row[1] else [],
                        'convertedEnergyCost': attack_row[2],
                        'damage': attack_row[3],
                        'text': attack_row[4]
                    }
                    card['attacks'].append(attack_dict)
            
            # Fetch abilities from abilities table
            cursor.execute("SELECT name, text, ability_type FROM abilities WHERE card_id = ? ORDER BY id", (card_id,))
            ability_rows = cursor.fetchall()
            if ability_rows:
                card['abilities'] = []
                for ability_row in ability_rows:
                    ability_dict = {
                        'name': ability_row[0],
                        'text': ability_row[1],
                        'type': ability_row[2]
                    }
                    card['abilities'].append(ability_dict)
            
            # Fetch weaknesses from weaknesses table
            cursor.execute("SELECT type, value FROM weaknesses WHERE card_id = ?", (card_id,))
            weakness_rows = cursor.fetchall()
            if weakness_rows:
                card['weaknesses'] = [{'type': row[0], 'value': row[1]} for row in weakness_rows]
            
            # Fetch resistances from resistances table
            cursor.execute("SELECT type, value FROM resistances WHERE card_id = ?", (card_id,))
            resistance_rows = cursor.fetchall()
            if resistance_rows:
                card['resistances'] = [{'type': row[0], 'value': row[1]} for row in resistance_rows]
            
            # Parse JSON fields from card table
            for field in ['rules', 'retreat_cost', 'national_pokedex_numbers', 'evolves_to']:
                if card.get(field):
                    try:
                        card[field] = json.loads(card[field])
                    except:
                        pass
            
            # Fetch set information
            set_id = card.get('set_id')
            if set_id:
                cursor.execute("SELECT * FROM sets WHERE id = ?", (set_id,))
                set_row = cursor.fetchone()
                if set_row:
                    set_data = dict_from_row(set_row)
                    build_set_images(set_data)
                    card['set'] = convert_keys_to_camel_case(set_data)
            
            # Build images from image_small and image_large with hosted URLs
            build_card_images(card)
        
        # Convert all cards to camelCase
        cards = [convert_keys_to_camel_case(card) for card in cards]
        
        conn.close()
        
        return {
            "data": cards,
            "page": page,
            "pageSize": pageSize,
            "count": len(cards),
            "totalCount": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cards/{card_id}")
async def get_card(card_id: str):
    """Get a specific card by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Card '{card_id}' not found")
        
        card = dict_from_row(row)
        
        # Fetch types from the card_types relationship table
        cursor.execute("SELECT type_name FROM card_types WHERE card_id = ?", (card_id,))
        type_rows = cursor.fetchall()
        if type_rows:
            card['types'] = [row[0] for row in type_rows]
        
        # Fetch subtypes from the card_subtypes relationship table
        cursor.execute("SELECT subtype_name FROM card_subtypes WHERE card_id = ?", (card_id,))
        subtype_rows = cursor.fetchall()
        if subtype_rows:
            card['subtypes'] = [row[0] for row in subtype_rows]
        
        # Fetch attacks from attacks table
        cursor.execute("SELECT name, cost, converted_energy_cost, damage, text FROM attacks WHERE card_id = ? ORDER BY id", (card_id,))
        attack_rows = cursor.fetchall()
        if attack_rows:
            card['attacks'] = []
            for attack_row in attack_rows:
                attack_dict = {
                    'name': attack_row[0],
                    'cost': json.loads(attack_row[1]) if attack_row[1] else [],
                    'convertedEnergyCost': attack_row[2],
                    'damage': attack_row[3],
                    'text': attack_row[4]
                }
                card['attacks'].append(attack_dict)
        
        # Fetch abilities from abilities table
        cursor.execute("SELECT name, text, ability_type FROM abilities WHERE card_id = ? ORDER BY id", (card_id,))
        ability_rows = cursor.fetchall()
        if ability_rows:
            card['abilities'] = []
            for ability_row in ability_rows:
                ability_dict = {
                    'name': ability_row[0],
                    'text': ability_row[1],
                    'type': ability_row[2]
                }
                card['abilities'].append(ability_dict)
        
        # Fetch weaknesses from weaknesses table
        cursor.execute("SELECT type, value FROM weaknesses WHERE card_id = ?", (card_id,))
        weakness_rows = cursor.fetchall()
        if weakness_rows:
            card['weaknesses'] = [{'type': row[0], 'value': row[1]} for row in weakness_rows]
        
        # Fetch resistances from resistances table
        cursor.execute("SELECT type, value FROM resistances WHERE card_id = ?", (card_id,))
        resistance_rows = cursor.fetchall()
        if resistance_rows:
            card['resistances'] = [{'type': row[0], 'value': row[1]} for row in resistance_rows]
        
        # Parse JSON fields (rules, legalities, retreat_cost, etc.)
        for field in ['rules', 'retreat_cost', 'national_pokedex_numbers', 'evolves_to']:
            if card.get(field):
                try:
                    card[field] = json.loads(card[field])
                except:
                    pass
        
        # Fetch set information
        set_id = card.get('set_id')
        if set_id:
            cursor.execute("SELECT * FROM sets WHERE id = ?", (set_id,))
            set_row = cursor.fetchone()
            if set_row:
                set_data = dict_from_row(set_row)
                build_set_images(set_data)
                card['set'] = convert_keys_to_camel_case(set_data)
        
        # Build images from image_small and image_large with hosted URLs
        build_card_images(card)
        
        # Convert snake_case keys to camelCase for frontend compatibility
        card = convert_keys_to_camel_case(card)
        
        conn.close()
        
        return {"data": card}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/types")
async def get_types():
    """Get all Pokemon types"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM types ORDER BY name")
        types = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {"data": types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_card_id(card_id: str):
    """Parse a card id like 'base1-4' into (set_id, number)"""
    if '-' in card_id:
        parts = card_id.split('-')
        set_id = parts[0]
        number = parts[-1]
        return set_id, number
    # Fallback: try to look up in DB
    return None, None


@app.get("/cards/{card_id}/image/{size}")
async def card_image_redirect(card_id: str, size: str):
    """Redirect to hosted card image. size = small|large"""
    try:
        set_id, number = parse_card_id(card_id)
        if not set_id or not number:
            raise HTTPException(status_code=400, detail="Invalid card id format")

        # normalize number (some numbers include '/'; replace)
        filename = f"{number}.png" if size == 'small' else f"{number}_hires.png"
        url = f"{HOSTED_IMAGES_BASE}/images/cards/{set_id}/{filename}"

        return RedirectResponse(url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sets/{set_id}/symbol")
async def set_symbol_redirect(set_id: str):
    """Redirect to hosted set symbol image"""
    try:
        url = f"{HOSTED_IMAGES_BASE}/images/sets/symbols/{set_id}_symbol.png"
        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sets/{set_id}/logo")
async def set_logo_redirect(set_id: str):
    """Redirect to hosted set logo image"""
    try:
        url = f"{HOSTED_IMAGES_BASE}/images/sets/logos/{set_id}_logo.png"
        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/proxy-image/{image_path:path}")
async def proxy_image(image_path: str):
    """Redirect to Hostinger-hosted images. No CORS issues since images are on your domain.

    Example: /proxy-image/cards/base1/small/1.png -> https://www.colleqtivetcg.com/tcg-images/pokemon/cards/base1/small/1.png
    """
    try:
        # Redirect to your Hostinger-hosted images instead of pokemontcg.io
        image_url = f"{HOSTED_IMAGES_BASE}/{image_path}"
        return RedirectResponse(image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/subtypes")
async def get_subtypes():
    """Get all card subtypes"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM subtypes ORDER BY name")
        subtypes = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {"data": subtypes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/supertypes")
async def get_supertypes():
    """Get all card supertypes"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM supertypes ORDER BY name")
        supertypes = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {"data": supertypes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rarities")
async def get_rarities():
    """Get all card rarities"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM rarities ORDER BY name")
        rarities = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {"data": rarities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
