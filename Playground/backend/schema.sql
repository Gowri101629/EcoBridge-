PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS farmers (
  farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  city TEXT NOT NULL,
  state_name TEXT,
  soil_type TEXT NOT NULL,
  farming_experience_years INTEGER NOT NULL CHECK (farming_experience_years >= 0),
  email TEXT,
  phone TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS crops (
  crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
  crop_name TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL,
  preferred_unit TEXT NOT NULL DEFAULT 'kg',
  is_organic_priority INTEGER NOT NULL DEFAULT 1 CHECK (is_organic_priority IN (0,1))
);

CREATE TABLE IF NOT EXISTS farmer_harvests (
  harvest_id INTEGER PRIMARY KEY AUTOINCREMENT,
  farmer_id INTEGER NOT NULL,
  crop_id INTEGER NOT NULL,
  season_label TEXT,
  harvested_quantity REAL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (farmer_id, crop_id),
  FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
  FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS markets (
  market_id INTEGER PRIMARY KEY AUTOINCREMENT,
  market_name TEXT NOT NULL,
  city TEXT NOT NULL UNIQUE,
  state_name TEXT NOT NULL,
  latitude REAL,
  longitude REAL
);

CREATE TABLE IF NOT EXISTS market_demand (
  demand_id INTEGER PRIMARY KEY AUTOINCREMENT,
  market_id INTEGER NOT NULL,
  crop_id INTEGER NOT NULL,
  demand_score REAL NOT NULL CHECK (demand_score BETWEEN 0 AND 100),
  average_price_inr REAL NOT NULL CHECK (average_price_inr >= 0),
  organic_profit_pct REAL NOT NULL CHECK (organic_profit_pct >= 0),
  last_updated TEXT NOT NULL,
  UNIQUE (market_id, crop_id),
  FOREIGN KEY (market_id) REFERENCES markets(market_id) ON DELETE CASCADE,
  FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS farmer_catalog_preferences (
  preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
  farmer_id INTEGER NOT NULL,
  crop_id INTEGER NOT NULL,
  preferred_price_inr REAL NOT NULL CHECK (preferred_price_inr >= 0),
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (farmer_id, crop_id),
  FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
  FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_market_demand_city_score
  ON market_demand (market_id, demand_score DESC);

CREATE INDEX IF NOT EXISTS idx_harvests_farmer
  ON farmer_harvests (farmer_id);
