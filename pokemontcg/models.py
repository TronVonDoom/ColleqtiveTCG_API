"""
SQLAlchemy ORM Models for Pokemon TCG Database
"""
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Many-to-many relationship tables
card_types_table = Table(
    'card_types',
    Base.metadata,
    Column('card_id', String, ForeignKey('cards.id', ondelete='CASCADE'), primary_key=True),
    Column('type_name', String, ForeignKey('types.name', ondelete='CASCADE'), primary_key=True)
)

card_subtypes_table = Table(
    'card_subtypes',
    Base.metadata,
    Column('card_id', String, ForeignKey('cards.id', ondelete='CASCADE'), primary_key=True),
    Column('subtype_name', String, ForeignKey('subtypes.name', ondelete='CASCADE'), primary_key=True)
)


class Set(Base):
    __tablename__ = 'sets'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    series = Column(String)
    printed_total = Column(Integer)
    total = Column(Integer)
    ptcgo_code = Column(String)
    release_date = Column(String)
    updated_at = Column(String)
    
    # Legalities
    standard_legal = Column(Boolean, default=False)
    expanded_legal = Column(Boolean, default=False)
    unlimited_legal = Column(Boolean, default=False)
    
    # Images
    symbol_url = Column(String)
    logo_url = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cards = relationship('Card', back_populates='set', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Set(id='{self.id}', name='{self.name}')>"


class Card(Base):
    __tablename__ = 'cards'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    supertype = Column(String, index=True)
    hp = Column(String)
    level = Column(String)
    
    # Set relationship
    set_id = Column(String, ForeignKey('sets.id', ondelete='CASCADE'), nullable=False)
    number = Column(String)
    
    # Evolution
    evolves_from = Column(String)
    evolves_to = Column(Text)  # JSON array as text
    
    # Rules and text
    rules = Column(Text)  # JSON array as text
    flavor_text = Column(Text)
    
    # Card details
    artist = Column(String, index=True)
    rarity = Column(String, index=True)
    regulation_mark = Column(String)
    
    # Costs
    retreat_cost = Column(Text)  # JSON array as text
    converted_retreat_cost = Column(Integer)
    
    # Pokedex
    national_pokedex_numbers = Column(Text)  # JSON array as text
    
    # Legalities
    standard_legal = Column(Boolean, default=False)
    expanded_legal = Column(Boolean, default=False)
    unlimited_legal = Column(Boolean, default=False)
    standard_banned = Column(Boolean, default=False)
    expanded_banned = Column(Boolean, default=False)
    
    # Images
    image_small = Column(String)
    image_large = Column(String)
    
    # Pricing (TCGPlayer USD)
    tcgplayer_url = Column(String)
    tcgplayer_updated_at = Column(String)
    market_price = Column(Float)
    low_price = Column(Float)
    mid_price = Column(Float)
    high_price = Column(Float)
    
    # Pricing (Cardmarket EUR)
    cardmarket_url = Column(String)
    cardmarket_updated_at = Column(String)
    cardmarket_avg_price = Column(Float)
    cardmarket_low_price = Column(Float)
    cardmarket_trend_price = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    set = relationship('Set', back_populates='cards')
    types = relationship('Type', secondary=card_types_table, back_populates='cards')
    subtypes = relationship('Subtype', secondary=card_subtypes_table, back_populates='cards')
    attacks = relationship('Attack', back_populates='card', cascade='all, delete-orphan')
    abilities = relationship('Ability', back_populates='card', cascade='all, delete-orphan')
    weaknesses = relationship('Weakness', back_populates='card', cascade='all, delete-orphan')
    resistances = relationship('Resistance', back_populates='card', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Card(id='{self.id}', name='{self.name}')>"


class Attack(Base):
    __tablename__ = 'attacks'
    
    id = Column(Integer, primary_key=True)
    card_id = Column(String, ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String, nullable=False)
    cost = Column(Text)  # JSON array as text
    converted_energy_cost = Column(Integer)
    damage = Column(String)
    text = Column(Text)
    
    card = relationship('Card', back_populates='attacks')
    
    def __repr__(self):
        return f"<Attack(name='{self.name}', damage='{self.damage}')>"


class Ability(Base):
    __tablename__ = 'abilities'
    
    id = Column(Integer, primary_key=True)
    card_id = Column(String, ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String, nullable=False)
    text = Column(Text)
    ability_type = Column(String)  # "Ability", "Poke-Power", etc.
    
    card = relationship('Card', back_populates='abilities')
    
    def __repr__(self):
        return f"<Ability(name='{self.name}', type='{self.ability_type}')>"


class Weakness(Base):
    __tablename__ = 'weaknesses'
    
    id = Column(Integer, primary_key=True)
    card_id = Column(String, ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    
    card = relationship('Card', back_populates='weaknesses')


class Resistance(Base):
    __tablename__ = 'resistances'
    
    id = Column(Integer, primary_key=True)
    card_id = Column(String, ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    
    card = relationship('Card', back_populates='resistances')


# Reference tables
class Type(Base):
    __tablename__ = 'types'
    
    name = Column(String, primary_key=True)
    
    cards = relationship('Card', secondary=card_types_table, back_populates='types')
    
    def __repr__(self):
        return f"<Type(name='{self.name}')>"


class Subtype(Base):
    __tablename__ = 'subtypes'
    
    name = Column(String, primary_key=True)
    
    cards = relationship('Card', secondary=card_subtypes_table, back_populates='subtypes')
    
    def __repr__(self):
        return f"<Subtype(name='{self.name}')>"


class Supertype(Base):
    __tablename__ = 'supertypes'
    
    name = Column(String, primary_key=True)
    
    def __repr__(self):
        return f"<Supertype(name='{self.name}')>"


class Rarity(Base):
    __tablename__ = 'rarities'
    
    name = Column(String, primary_key=True)
    
    def __repr__(self):
        return f"<Rarity(name='{self.name}')>"


class SyncStatus(Base):
    """Track sync progress and status"""
    __tablename__ = 'sync_status'
    
    id = Column(Integer, primary_key=True)
    sync_type = Column(String, nullable=False)  # 'full', 'update', 'prices'
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String, nullable=False)  # 'running', 'completed', 'failed'
    
    total_items = Column(Integer)
    processed_items = Column(Integer)
    failed_items = Column(Integer)
    
    last_processed_id = Column(String)  # For resuming
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<SyncStatus(type='{self.sync_type}', status='{self.status}')>"
