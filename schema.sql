-- PostgreSQL Schema for Pokemon TCG Database
-- This file can be used to manually create the schema on Railway

-- Sets table
CREATE TABLE sets (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    series VARCHAR,
    printed_total INTEGER,
    total INTEGER,
    ptcgo_code VARCHAR,
    release_date VARCHAR,
    updated_at VARCHAR,
    standard_legal BOOLEAN DEFAULT FALSE,
    expanded_legal BOOLEAN DEFAULT FALSE,
    unlimited_legal BOOLEAN DEFAULT FALSE,
    symbol_url VARCHAR,
    logo_url VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sets_name ON sets(name);
CREATE INDEX idx_sets_series ON sets(series);
CREATE INDEX idx_sets_release_date ON sets(release_date);

-- Cards table
CREATE TABLE cards (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    supertype VARCHAR,
    hp VARCHAR,
    level VARCHAR,
    set_id VARCHAR NOT NULL REFERENCES sets(id) ON DELETE CASCADE,
    number VARCHAR,
    evolves_from VARCHAR,
    evolves_to TEXT,
    rules TEXT,
    flavor_text TEXT,
    artist VARCHAR,
    rarity VARCHAR,
    regulation_mark VARCHAR,
    retreat_cost TEXT,
    converted_retreat_cost INTEGER,
    national_pokedex_numbers TEXT,
    standard_legal BOOLEAN DEFAULT FALSE,
    expanded_legal BOOLEAN DEFAULT FALSE,
    unlimited_legal BOOLEAN DEFAULT FALSE,
    standard_banned BOOLEAN DEFAULT FALSE,
    expanded_banned BOOLEAN DEFAULT FALSE,
    image_small VARCHAR,
    image_large VARCHAR,
    tcgplayer_url VARCHAR,
    tcgplayer_updated_at VARCHAR,
    market_price FLOAT,
    low_price FLOAT,
    mid_price FLOAT,
    high_price FLOAT,
    cardmarket_url VARCHAR,
    cardmarket_updated_at VARCHAR,
    cardmarket_avg_price FLOAT,
    cardmarket_low_price FLOAT,
    cardmarket_trend_price FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cards_name ON cards(name);
CREATE INDEX idx_cards_supertype ON cards(supertype);
CREATE INDEX idx_cards_artist ON cards(artist);
CREATE INDEX idx_cards_rarity ON cards(rarity);
CREATE INDEX idx_cards_set_id ON cards(set_id);
CREATE INDEX idx_cards_market_price ON cards(market_price);

-- Types reference table
CREATE TABLE types (
    name VARCHAR PRIMARY KEY
);

-- Subtypes reference table
CREATE TABLE subtypes (
    name VARCHAR PRIMARY KEY
);

-- Supertypes reference table
CREATE TABLE supertypes (
    name VARCHAR PRIMARY KEY
);

-- Rarities reference table
CREATE TABLE rarities (
    name VARCHAR PRIMARY KEY
);

-- Card types junction table
CREATE TABLE card_types (
    card_id VARCHAR REFERENCES cards(id) ON DELETE CASCADE,
    type_name VARCHAR REFERENCES types(name) ON DELETE CASCADE,
    PRIMARY KEY (card_id, type_name)
);

CREATE INDEX idx_card_types_card_id ON card_types(card_id);
CREATE INDEX idx_card_types_type_name ON card_types(type_name);

-- Card subtypes junction table
CREATE TABLE card_subtypes (
    card_id VARCHAR REFERENCES cards(id) ON DELETE CASCADE,
    subtype_name VARCHAR REFERENCES subtypes(name) ON DELETE CASCADE,
    PRIMARY KEY (card_id, subtype_name)
);

CREATE INDEX idx_card_subtypes_card_id ON card_subtypes(card_id);
CREATE INDEX idx_card_subtypes_subtype_name ON card_subtypes(subtype_name);

-- Attacks table
CREATE TABLE attacks (
    id SERIAL PRIMARY KEY,
    card_id VARCHAR NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    cost TEXT,
    converted_energy_cost INTEGER,
    damage VARCHAR,
    text TEXT
);

CREATE INDEX idx_attacks_card_id ON attacks(card_id);
CREATE INDEX idx_attacks_name ON attacks(name);

-- Abilities table
CREATE TABLE abilities (
    id SERIAL PRIMARY KEY,
    card_id VARCHAR NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    text TEXT,
    ability_type VARCHAR
);

CREATE INDEX idx_abilities_card_id ON abilities(card_id);
CREATE INDEX idx_abilities_name ON abilities(name);

-- Weaknesses table
CREATE TABLE weaknesses (
    id SERIAL PRIMARY KEY,
    card_id VARCHAR NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL,
    value VARCHAR NOT NULL
);

CREATE INDEX idx_weaknesses_card_id ON weaknesses(card_id);

-- Resistances table
CREATE TABLE resistances (
    id SERIAL PRIMARY KEY,
    card_id VARCHAR NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL,
    value VARCHAR NOT NULL
);

CREATE INDEX idx_resistances_card_id ON resistances(card_id);

-- Sync status table
CREATE TABLE sync_status (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL,
    total_items INTEGER,
    processed_items INTEGER,
    failed_items INTEGER,
    last_processed_id VARCHAR,
    error_message TEXT
);

CREATE INDEX idx_sync_status_type ON sync_status(sync_type);
CREATE INDEX idx_sync_status_started_at ON sync_status(started_at);

-- Views for common queries

-- View: Latest cards with pricing
CREATE VIEW latest_cards_with_prices AS
SELECT 
    c.id,
    c.name,
    c.set_id,
    s.name as set_name,
    c.rarity,
    c.market_price,
    c.image_small,
    c.synced_at
FROM cards c
JOIN sets s ON c.set_id = s.id
WHERE c.market_price IS NOT NULL
ORDER BY c.synced_at DESC;

-- View: Standard legal cards
CREATE VIEW standard_legal_cards AS
SELECT 
    c.id,
    c.name,
    c.supertype,
    c.hp,
    c.set_id,
    s.name as set_name,
    c.rarity
FROM cards c
JOIN sets s ON c.set_id = s.id
WHERE c.standard_legal = TRUE;

-- View: Card statistics by set
CREATE VIEW set_statistics AS
SELECT 
    s.id,
    s.name,
    s.series,
    s.total as total_cards,
    COUNT(c.id) as cards_synced,
    COUNT(CASE WHEN c.market_price IS NOT NULL THEN 1 END) as cards_with_prices,
    AVG(c.market_price) as avg_price,
    MAX(c.market_price) as max_price
FROM sets s
LEFT JOIN cards c ON s.id = c.set_id
GROUP BY s.id, s.name, s.series, s.total;
