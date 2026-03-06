# FarmBridge Backend + Database

## What this backend stores
- Farmer user profile: name, location, soil type, farming experience, email/phone
- Harvested crop types per farmer
- Market details for 5 cities
- Crop master data with 50 crops
- City-wise crop demand scores and organic profit percentage
- Farmer catalog price preferences

## Database
- Engine: SQLite (`/Users/gowrimahesh/Documents/Playground/backend/farmbridge.db`)
- Schema file: `schema.sql`

## Run server
```bash
cd /Users/gowrimahesh/Documents/Playground
python3 backend/server.py
```
Server URL: http://127.0.0.1:9000

This serves both:
- Frontend UI (`/`)
- Backend API (`/api/...`)

## Configure AI key (Gemini)
Do not hardcode keys in source. Set it as environment variable:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python3 backend/server.py
```

If key is not set or API call fails, backend automatically uses a local fallback advisor response.

## Configure OpenWeather key (Climate risk prediction)
Set OpenWeather API key to enable live climate-risk prediction:

```bash
export OPENWEATHER_API_KEY="YOUR_OPENWEATHER_API_KEY"
python3 backend/server.py
```

If this key is not set (or weather API fails), backend returns fallback climate guidance.

## Key APIs
- `GET /api/cities`
- `GET /api/crops`
- `GET /api/cities/{city}/demand?organic_first=true&crop_id={crop_id}`
- `GET /api/listings?city={city}&crop_name={crop_name}`
- `GET /api/farmers`
- `POST /api/farmers`
- `POST /api/catalog/preferences`
- `POST /api/ai/ask`
- `GET /api/climate-risk?city={city}&crop_name={crop_name}`
