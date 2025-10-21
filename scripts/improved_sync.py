"""
Improved Database Sync Script with better error handling and smaller batches
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import json
import time
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import (
    API_KEY, BASE_URL, DATABASE_URL,
    RATE_LIMIT_DELAY, MAX_RETRIES, RETRY_DELAY,
    INCLUDE_PRICING, LOG_LEVEL, LOG_FILE
)
from core.models import (
    Base, Set, Card, Attack, Ability, Weakness, Resistance,
    Type, Subtype, Supertype, Rarity, SyncStatus
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ImprovedPokemonTCGSync:
    """Improved Pokemon TCG API sync with better error handling"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.headers = {'X-Api-Key': API_KEY}
        # Use smaller batch size for better reliability
        self.batch_size = 25
        
    def init_database(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
        
    def make_request_powershell(self, endpoint, params=None, timeout=30):
        """Make API request using PowerShell with improved error handling"""
        url = f"{BASE_URL}/{endpoint}"
        
        # Add query parameters
        if params:
            query_parts = []
            for key, value in params.items():
                query_parts.append(f"{key}={value}")
            if query_parts:
                url += "?" + "&".join(query_parts)
        
        for attempt in range(MAX_RETRIES):
            try:
                # Build PowerShell command
                ps_cmd = f"$response = Invoke-WebRequest -Uri '{url}'"
                
                # Add headers
                for key, value in self.headers.items():
                    ps_cmd += f" -Headers @{{'{key}'='{value}'}}"
                
                ps_cmd += f" -TimeoutSec {timeout}"
                ps_cmd += "; $response.Content"
                
                logger.debug(f"Attempting request to: {url} (attempt {attempt + 1}/{MAX_RETRIES})")
                
                # Execute PowerShell command
                start_time = time.time()
                result = subprocess.run(
                    ['powershell', '-Command', ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 10  # Slightly longer than PowerShell timeout
                )
                elapsed = time.time() - start_time
                
                if result.returncode == 0:
                    # Check if we got actual content
                    if len(result.stdout.strip()) == 0:
                        logger.warning(f"Empty response from API (took {elapsed:.2f}s)")
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return None
                    
                    # Parse JSON response
                    try:
                        data = json.loads(result.stdout)
                        logger.debug(f"Successful request (took {elapsed:.2f}s)")
                        if RATE_LIMIT_DELAY > 0:
                            time.sleep(RATE_LIMIT_DELAY)
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}")
                        logger.debug(f"Response (first 500 chars): {result.stdout[:500]}")
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            return None
                else:
                    # Check if it's a rate limit or timeout error
                    stderr_lower = result.stderr.lower()
                    if '429' in stderr_lower or 'rate limit' in stderr_lower:
                        wait_time = RETRY_DELAY * (3 ** attempt)  # More aggressive backoff for rate limits
                        logger.warning(f"Rate limited by API! Waiting {wait_time}s...")
                        time.sleep(wait_time)
                    elif 'timeout' in stderr_lower or 'timed out' in stderr_lower:
                        logger.warning(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"Failed after {MAX_RETRIES} timeout attempts")
                            return None
                    else:
                        logger.error(f"PowerShell error: {result.stderr}")
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            return None
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Process timeout on attempt {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {MAX_RETRIES} timeout attempts")
                    return None
                    
            except Exception as e:
                logger.warning(f"Request error on attempt {attempt + 1}/{MAX_RETRIES}: {e}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {MAX_RETRIES} attempts")
                    return None
        
        return None
    
    def sync_cards_for_set(self, set_id):
        """Sync cards for a specific set with improved pagination"""
        logger.info(f"Syncing cards for set: {set_id}")
        session = self.Session()
        
        try:
            page = 1
            total_cards = 0
            processed = 0
            
            while True:
                params = {
                    'page': page,
                    'pageSize': self.batch_size,
                    'q': f'set.id:{set_id}'
                }
                
                logger.info(f"Fetching page {page} (batch size: {self.batch_size})...")
                data = self.make_request_powershell('cards', params, timeout=45)
                
                if not data or 'data' not in data:
                    logger.error(f"Failed to fetch page {page} for set {set_id}")
                    break
                
                cards_data = data['data']
                
                if page == 1:
                    total_cards = data.get('totalCount', 0)
                    logger.info(f"Total cards in set {set_id}: {total_cards}")
                
                if not cards_data:
                    logger.info(f"No more cards to fetch for set {set_id}")
                    break
                
                # Process cards
                for card_data in cards_data:
                    try:
                        self._process_card(session, card_data)
                        processed += 1
                        
                        if processed % 25 == 0:
                            logger.info(f"Processed {processed}/{total_cards} cards from set {set_id}")
                            session.commit()
                        
                    except Exception as e:
                        logger.error(f"Error processing card {card_data.get('id')}: {e}")
                        continue
                
                session.commit()
                
                # Check if we're done
                if len(cards_data) < self.batch_size:
                    logger.info(f"Reached end of set {set_id} (page {page})")
                    break
                
                page += 1
                
                # Add a small delay between pages
                time.sleep(1)
            
            logger.info(f"Successfully synced {processed} cards from set {set_id}")
            return processed
            
        except Exception as e:
            logger.error(f"Error syncing cards for set {set_id}: {e}")
            session.rollback()
            return 0
        finally:
            session.close()
    
    def _process_card(self, session, card_data):
        """Process and save a single card (simplified version)"""
        card_id = card_data['id']
        
        # Check if card exists
        card = session.query(Card).filter_by(id=card_id).first()
        
        if card:
            logger.debug(f"Updating card: {card_data['name']}")
        else:
            logger.debug(f"Adding new card: {card_data['name']}")
            card = Card(id=card_id)
        
        # Basic fields
        card.name = card_data.get('name')
        card.supertype = card_data.get('supertype')
        card.hp = card_data.get('hp')
        card.level = card_data.get('level')
        card.set_id = card_data['set']['id']
        card.number = card_data.get('number')
        
        # Evolution
        card.evolves_from = card_data.get('evolvesFrom')
        if card_data.get('evolvesTo'):
            card.evolves_to = json.dumps(card_data['evolvesTo'])
        
        # Text
        if card_data.get('rules'):
            card.rules = json.dumps(card_data['rules'])
        card.flavor_text = card_data.get('flavorText')
        
        # Details
        card.artist = card_data.get('artist')
        card.rarity = card_data.get('rarity')
        card.regulation_mark = card_data.get('regulationMark')
        
        # Costs
        if card_data.get('retreatCost'):
            card.retreat_cost = json.dumps(card_data['retreatCost'])
        card.converted_retreat_cost = card_data.get('convertedRetreatCost')
        
        # Pokedex
        if card_data.get('nationalPokedexNumbers'):
            card.national_pokedex_numbers = json.dumps(card_data['nationalPokedexNumbers'])
        
        # Legalities
        legalities = card_data.get('legalities', {})
        card.standard_legal = legalities.get('standard') == 'Legal'
        card.expanded_legal = legalities.get('expanded') == 'Legal'
        card.unlimited_legal = legalities.get('unlimited') == 'Legal'
        card.standard_banned = legalities.get('standard') == 'Banned'
        card.expanded_banned = legalities.get('expanded') == 'Banned'
        
        # Images
        images = card_data.get('images', {})
        card.image_small = images.get('small')
        card.image_large = images.get('large')
        
        card.synced_at = datetime.now(timezone.utc)
        
        session.add(card)
        session.flush()
        
        # Process types
        if card_data.get('types'):
            card.types.clear()
            for type_name in card_data['types']:
                type_obj = session.query(Type).filter_by(name=type_name).first()
                if type_obj:
                    card.types.append(type_obj)
        
        # Process subtypes
        if card_data.get('subtypes'):
            card.subtypes.clear()
            for subtype_name in card_data['subtypes']:
                subtype_obj = session.query(Subtype).filter_by(name=subtype_name).first()
                if subtype_obj:
                    card.subtypes.append(subtype_obj)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Improved Pokemon TCG Database Sync')
    parser.add_argument('--set', type=str, help='Sync specific set by ID')
    
    args = parser.parse_args()
    
    syncer = ImprovedPokemonTCGSync()
    
    if args.set:
        syncer.init_database()
        syncer.sync_cards_for_set(args.set)
    else:
        parser.print_help()