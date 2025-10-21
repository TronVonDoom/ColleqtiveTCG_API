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

# Database path
DB_PATH = Path(__file__).parent / "pokemontcg.db"

# Hosted image base (Hostinger)
HOSTED_IMAGES_BASE = "https://lime-goat-951061.hostingersite.com/pokemon-tcg-data"


def build_card_images(card_data):
    """Build images object from card database columns with hosted URLs"""
    set_id = card_data.get('set_id', '')
    number = card_data.get('number', '')
    
    if set_id and number:
        # Use hosted URLs
        card_data['images'] = {
            'small': f"{HOSTED_IMAGES_BASE}/images/cards/{set_id}/{number}.png",
            'large': f"{HOSTED_IMAGES_BASE}/images/cards/{set_id}/{number}_hires.png"
        }
    
    # Clean up the old database columns
    card_data.pop('image_small', None)
    card_data.pop('image_large', None)
    
    return card_data


def build_set_images(set_data):
    """Build images object from set database columns with hosted URLs"""
    set_id = set_data.get('id', '')
    
    if set_id:
        # Use hosted URLs
        set_data['images'] = {
            'symbol': f"{HOSTED_IMAGES_BASE}/images/sets/symbols/{set_id}_symbol.png",
            'logo': f"{HOSTED_IMAGES_BASE}/images/sets/logos/{set_id}_logo.png"
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
    type: Optional[str] = Query(None, description="Filter by Pokemon type")
):
    """Get Pokemon TCG cards with filtering and pagination"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        if name:
            where_clauses.append("name LIKE ?")
            params.append(f"%{name}%")
        if supertype:
            where_clauses.append("supertype = ?")
            params.append(supertype)
        if subtype:
            where_clauses.append("subtypes LIKE ?")
            params.append(f"%{subtype}%")
        if set_id:
            where_clauses.append("set_id = ?")
            params.append(set_id)
        if rarity:
            where_clauses.append("rarity = ?")
            params.append(rarity)
        if type:
            where_clauses.append("types LIKE ?")
            params.append(f"%{type}%")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM cards WHERE {where_sql}", params)
        total_count = cursor.fetchone()[0]
        
        # Calculate offset
        offset = (page - 1) * pageSize
        
        # Get cards
        cursor.execute(f"""
            SELECT * FROM cards 
            WHERE {where_sql}
            ORDER BY set_id, number
            LIMIT ? OFFSET ?
        """, params + [pageSize, offset])
        
        cards = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Parse JSON fields and build images
        for card in cards:
            for field in ['attacks', 'weaknesses', 'resistances', 'abilities', 'rules', 'legalities']:
                if card.get(field):
                    try:
                        card[field] = json.loads(card[field])
                    except:
                        pass
            # Parse list fields
            for field in ['types', 'subtypes', 'retreat_cost']:
                if card.get(field):
                    try:
                        card[field] = json.loads(card[field])
                    except:
                        pass
            # Build images from image_small and image_large with hosted URLs
            build_card_images(card)
        
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
        
        # Parse JSON fields
        for field in ['attacks', 'weaknesses', 'resistances', 'abilities', 'rules', 'legalities']:
            if card.get(field):
                try:
                    card[field] = json.loads(card[field])
                except:
                    pass
        # Parse list fields
        for field in ['types', 'subtypes', 'retreat_cost']:
            if card.get(field):
                try:
                    card[field] = json.loads(card[field])
                except:
                    pass
        # Build images from image_small and image_large with hosted URLs
        build_card_images(card)
        
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

    Example: /proxy-image/base1/logo.png -> https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/base1/logo.png
    """
    try:
        # Redirect to your Hostinger-hosted images instead of pokemontcg.io
        image_url = f"{HOSTED_IMAGES_BASE}/images/{image_path}"
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
