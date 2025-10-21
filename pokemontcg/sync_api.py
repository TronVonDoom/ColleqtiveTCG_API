"""
Main Database Sync Script for Pokemon TCG API
Fetches all data from the API and stores in local database
"""
import subprocess
import time
import json
import logging
import argparse
from datetime import datetime, timezone
from urllib.parse import urlencode, quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from .config import (
    API_KEY, BASE_URL, DATABASE_URL, BATCH_SIZE, 
    RATE_LIMIT_DELAY, MAX_RETRIES, RETRY_DELAY,
    INCLUDE_PRICING, LOG_LEVEL, LOG_FILE, REQUEST_TIMEOUT
)
from .models import (
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


class PokemonTCGSync:
    """Sync Pokemon TCG API data to local database"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.headers = {'X-Api-Key': API_KEY}
        
    def init_database(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
        
    def make_request(self, endpoint, params=None):
        """Make API request using PowerShell (more reliable on Windows)"""
        url = f"{BASE_URL}/{endpoint}"
        
        # Build query string if params provided (properly URL encoded)
        if params:
            url += "?" + urlencode(params, quote_via=quote)
        
        for attempt in range(MAX_RETRIES):
            try:
                # Build PowerShell command with proper escaping
                ps_cmd = f'$response = Invoke-WebRequest -Uri "{url}"'
                
                # Add API key header
                ps_cmd += f" -Headers @{{'X-Api-Key'='{API_KEY}'}}"
                ps_cmd += f" -TimeoutSec {REQUEST_TIMEOUT}"
                ps_cmd += " -UseBasicParsing"
                ps_cmd += "; $response.Content"
                
                logger.debug(f"Requesting: {endpoint} (attempt {attempt + 1}/{MAX_RETRIES})")
                
                # Execute PowerShell command
                result = subprocess.run(
                    ['powershell', '-Command', ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=REQUEST_TIMEOUT + 10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        data = json.loads(result.stdout)
                        if RATE_LIMIT_DELAY > 0:
                            time.sleep(RATE_LIMIT_DELAY)
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}")
                        logger.debug(f"Response: {result.stdout[:500]}")
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            return None
                else:
                    # Check for rate limiting or server errors in stderr
                    stderr_lower = result.stderr.lower()
                    if '429' in stderr_lower or 'rate limit' in stderr_lower:
                        wait_time = RETRY_DELAY * (3 ** attempt)
                        logger.warning(f"Rate limited! Waiting {wait_time}s...")
                        time.sleep(wait_time)
                    elif '50' in result.stderr[:10]:  # 500-level errors
                        logger.warning(f"Server error detected")
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            return None
                    else:
                        if attempt < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (2 ** attempt)
                            logger.warning(f"Request failed, retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"Request failed: {result.stderr[:200]}")
                            return None
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Request timeout on attempt {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {MAX_RETRIES} timeout attempts")
                    return None
            
            except KeyboardInterrupt:
                logger.warning("Request interrupted by user")
                raise
                    
            except Exception as e:
                logger.warning(f"Request error on attempt {attempt + 1}/{MAX_RETRIES}: {type(e).__name__}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {MAX_RETRIES} attempts: {e}")
                    return None
        
        return None
    
    def sync_reference_data(self):
        """Sync types, subtypes, supertypes, and rarities"""
        logger.info("Syncing reference data...")
        session = self.Session()
        
        try:
            # Sync types
            logger.info("Fetching types...")
            try:
                data = self.make_request('types')
                if data and 'data' in data:
                    for type_name in data['data']:
                        type_obj = session.query(Type).filter_by(name=type_name).first()
                        if not type_obj:
                            session.add(Type(name=type_name))
                    logger.info(f"Synced {len(data['data'])} types")
                else:
                    logger.warning("Failed to fetch types, will continue anyway")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.warning(f"Error fetching types: {e}")
            
            # Sync subtypes
            logger.info("Fetching subtypes...")
            try:
                data = self.make_request('subtypes')
                if data and 'data' in data:
                    for subtype_name in data['data']:
                        subtype_obj = session.query(Subtype).filter_by(name=subtype_name).first()
                        if not subtype_obj:
                            session.add(Subtype(name=subtype_name))
                    logger.info(f"Synced {len(data['data'])} subtypes")
                else:
                    logger.warning("Failed to fetch subtypes, will continue anyway")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.warning(f"Error fetching subtypes: {e}")
            
            # Sync supertypes
            logger.info("Fetching supertypes...")
            try:
                data = self.make_request('supertypes')
                if data and 'data' in data:
                    for supertype_name in data['data']:
                        supertype_obj = session.query(Supertype).filter_by(name=supertype_name).first()
                        if not supertype_obj:
                            session.add(Supertype(name=supertype_name))
                    logger.info(f"Synced {len(data['data'])} supertypes")
                else:
                    logger.warning("Failed to fetch supertypes, will continue anyway")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.warning(f"Error fetching supertypes: {e}")
            
            # Sync rarities
            logger.info("Fetching rarities...")
            try:
                data = self.make_request('rarities')
                if data and 'data' in data:
                    for rarity_name in data['data']:
                        rarity_obj = session.query(Rarity).filter_by(name=rarity_name).first()
                        if not rarity_obj:
                            session.add(Rarity(name=rarity_name))
                    logger.info(f"Synced {len(data['data'])} rarities")
                else:
                    logger.warning("Failed to fetch rarities, will continue anyway")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.warning(f"Error fetching rarities: {e}")
            
            session.commit()
            logger.info("Reference data synced successfully")
            
        except KeyboardInterrupt:
            logger.warning("Reference data sync interrupted by user")
            session.rollback()
            raise
        except Exception as e:
            logger.error(f"Error syncing reference data: {e}")
            session.rollback()
        finally:
            session.close()
    
    def sync_sets(self):
        """Sync all sets from API"""
        logger.info("Syncing sets...")
        session = self.Session()
        
        try:
            data = self.make_request('sets')
            
            if not data or 'data' not in data:
                logger.error("Failed to fetch sets")
                return
            
            sets_data = data['data']
            logger.info(f"Found {len(sets_data)} sets")
            
            for set_data in sets_data:
                try:
                    # Check if set exists
                    set_obj = session.query(Set).filter_by(id=set_data['id']).first()
                    
                    if set_obj:
                        logger.debug(f"Updating set: {set_data['name']}")
                    else:
                        logger.info(f"Adding new set: {set_data['name']}")
                        set_obj = Set(id=set_data['id'])
                    
                    # Update fields
                    set_obj.name = set_data.get('name')
                    set_obj.series = set_data.get('series')
                    set_obj.printed_total = set_data.get('printedTotal')
                    set_obj.total = set_data.get('total')
                    set_obj.ptcgo_code = set_data.get('ptcgoCode')
                    set_obj.release_date = set_data.get('releaseDate')
                    set_obj.updated_at = set_data.get('updatedAt')
                    
                    # Legalities
                    legalities = set_data.get('legalities', {})
                    set_obj.standard_legal = 'standard' in legalities
                    set_obj.expanded_legal = 'expanded' in legalities
                    set_obj.unlimited_legal = 'unlimited' in legalities
                    
                    # Images
                    images = set_data.get('images', {})
                    set_obj.symbol_url = images.get('symbol')
                    set_obj.logo_url = images.get('logo')
                    
                    set_obj.synced_at = datetime.now(timezone.utc)
                    
                    session.add(set_obj)
                    
                except Exception as e:
                    logger.error(f"Error processing set {set_data.get('id')}: {e}")
                    continue
            
            session.commit()
            logger.info(f"Successfully synced {len(sets_data)} sets")
            
        except Exception as e:
            logger.error(f"Error syncing sets: {e}")
            session.rollback()
        finally:
            session.close()
    
    def sync_cards(self, set_id=None, resume_from=None):
        """Sync all cards from API"""
        session = self.Session()
        
        try:
            # Build query
            query = ''
            if set_id:
                query = f'set.id:{set_id}'
                logger.info(f"Syncing cards from set: {set_id}")
            else:
                logger.info("Syncing all cards...")
            
            page = 1
            total_cards = 0
            processed = 0
            
            while True:
                params = {
                    'page': page,
                    'pageSize': BATCH_SIZE
                }
                
                if query:
                    params['q'] = query
                
                logger.info(f"Fetching page {page}...")
                data = self.make_request('cards', params)
                
                if not data or 'data' not in data:
                    logger.error(f"Failed to fetch page {page}")
                    break
                
                cards_data = data['data']
                
                if page == 1:
                    total_cards = data.get('totalCount', 0)
                    logger.info(f"Total cards to sync: {total_cards}")
                
                if not cards_data:
                    logger.info("No more cards to fetch")
                    break
                
                # Process cards
                for card_data in cards_data:
                    try:
                        if resume_from and card_data['id'] <= resume_from:
                            continue
                        
                        self._process_card(session, card_data)
                        processed += 1
                        
                        if processed % 250 == 0:
                            logger.info(f"Processed {processed}/{total_cards} cards ({(processed/total_cards*100):.1f}%)")
                            session.commit()
                        
                    except Exception as e:
                        logger.error(f"Error processing card {card_data.get('id')}: {e}")
                        continue
                
                session.commit()
                
                # Check if we're done
                if len(cards_data) < BATCH_SIZE:
                    break
                
                page += 1
            
            logger.info(f"Successfully synced {processed} cards")
            
        except Exception as e:
            logger.error(f"Error syncing cards: {e}")
            session.rollback()
        finally:
            session.close()
    
    def _process_card(self, session, card_data):
        """Process and save a single card"""
        card_id = card_data['id']
        
        # Check if card exists
        card = session.query(Card).filter_by(id=card_id).first()
        
        if card:
            # Update existing
            logger.debug(f"Updating card: {card_data['name']}")
        else:
            # Create new
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
        
        # Pricing
        if INCLUDE_PRICING:
            self._process_pricing(card, card_data)
        
        card.synced_at = datetime.now(timezone.utc)
        
        session.add(card)
        session.flush()  # Get card ID for relationships
        
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
        
        # Process attacks
        if card_data.get('attacks'):
            # Clear existing
            for attack in card.attacks:
                session.delete(attack)
            
            for attack_data in card_data['attacks']:
                attack = Attack(
                    card_id=card_id,
                    name=attack_data.get('name'),
                    cost=json.dumps(attack_data.get('cost', [])),
                    converted_energy_cost=attack_data.get('convertedEnergyCost'),
                    damage=attack_data.get('damage'),
                    text=attack_data.get('text')
                )
                session.add(attack)
        
        # Process abilities
        if card_data.get('abilities'):
            # Clear existing
            for ability in card.abilities:
                session.delete(ability)
            
            for ability_data in card_data['abilities']:
                ability = Ability(
                    card_id=card_id,
                    name=ability_data.get('name'),
                    text=ability_data.get('text'),
                    ability_type=ability_data.get('type')
                )
                session.add(ability)
        
        # Process weaknesses
        if card_data.get('weaknesses'):
            # Clear existing
            for weakness in card.weaknesses:
                session.delete(weakness)
            
            for weakness_data in card_data['weaknesses']:
                weakness = Weakness(
                    card_id=card_id,
                    type=weakness_data.get('type'),
                    value=weakness_data.get('value')
                )
                session.add(weakness)
        
        # Process resistances
        if card_data.get('resistances'):
            # Clear existing
            for resistance in card.resistances:
                session.delete(resistance)
            
            for resistance_data in card_data['resistances']:
                resistance = Resistance(
                    card_id=card_id,
                    type=resistance_data.get('type'),
                    value=resistance_data.get('value')
                )
                session.add(resistance)
    
    def _process_pricing(self, card, card_data):
        """Process pricing data"""
        # TCGPlayer
        if 'tcgplayer' in card_data:
            tcg = card_data['tcgplayer']
            card.tcgplayer_url = tcg.get('url')
            card.tcgplayer_updated_at = tcg.get('updatedAt')
            
            # Get market price from first available variant
            prices = tcg.get('prices', {})
            for variant, price_data in prices.items():
                if 'market' in price_data:
                    card.market_price = price_data['market']
                    card.low_price = price_data.get('low')
                    card.mid_price = price_data.get('mid')
                    card.high_price = price_data.get('high')
                    break
        
        # Cardmarket
        if 'cardmarket' in card_data:
            cm = card_data['cardmarket']
            card.cardmarket_url = cm.get('url')
            card.cardmarket_updated_at = cm.get('updatedAt')
            
            prices = cm.get('prices', {})
            card.cardmarket_avg_price = prices.get('averageSellPrice')
            card.cardmarket_low_price = prices.get('lowPrice')
            card.cardmarket_trend_price = prices.get('trendPrice')
    
    def full_sync(self):
        """Perform full database sync"""
        logger.info("=" * 60)
        logger.info("Starting FULL SYNC")
        logger.info("=" * 60)
        
        start_time = datetime.now(timezone.utc)
        
        # Initialize database FIRST
        self.init_database()
        
        # Create sync status
        session = self.Session()
        sync_status = SyncStatus(
            sync_type='full',
            started_at=start_time,
            status='running'
        )
        session.add(sync_status)
        session.commit()
        
        try:
            
            # Sync reference data
            try:
                self.sync_reference_data()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Reference data sync failed: {e}, continuing anyway...")
            
            # Sync sets
            try:
                self.sync_sets()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Sets sync failed: {e}, continuing anyway...")
            
            # Sync all cards
            try:
                self.sync_cards()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Cards sync failed: {e}")
            
            # Mark as completed
            sync_status.status = 'completed'
            sync_status.completed_at = datetime.now(timezone.utc)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info("=" * 60)
            logger.info(f"FULL SYNC COMPLETED in {duration:.2f} seconds")
            logger.info("=" * 60)
            
        except KeyboardInterrupt:
            logger.warning("\n" + "=" * 60)
            logger.warning("SYNC INTERRUPTED BY USER")
            logger.warning("=" * 60)
            sync_status.status = 'interrupted'
            sync_status.error_message = 'User interrupted the sync'
        except Exception as e:
            logger.error(f"Full sync failed: {e}")
            sync_status.status = 'failed'
            sync_status.error_message = str(e)
        finally:
            session.commit()
            session.close()


def main():
    parser = argparse.ArgumentParser(description='Pokemon TCG Database Sync')
    parser.add_argument('--full', action='store_true', help='Perform full sync')
    parser.add_argument('--update', action='store_true', help='Update with new data')
    parser.add_argument('--reference', action='store_true', help='Sync reference data only')
    parser.add_argument('--sets', action='store_true', help='Sync sets only')
    parser.add_argument('--set', type=str, help='Sync specific set by ID')
    parser.add_argument('--resume', type=str, help='Resume from card ID')
    parser.add_argument('--reset', action='store_true', help='Drop and recreate database')
    
    args = parser.parse_args()
    
    syncer = PokemonTCGSync()
    
    if args.reset:
        logger.warning("Dropping all tables...")
        Base.metadata.drop_all(syncer.engine)
        logger.info("Database reset complete")
    
    if args.full:
        syncer.full_sync()
    elif args.reference:
        syncer.init_database()
        syncer.sync_reference_data()
    elif args.sets:
        syncer.init_database()
        syncer.sync_sets()
    elif args.set:
        syncer.init_database()
        syncer.sync_cards(set_id=args.set)
    elif args.update:
        syncer.init_database()
        syncer.sync_sets()
        syncer.sync_cards()
    elif args.resume:
        syncer.init_database()
        syncer.sync_cards(resume_from=args.resume)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
