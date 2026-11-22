-- PerkPilot SQLite Schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_name TEXT NOT NULL,
    issuer TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    merchant TEXT NOT NULL,
    category TEXT NOT NULL,
    benefit_type TEXT NOT NULL CHECK(benefit_type IN ('cashback_percent', 'instant_discount_percent', 'reward_percent')),
    rate_percent REAL NOT NULL CHECK(rate_percent >= 0),
    minimum_spend REAL NOT NULL DEFAULT 0 CHECK(minimum_spend >= 0),
    cap_amount REAL CHECK(cap_amount IS NULL OR cap_amount >= 0),
    active INTEGER NOT NULL DEFAULT 1,
    valid_from TEXT,
    valid_until TEXT,
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_offers_merchant ON offers(merchant);
CREATE INDEX IF NOT EXISTS idx_offers_category ON offers(category);
CREATE INDEX IF NOT EXISTS idx_offers_card_id ON offers(card_id);
