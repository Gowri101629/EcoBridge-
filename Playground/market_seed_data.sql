SET search_path TO farming_market;

-- Locations
INSERT INTO locations (state_name, district_name, city_name, latitude, longitude)
VALUES
('Karnataka', 'Bengaluru Urban', 'Bengaluru', 12.9716, 77.5946),
('Maharashtra', 'Pune', 'Pune', 18.5204, 73.8567),
('Tamil Nadu', 'Coimbatore', 'Coimbatore', 11.0168, 76.9558)
ON CONFLICT (state_name, city_name) DO NOTHING;

-- Markets
INSERT INTO markets (market_name, market_type, location_id, address_line)
SELECT 'Yeshwanthpur APMC', 'APMC', l.location_id, 'Yeshwanthpur Market Yard'
FROM locations l WHERE l.state_name='Karnataka' AND l.city_name='Bengaluru'
ON CONFLICT (market_name, location_id) DO NOTHING;

INSERT INTO markets (market_name, market_type, location_id, address_line)
SELECT 'Pune Gultekdi Market', 'wholesale', l.location_id, 'Gultekdi'
FROM locations l WHERE l.state_name='Maharashtra' AND l.city_name='Pune'
ON CONFLICT (market_name, location_id) DO NOTHING;

-- Goods
INSERT INTO goods (good_name, category, unit)
VALUES
('Tomato', 'vegetable', 'kg'),
('Onion', 'vegetable', 'kg'),
('Rice', 'cereal', 'kg'),
('Banana', 'fruit', 'dozen')
ON CONFLICT (good_name) DO NOTHING;

-- Market goods mapping
INSERT INTO market_goods (market_id, good_id, quality_grade)
SELECT m.market_id, g.good_id, 'Standard'
FROM markets m
CROSS JOIN goods g
WHERE m.market_name IN ('Yeshwanthpur APMC', 'Pune Gultekdi Market')
  AND g.good_name IN ('Tomato', 'Onion', 'Rice', 'Banana')
ON CONFLICT (market_id, good_id, quality_grade) DO NOTHING;

-- Market prices
INSERT INTO market_prices (market_id, good_id, price_date, min_price, max_price, modal_price, currency_code, source)
SELECT m.market_id, g.good_id, CURRENT_DATE, 20, 32, 27, 'INR', 'sample_data'
FROM markets m JOIN goods g ON g.good_name='Tomato'
WHERE m.market_name='Yeshwanthpur APMC'
ON CONFLICT (market_id, good_id, price_date) DO NOTHING;

INSERT INTO market_prices (market_id, good_id, price_date, min_price, max_price, modal_price, currency_code, source)
SELECT m.market_id, g.good_id, CURRENT_DATE, 18, 29, 24, 'INR', 'sample_data'
FROM markets m JOIN goods g ON g.good_name='Onion'
WHERE m.market_name='Yeshwanthpur APMC'
ON CONFLICT (market_id, good_id, price_date) DO NOTHING;

INSERT INTO market_prices (market_id, good_id, price_date, min_price, max_price, modal_price, currency_code, source)
SELECT m.market_id, g.good_id, CURRENT_DATE, 42, 51, 47, 'INR', 'sample_data'
FROM markets m JOIN goods g ON g.good_name='Rice'
WHERE m.market_name='Pune Gultekdi Market'
ON CONFLICT (market_id, good_id, price_date) DO NOTHING;

-- Trending goods
INSERT INTO trending_goods (good_id, market_id, trend_date, trend_type, trend_score, notes)
SELECT g.good_id, m.market_id, CURRENT_DATE, 'price_up', 88.50, 'High demand due to lower supply'
FROM goods g
JOIN markets m ON m.market_name='Yeshwanthpur APMC'
WHERE g.good_name='Tomato'
ON CONFLICT (good_id, market_id, trend_date, trend_type) DO NOTHING;

INSERT INTO trending_goods (good_id, market_id, trend_date, trend_type, trend_score, notes)
SELECT g.good_id, m.market_id, CURRENT_DATE, 'demand_up', 79.30, 'Festival demand increase'
FROM goods g
JOIN markets m ON m.market_name='Pune Gultekdi Market'
WHERE g.good_name='Banana'
ON CONFLICT (good_id, market_id, trend_date, trend_type) DO NOTHING;
