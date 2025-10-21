"""
Sync Pokemon TCG data from GitHub repository instead of API
This avoids the API rate limits and slowness
"""
import os
import json
import logging
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL, LOG_LEVEL, LOG_FILE
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

# GitHub repository URL
GITHUB_REPO = "https://github.com/PokemonTCG/pokemon-tcg-data.git"
DATA_DIR = "pokemon-tcg-data"


class GitHubTCGSync:
    """Sync Pokemon TCG data from GitHub repository"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or DATABASE_URL
        # For SQLite, use check_same_thread=False to allow multi-threaded access
        connect_args = {}
        if 'sqlite' in self.database_url:
            connect_args = {'check_same_thread': False}
        self.engine = create_engine(self.database_url, echo=False, connect_args=connect_args)
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.data_dir = Path(DATA_DIR)
        
    def init_database(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
    
    def clone_or_update_repo(self):
        """Clone or update the GitHub repository"""
        if self.data_dir.exists():
            logger.info("Updating existing repository...")
            try:
                result = subprocess.run(
                    ['git', 'pull'],
                    cwd=self.data_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    logger.info("Repository updated successfully")
                    return True
                else:
                    logger.error(f"Git pull failed: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"Error updating repository: {e}")
                return False
        else:
            logger.info("Cloning repository...")
            try:
                result = subprocess.run(
                    ['git', 'clone', GITHUB_REPO, str(self.data_dir)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("Repository cloned successfully")
                    return True
                else:
                    logger.error(f"Git clone failed: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"Error cloning repository: {e}")
                return False
    
    def sync_reference_data(self):
        """Sync types, subtypes, supertypes, and rarities from card data"""
        logger.info("Syncing reference data from cards...")
        session = self.Session()
        
        try:
            # Collect unique values from all cards
            types_set = set()
            subtypes_set = set()
            supertypes_set = set()
            rarities_set = set()
            
            cards_dir = self.data_dir / "cards" / "en"
            if not cards_dir.exists():
                logger.error(f"Cards directory not found: {cards_dir}")
                return
            
            # Scan through all JSON files
            set_count = 0
            for set_file in cards_dir.glob("*.json"):
                set_count += 1
                try:
                    with open(set_file, 'r', encoding='utf-8') as f:
                        cards_data = json.load(f)
                        
                        for card in cards_data:
                            # Collect types
                            if 'types' in card:
                                types_set.update(card['types'])
                            
                            # Collect subtypes
                            if 'subtypes' in card:
                                subtypes_set.update(card['subtypes'])
                            
                            # Collect supertype
                            if 'supertype' in card:
                                supertypes_set.add(card['supertype'])
                            
                            # Collect rarity
                            if 'rarity' in card:
                                rarities_set.add(card['rarity'])
                
                except Exception as e:
                    logger.warning(f"Error reading set file {set_file}: {e}")
                    continue
            
            logger.info(f"Scanned {set_count} sets")
            
            # Insert types
            for type_name in types_set:
                type_obj = session.query(Type).filter_by(name=type_name).first()
                if not type_obj:
                    session.add(Type(name=type_name))
            logger.info(f"Synced {len(types_set)} types")
            
            # Insert subtypes
            for subtype_name in subtypes_set:
                subtype_obj = session.query(Subtype).filter_by(name=subtype_name).first()
                if not subtype_obj:
                    session.add(Subtype(name=subtype_name))
            logger.info(f"Synced {len(subtypes_set)} subtypes")
            
            # Insert supertypes
            for supertype_name in supertypes_set:
                supertype_obj = session.query(Supertype).filter_by(name=supertype_name).first()
                if not supertype_obj:
                    session.add(Supertype(name=supertype_name))
            logger.info(f"Synced {len(supertypes_set)} supertypes")
            
            # Insert rarities
            for rarity_name in rarities_set:
                rarity_obj = session.query(Rarity).filter_by(name=rarity_name).first()
                if not rarity_obj:
                    session.add(Rarity(name=rarity_name))
            logger.info(f"Synced {len(rarities_set)} rarities")
            
            session.commit()
            logger.info("Reference data synced successfully")
            
        except Exception as e:
            logger.error(f"Error syncing reference data: {e}")
            session.rollback()
        finally:
            session.close()
    
    def sync_sets(self):
        """Sync all sets from JSON files"""
        logger.info("Syncing sets from GitHub data...")
        session = self.Session()
        
        try:
            sets_dir = self.data_dir / "sets"
            if not sets_dir.exists():
                logger.error(f"Sets directory not found: {sets_dir}")
                return
            
            sets_file = sets_dir / "en.json"
            if not sets_file.exists():
                logger.error(f"Sets file not found: {sets_file}")
                return
            
            with open(sets_file, 'r', encoding='utf-8') as f:
                sets_data = json.load(f)
            
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
    
    def sync_cards(self):
        """Sync all cards from JSON files"""
        logger.info("Syncing cards from GitHub data...")
        session = self.Session()
        
        try:
            cards_dir = self.data_dir / "cards" / "en"
            if not cards_dir.exists():
                logger.error(f"Cards directory not found: {cards_dir}")
                return
            
            total_cards = 0
            processed = 0
            
            # Process each JSON file in the directory
            for set_file in sorted(cards_dir.glob("*.json")):
                try:
                    with open(set_file, 'r', encoding='utf-8') as f:
                        cards_data = json.load(f)
                    
                    # Extract set_id from filename (e.g., "base1.json" -> "base1")
                    set_id = set_file.stem
                    
                    total_cards += len(cards_data)
                    logger.info(f"Processing {set_file.name}: {len(cards_data)} cards (set_id: {set_id})")
                    
                    for card_data in cards_data:
                        try:
                            self._process_card(session, card_data, set_id)
                            processed += 1
                            
                            if processed % 100 == 0:
                                logger.info(f"Processed {processed} cards...")
                                session.commit()
                        
                        except Exception as e:
                            logger.error(f"Error processing card {card_data.get('id')}: {e}")
                            continue
                    
                    session.commit()
                    logger.info(f"Completed {set_file.name}")
                
                except Exception as e:
                    logger.error(f"Error reading set file {set_file}: {e}")
                    continue
            
            logger.info(f"Successfully synced {processed}/{total_cards} cards")
            
        except Exception as e:
            logger.error(f"Error syncing cards: {e}")
            session.rollback()
        finally:
            session.close()
    
    def _process_card(self, session, card_data, set_id):
        """Process and save a single card"""
        card_id = card_data['id']
        
        # Check if card exists
        card = session.query(Card).filter_by(id=card_id).first()
        
        if not card:
            card = Card(id=card_id)
        
        # Basic fields
        card.name = card_data.get('name')
        card.supertype = card_data.get('supertype')
        card.hp = card_data.get('hp')
        card.level = card_data.get('level')
        card.set_id = set_id  # Use the set_id passed from the filename
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
        
        # Pricing (if available)
        if 'tcgplayer' in card_data:
            tcg = card_data['tcgplayer']
            card.tcgplayer_url = tcg.get('url')
            card.tcgplayer_updated_at = tcg.get('updatedAt')
            
            prices = tcg.get('prices', {})
            for variant, price_data in prices.items():
                if 'market' in price_data:
                    card.market_price = price_data['market']
                    card.low_price = price_data.get('low')
                    card.mid_price = price_data.get('mid')
                    card.high_price = price_data.get('high')
                    break
        
        if 'cardmarket' in card_data:
            cm = card_data['cardmarket']
            card.cardmarket_url = cm.get('url')
            card.cardmarket_updated_at = cm.get('updatedAt')
            
            prices = cm.get('prices', {})
            card.cardmarket_avg_price = prices.get('averageSellPrice')
            card.cardmarket_low_price = prices.get('lowPrice')
            card.cardmarket_trend_price = prices.get('trendPrice')
        
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
        
        # Process attacks
        if card_data.get('attacks'):
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
            for resistance in card.resistances:
                session.delete(resistance)
            
            for resistance_data in card_data['resistances']:
                resistance = Resistance(
                    card_id=card_id,
                    type=resistance_data.get('type'),
                    value=resistance_data.get('value')
                )
                session.add(resistance)
    
    def full_sync(self):
        """Perform full sync from GitHub repository"""
        logger.info("=" * 60)
        logger.info("Starting FULL SYNC from GitHub Repository")
        logger.info("=" * 60)
        
        start_time = datetime.now(timezone.utc)
        
        # Initialize database
        self.init_database()
        
        # Create sync status
        session = self.Session()
        sync_status = SyncStatus(
            sync_type='full_github',
            started_at=start_time,
            status='running'
        )
        session.add(sync_status)
        session.commit()
        
        try:
            # Clone or update repository
            if not self.clone_or_update_repo():
                raise Exception("Failed to clone/update repository")
            
            # Sync reference data
            self.sync_reference_data()
            
            # Sync sets
            self.sync_sets()
            
            # Sync cards
            self.sync_cards()
            
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
    parser = argparse.ArgumentParser(description='Pokemon TCG Database Sync from GitHub')
    parser.add_argument('--full', action='store_true', help='Perform full sync')
    parser.add_argument('--update', action='store_true', help='Update repository and sync')
    parser.add_argument('--sets', action='store_true', help='Sync sets only')
    parser.add_argument('--cards', action='store_true', help='Sync cards only')
    parser.add_argument('--reference', action='store_true', help='Sync reference data only')
    
    args = parser.parse_args()
    
    syncer = GitHubTCGSync()
    
    if args.full:
        syncer.full_sync()
    elif args.update:
        syncer.init_database()
        syncer.clone_or_update_repo()
        syncer.sync_reference_data()
        syncer.sync_sets()
        syncer.sync_cards()
    elif args.sets:
        syncer.init_database()
        if syncer.clone_or_update_repo():
            syncer.sync_sets()
    elif args.cards:
        syncer.init_database()
        if syncer.clone_or_update_repo():
            syncer.sync_cards()
    elif args.reference:
        syncer.init_database()
        if syncer.clone_or_update_repo():
            syncer.sync_reference_data()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
