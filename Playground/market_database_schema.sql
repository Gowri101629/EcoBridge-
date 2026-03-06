-- AI Based Soil Health & Sustainable Farming Advisor
-- Market intelligence database schema (PostgreSQL)

-- Optional: create a dedicated schema
CREATE SCHEMA IF NOT EXISTS farming_market;
SET search_path TO farming_market;

-- Master list of products/farm goods
CREATE TABLE IF NOT EXISTS goods (
    good_id BIGSERIAL PRIMARY KEY,
    good_name VARCHAR(120) NOT NULL UNIQUE,
    category VARCHAR(60) NOT NULL,            -- e.g. cereal, vegetable, fruit, pulse
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',   -- kg, quintal, ton, piece
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Geographic hierarchy for market locations
CREATE TABLE IF NOT EXISTS locations (
    location_id BIGSERIAL PRIMARY KEY,
    country VARCHAR(80) NOT NULL DEFAULT 'India',
    state_name VARCHAR(80) NOT NULL,
    district_name VARCHAR(80),
    city_name VARCHAR(80) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_location UNIQUE (state_name, city_name)
);

-- Market details
CREATE TABLE IF NOT EXISTS markets (
    market_id BIGSERIAL PRIMARY KEY,
    market_name VARCHAR(150) NOT NULL,
    market_type VARCHAR(40) NOT NULL,         -- APMC, wholesale, retail, farmer_market
    location_id BIGINT NOT NULL REFERENCES locations(location_id) ON DELETE RESTRICT,
    address_line VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_market_name_location UNIQUE (market_name, location_id)
);

-- What goods are sellable in each market
CREATE TABLE IF NOT EXISTS market_goods (
    market_good_id BIGSERIAL PRIMARY KEY,
    market_id BIGINT NOT NULL REFERENCES markets(market_id) ON DELETE CASCADE,
    good_id BIGINT NOT NULL REFERENCES goods(good_id) ON DELETE RESTRICT,
    quality_grade VARCHAR(20) DEFAULT 'Standard', -- Standard, A, B, Organic
    is_sellable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_market_good UNIQUE (market_id, good_id, quality_grade)
);

-- Daily price records for each good in each market
CREATE TABLE IF NOT EXISTS market_prices (
    price_id BIGSERIAL PRIMARY KEY,
    market_id BIGINT NOT NULL REFERENCES markets(market_id) ON DELETE CASCADE,
    good_id BIGINT NOT NULL REFERENCES goods(good_id) ON DELETE RESTRICT,
    price_date DATE NOT NULL,
    min_price DECIMAL(12,2) NOT NULL CHECK (min_price >= 0),
    max_price DECIMAL(12,2) NOT NULL CHECK (max_price >= min_price),
    modal_price DECIMAL(12,2) NOT NULL CHECK (modal_price BETWEEN min_price AND max_price),
    currency_code CHAR(3) NOT NULL DEFAULT 'INR',
    source VARCHAR(80) DEFAULT 'manual_entry',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_daily_price UNIQUE (market_id, good_id, price_date)
);

-- AI/rule-based trending results
CREATE TABLE IF NOT EXISTS trending_goods (
    trend_id BIGSERIAL PRIMARY KEY,
    good_id BIGINT NOT NULL REFERENCES goods(good_id) ON DELETE CASCADE,
    market_id BIGINT REFERENCES markets(market_id) ON DELETE CASCADE,
    trend_date DATE NOT NULL,
    trend_type VARCHAR(30) NOT NULL,          -- price_up, price_down, demand_up
    trend_score DECIMAL(6,2) NOT NULL CHECK (trend_score >= 0),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_trend UNIQUE (good_id, market_id, trend_date, trend_type)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_market_prices_lookup
    ON market_prices (good_id, market_id, price_date DESC);

CREATE INDEX IF NOT EXISTS idx_market_prices_date
    ON market_prices (price_date DESC);

CREATE INDEX IF NOT EXISTS idx_trending_goods_date_score
    ON trending_goods (trend_date DESC, trend_score DESC);

-- -------------------------
-- Sample reporting queries
-- -------------------------

-- 1) Latest modal prices by market and good
-- SELECT m.market_name, g.good_name, mp.price_date, mp.modal_price, mp.currency_code
-- FROM market_prices mp
-- JOIN markets m ON m.market_id = mp.market_id
-- JOIN goods g ON g.good_id = mp.good_id
-- WHERE mp.price_date = (SELECT MAX(price_date) FROM market_prices);

-- 2) Top trending goods for a date
-- SELECT tg.trend_date, g.good_name, m.market_name, tg.trend_type, tg.trend_score
-- FROM trending_goods tg
-- JOIN goods g ON g.good_id = tg.good_id
-- LEFT JOIN markets m ON m.market_id = tg.market_id
-- WHERE tg.trend_date = CURRENT_DATE
-- ORDER BY tg.trend_score DESC
-- LIMIT 10;

-- 3) 7-day average modal price for each good in each market
-- SELECT m.market_name, g.good_name, AVG(mp.modal_price) AS avg_modal_price_7d
-- FROM market_prices mp
-- JOIN markets m ON m.market_id = mp.market_id
-- JOIN goods g ON g.good_id = mp.good_id
-- WHERE mp.price_date >= CURRENT_DATE - INTERVAL '7 days'
-- GROUP BY m.market_name, g.good_name
-- ORDER BY avg_modal_price_7d DESC;
