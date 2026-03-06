#!/usr/bin/env python3
import datetime as dt
import hashlib
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
WEB_DIR = PROJECT_DIR / "web"
DB_PATH = BASE_DIR / "farmbridge.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
HOST = "127.0.0.1"
PORT = 9000

CROPS = [
    ("Tomato", "Vegetable", "kg", 1),
    ("Onion", "Vegetable", "kg", 1),
    ("Potato", "Vegetable", "kg", 1),
    ("Brinjal", "Vegetable", "kg", 1),
    ("Okra", "Vegetable", "kg", 1),
    ("Cabbage", "Vegetable", "kg", 1),
    ("Cauliflower", "Vegetable", "kg", 1),
    ("Carrot", "Vegetable", "kg", 1),
    ("Beetroot", "Vegetable", "kg", 1),
    ("Spinach", "Leafy", "bunch", 1),
    ("Coriander", "Leafy", "bunch", 1),
    ("Methi", "Leafy", "bunch", 1),
    ("Cucumber", "Vegetable", "kg", 1),
    ("Bottle Gourd", "Vegetable", "kg", 1),
    ("Bitter Gourd", "Vegetable", "kg", 1),
    ("Pumpkin", "Vegetable", "kg", 1),
    ("Green Chili", "Vegetable", "kg", 1),
    ("Capsicum", "Vegetable", "kg", 1),
    ("Banana", "Fruit", "dozen", 1),
    ("Mango", "Fruit", "kg", 1),
    ("Papaya", "Fruit", "kg", 1),
    ("Guava", "Fruit", "kg", 1),
    ("Pomegranate", "Fruit", "kg", 1),
    ("Watermelon", "Fruit", "kg", 1),
    ("Muskmelon", "Fruit", "kg", 1),
    ("Rice", "Cereal", "kg", 0),
    ("Wheat", "Cereal", "kg", 0),
    ("Maize", "Cereal", "kg", 0),
    ("Ragi", "Millet", "kg", 1),
    ("Bajra", "Millet", "kg", 1),
    ("Jowar", "Millet", "kg", 1),
    ("Foxtail Millet", "Millet", "kg", 1),
    ("Little Millet", "Millet", "kg", 1),
    ("Tur Dal", "Pulse", "kg", 1),
    ("Moong Dal", "Pulse", "kg", 1),
    ("Urad Dal", "Pulse", "kg", 1),
    ("Chana", "Pulse", "kg", 1),
    ("Groundnut", "Oilseed", "kg", 1),
    ("Sesame", "Oilseed", "kg", 1),
    ("Sunflower", "Oilseed", "kg", 0),
    ("Mustard", "Oilseed", "kg", 0),
    ("Soybean", "Oilseed", "kg", 0),
    ("Turmeric", "Spice", "kg", 1),
    ("Ginger", "Spice", "kg", 1),
    ("Coriander Seed", "Spice", "kg", 1),
    ("Cumin", "Spice", "kg", 1),
    ("Fenugreek Seed", "Spice", "kg", 1),
    ("Coconut", "Plantation", "piece", 0),
    ("Sugarcane", "Cash Crop", "ton", 0),
    ("Cotton", "Cash Crop", "kg", 0),
]

MARKETS = [
    ("Yeshwanthpur APMC", "Bengaluru", "Karnataka", 12.9789, 77.5722),
    ("Pune Gultekdi Market", "Pune", "Maharashtra", 18.4987, 73.8744),
    ("Uzhavar Sandhai", "Coimbatore", "Tamil Nadu", 11.0168, 76.9558),
    ("Bowenpally Market", "Hyderabad", "Telangana", 17.4615, 78.4747),
    ("Azadpur Mandi", "Delhi", "Delhi", 28.7141, 77.1727),
]

SAMPLE_FARMERS = [
    {
        "full_name": "Anand R",
        "city": "Bengaluru",
        "state_name": "Karnataka",
        "soil_type": "Loamy",
        "farming_experience_years": 7,
        "email": "anand@example.com",
        "phone": "+919900000001",
        "crops": ["Tomato", "Ragi", "Coriander"],
    },
    {
        "full_name": "Lakshmi M",
        "city": "Pune",
        "state_name": "Maharashtra",
        "soil_type": "Black Soil",
        "farming_experience_years": 12,
        "email": "lakshmi@example.com",
        "phone": "+919900000002",
        "crops": ["Turmeric", "Banana", "Moong Dal"],
    },
]


def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def stable_int(key, low, high):
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    number = int(digest[:8], 16)
    span = high - low + 1
    return low + (number % span)


def seed_data(conn):
    conn.executemany(
        """
        INSERT OR IGNORE INTO crops (crop_name, category, preferred_unit, is_organic_priority)
        VALUES (?, ?, ?, ?)
        """,
        CROPS,
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO markets (market_name, city, state_name, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
        """,
        MARKETS,
    )

    crop_rows = conn.execute("SELECT crop_id, crop_name, is_organic_priority FROM crops").fetchall()
    market_rows = conn.execute("SELECT market_id, city FROM markets").fetchall()

    now = dt.date.today().isoformat()
    for market in market_rows:
        for crop in crop_rows:
            score = stable_int(f"{market['city']}:{crop['crop_name']}:score", 48, 97)
            base_price = stable_int(f"{market['city']}:{crop['crop_name']}:price", 20, 180)
            premium = stable_int(f"{market['city']}:{crop['crop_name']}:premium", 8, 35)
            if crop["is_organic_priority"] == 0:
                premium = max(0, premium - 10)

            conn.execute(
                """
                INSERT OR IGNORE INTO market_demand
                (market_id, crop_id, demand_score, average_price_inr, organic_profit_pct, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (market["market_id"], crop["crop_id"], score, base_price, premium, now),
            )

    for farmer in SAMPLE_FARMERS:
        conn.execute(
            """
            INSERT OR IGNORE INTO farmers
            (full_name, city, state_name, soil_type, farming_experience_years, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer["full_name"],
                farmer["city"],
                farmer["state_name"],
                farmer["soil_type"],
                farmer["farming_experience_years"],
                farmer["email"],
                farmer["phone"],
            ),
        )

    farmer_rows = conn.execute("SELECT farmer_id, full_name FROM farmers").fetchall()
    crop_map = {
        row["crop_name"]: row["crop_id"]
        for row in conn.execute("SELECT crop_id, crop_name FROM crops").fetchall()
    }

    for farmer in SAMPLE_FARMERS:
        farmer_id = next(
            (row["farmer_id"] for row in farmer_rows if row["full_name"] == farmer["full_name"]),
            None,
        )
        if farmer_id is None:
            continue
        for crop_name in farmer["crops"]:
            crop_id = crop_map.get(crop_name)
            if crop_id is None:
                continue
            conn.execute(
                """
                INSERT OR IGNORE INTO farmer_harvests
                (farmer_id, crop_id, season_label, harvested_quantity)
                VALUES (?, ?, ?, ?)
                """,
                (farmer_id, crop_id, "Kharif 2025", stable_int(f"{farmer_id}:{crop_id}:qty", 80, 450)),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO farmer_catalog_preferences
                (farmer_id, crop_id, preferred_price_inr)
                VALUES (?, ?, ?)
                """,
                (
                    farmer_id,
                    crop_id,
                    stable_int(f"{farmer_id}:{crop_id}:pref", 30, 220),
                ),
            )


def init_db():
    conn = db_conn()
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        conn.executescript(schema_file.read())

    crops_count = conn.execute("SELECT COUNT(*) AS count FROM crops").fetchone()["count"]
    markets_count = conn.execute("SELECT COUNT(*) AS count FROM markets").fetchone()["count"]

    if crops_count < 50 or markets_count < 5:
        seed_data(conn)

    conn.commit()
    conn.close()


def json_response(handler, status, payload):
    data = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(data)


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length) if length > 0 else b"{}"
    return json.loads(body.decode("utf-8"))


def ai_fallback_answer(
    question,
    city,
    crop_name=None,
    soil_type=None,
    experience_years=None,
    demand_ctx=None,
    climate_ctx=None,
):
    crop = crop_name or "high-demand organic crops"
    demand_line = ""
    if demand_ctx:
        demand_line = (
            f" In {city}, {demand_ctx['crop_name']} demand score is "
            f"{demand_ctx['demand_score']:.1f} with avg price ₹{demand_ctx['average_price_inr']:.0f}."
        )
    climate_line = ""
    if climate_ctx:
        climate_line = (
            f" Current climate risk is {climate_ctx['risk_level']} "
            f"({climate_ctx['risk_score']}/100)."
        )
    soil_line = f" Soil type noted: {soil_type}." if soil_type else ""
    exp_line = (
        f" With {experience_years} years of experience, scale gradually with weekly tracking."
        if experience_years is not None
        else "Start with a small pilot plot and track weekly cost-profit."
    )
    return (
        f"For your question '{question}': in {city}, focus on {crop} using sustainable practices."
        f"{demand_line}{climate_line}{soil_line} "
        "Use crop rotation, mulch, and efficient irrigation for stable yields. "
        f"{exp_line}"
    )


def demand_context(conn, city, crop_name=None):
    sql = """
        SELECT c.crop_name, md.demand_score, md.average_price_inr, md.organic_profit_pct
        FROM market_demand md
        JOIN markets m ON m.market_id = md.market_id
        JOIN crops c ON c.crop_id = md.crop_id
        WHERE m.city = ?
    """
    params = [city]
    if crop_name:
        sql += " AND c.crop_name = ?"
        params.append(crop_name)
    sql += " ORDER BY c.is_organic_priority DESC, md.demand_score DESC LIMIT 1"
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def ask_gemini(conn, question, city, crop_name=None, soil_type=None, experience_years=None):
    # Uses provided key by default; environment variable can override it.
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDQcBatdyZXCo4MA3s8fIeSncMN0M7kDQE").strip()
    demand_ctx = demand_context(conn, city, crop_name)
    climate_ctx = openweather_climate_risk(conn, city, crop_name)
    if not api_key:
        return (
            ai_fallback_answer(
                question,
                city,
                crop_name=crop_name,
                soil_type=soil_type,
                experience_years=experience_years,
                demand_ctx=demand_ctx,
                climate_ctx=climate_ctx,
            ),
            "fallback",
        )

    prompt = (
        "You are an expert farming advisor for sustainable market-linked agriculture. "
        "Answer directly to the user question with practical steps. "
        "Return concise but actionable advice in 5-8 short lines. "
        f"City: {city}. "
        f"Selected crop: {crop_name or 'Not specified'}. "
        f"Soil type: {soil_type or 'Not specified'}. "
        f"Farmer experience years: {experience_years if experience_years is not None else 'Not specified'}. "
        f"Demand context: {json.dumps(demand_ctx) if demand_ctx else 'not available'}. "
        f"Climate context: {json.dumps(climate_ctx) if climate_ctx else 'not available'}. "
        f"User question: {question}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
        text = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )
        if not text:
            return (
                ai_fallback_answer(
                    question,
                    city,
                    crop_name=crop_name,
                    soil_type=soil_type,
                    experience_years=experience_years,
                    demand_ctx=demand_ctx,
                    climate_ctx=climate_ctx,
                ),
                "fallback",
            )
        return text.strip(), "gemini"
    except Exception:
        return (
            ai_fallback_answer(
                question,
                city,
                crop_name=crop_name,
                soil_type=soil_type,
                experience_years=experience_years,
                demand_ctx=demand_ctx,
                climate_ctx=climate_ctx,
            ),
            "fallback",
        )


def fallback_climate(city):
    templates = {
        "Bengaluru": {
            "risk_level": "Moderate",
            "risk_score": 56,
            "summary": "Heat stress with irregular rain windows.",
            "actions": [
                "Use drip irrigation and mulching.",
                "Increase compost use for moisture retention.",
                "Use preventive pest management after rainfall spikes.",
            ],
        },
        "Pune": {
            "risk_level": "Moderate",
            "risk_score": 60,
            "summary": "Dry spells and high daytime temperature.",
            "actions": [
                "Adopt staggered sowing windows.",
                "Use short-duration crop varieties.",
                "Irrigate during low-evaporation hours.",
            ],
        },
    }
    base = templates.get(
        city,
        {
            "risk_level": "Moderate",
            "risk_score": 58,
            "summary": "Variable weather conditions expected.",
            "actions": [
                "Maintain soil moisture with mulching.",
                "Monitor local forecast before irrigation scheduling.",
                "Use resilient crop rotation and bio-inputs.",
            ],
        },
    )
    return {
        "city": city,
        "provider": "fallback",
        **base,
    }


def crop_adaptation_actions(crop_name, risk_level, max_temp, total_rain, max_wind):
    crop = (crop_name or "").strip().lower()
    level = risk_level.lower()
    base = [
        "Apply mulching and schedule irrigation in low-evaporation hours.",
        "Strengthen drainage and monitor pest activity after weather swings.",
        "Track weekly weather and adjust sowing/harvest windows proactively.",
    ]

    crop_specific = {
        "tomato": [
            "Use staking and pruning to reduce fungal spread after humidity spikes.",
            "Use drip irrigation to avoid leaf wetness and blossom drop in heat.",
        ],
        "rice": [
            "Use field bund strengthening and controlled water depth management.",
            "Adopt short-duration variety if delayed rainfall persists.",
        ],
        "onion": [
            "Avoid waterlogging to prevent bulb rot; improve raised-bed drainage.",
            "Time irrigation carefully near maturity to protect bulb quality.",
        ],
        "banana": [
            "Anchor plants and support pseudo-stems during high wind periods.",
            "Maintain mulch ring to reduce moisture stress and root heat.",
        ],
        "groundnut": [
            "Use ridge-furrow system for better runoff handling in heavy rain.",
            "Apply bio-fungicide seed treatment for disease-prone weather windows.",
        ],
    }

    chosen = crop_specific.get(crop, [])
    severity_line = (
        f"Risk severity is {risk_level}; observed max temp {max_temp:.1f}°C, "
        f"rain {total_rain:.1f} mm, wind {max_wind:.1f} m/s."
    )
    if level == "high":
        base.insert(0, "Prioritize crop protection and avoid major input application before severe weather.")
    return [severity_line] + chosen + base


def openweather_climate_risk(conn, city, crop_name=None):
    key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        return fallback_climate(city)

    market = conn.execute(
        "SELECT latitude, longitude FROM markets WHERE city = ? LIMIT 1",
        (city,),
    ).fetchone()
    if not market or market["latitude"] is None or market["longitude"] is None:
        return fallback_climate(city)

    params = urlencode(
        {
            "lat": market["latitude"],
            "lon": market["longitude"],
            "appid": key,
            "units": "metric",
        }
    )
    url = f"https://api.openweathermap.org/data/2.5/forecast?{params}"
    req = Request(url, headers={"Accept": "application/json"}, method="GET")

    try:
        with urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return fallback_climate(city)

    entries = payload.get("list", [])
    if not entries:
        return fallback_climate(city)

    max_temp = max((entry.get("main", {}).get("temp", 0) for entry in entries), default=0)
    total_rain = 0.0
    max_wind = 0.0
    thunder_count = 0
    for entry in entries:
        rain_3h = entry.get("rain", {}).get("3h", 0) or 0
        total_rain += float(rain_3h)
        wind_speed = float(entry.get("wind", {}).get("speed", 0) or 0)
        if wind_speed > max_wind:
            max_wind = wind_speed
        weather_main = (
            entry.get("weather", [{}])[0].get("main", "").lower()
            if entry.get("weather")
            else ""
        )
        if "thunderstorm" in weather_main:
            thunder_count += 1

    score = 25
    if max_temp >= 39:
        score += 30
    elif max_temp >= 35:
        score += 20
    elif max_temp >= 32:
        score += 12

    if total_rain >= 60:
        score += 28
    elif total_rain >= 30:
        score += 18
    elif total_rain >= 10:
        score += 10

    if max_wind >= 14:
        score += 20
    elif max_wind >= 10:
        score += 12
    elif max_wind >= 7:
        score += 6

    score += min(12, thunder_count * 4)
    score = min(100, int(round(score)))

    if score >= 75:
        level = "High"
    elif score >= 50:
        level = "Moderate"
    else:
        level = "Low"

    summary = (
        f"5-day outlook: max temp {max_temp:.1f}°C, rainfall {total_rain:.1f} mm, "
        f"max wind {max_wind:.1f} m/s."
    )
    actions = crop_adaptation_actions(crop_name, level, max_temp, total_rain, max_wind)

    return {
        "city": city,
        "crop_name": crop_name,
        "provider": "openweather",
        "risk_level": level,
        "risk_score": score,
        "summary": summary,
        "actions": actions,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/health":
            return json_response(self, 200, {"status": "ok", "date": dt.date.today().isoformat()})

        if path == "/api/cities":
            conn = db_conn()
            rows = conn.execute(
                "SELECT city, state_name, market_name FROM markets ORDER BY city"
            ).fetchall()
            conn.close()
            return json_response(self, 200, {"cities": [dict(r) for r in rows]})

        if path == "/api/crops":
            conn = db_conn()
            rows = conn.execute(
                "SELECT crop_id, crop_name, category, preferred_unit, is_organic_priority FROM crops ORDER BY crop_name"
            ).fetchall()
            conn.close()
            return json_response(self, 200, {"count": len(rows), "crops": [dict(r) for r in rows]})

        if path == "/api/farmers":
            conn = db_conn()
            rows = conn.execute(
                """
                SELECT farmer_id, full_name, city, state_name, soil_type, farming_experience_years, email, phone, created_at
                FROM farmers
                ORDER BY farmer_id DESC
                """
            ).fetchall()
            conn.close()
            return json_response(self, 200, {"farmers": [dict(r) for r in rows]})

        if path == "/api/climate-risk":
            city = query.get("city", ["Bengaluru"])[0]
            crop_name = query.get("crop_name", [None])[0]
            conn = db_conn()
            result = openweather_climate_risk(conn, city, crop_name)
            conn.close()
            return json_response(self, 200, result)

        if path == "/api/listings":
            city = query.get("city", [None])[0]
            crop_name = query.get("crop_name", [None])[0]
            conn = db_conn()
            sql = """
                SELECT f.farmer_id, f.full_name, f.city, c.crop_name,
                       CASE WHEN c.is_organic_priority = 1 THEN 'Organic' ELSE 'Standard' END AS farming_type,
                       printf('%.0f kg', fh.harvested_quantity) AS available_qty,
                       COALESCE(fcp.preferred_price_inr, md.average_price_inr) AS preferred_price_inr
                FROM farmers f
                JOIN farmer_harvests fh ON fh.farmer_id = f.farmer_id
                JOIN crops c ON c.crop_id = fh.crop_id
                LEFT JOIN markets m ON m.city = f.city
                LEFT JOIN market_demand md ON md.market_id = m.market_id AND md.crop_id = c.crop_id
                LEFT JOIN farmer_catalog_preferences fcp
                  ON fcp.farmer_id = f.farmer_id AND fcp.crop_id = c.crop_id
            """
            params = []
            if city:
                sql += " WHERE f.city = ?"
                params.append(city)
            if crop_name:
                sql += " AND c.crop_name = ?" if city else " WHERE c.crop_name = ?"
                params.append(crop_name)
            sql += " ORDER BY f.full_name, c.crop_name"
            rows = conn.execute(sql, params).fetchall()

            # Ensure listings are always available for selected city/crop by
            # generating market-backed direct listing rows when farmer rows are missing.
            if len(rows) == 0 and city:
                fallback_sql = """
                    SELECT m.city, c.crop_name, c.is_organic_priority, md.average_price_inr
                    FROM market_demand md
                    JOIN markets m ON m.market_id = md.market_id
                    JOIN crops c ON c.crop_id = md.crop_id
                    WHERE m.city = ?
                """
                fallback_params = [city]
                if crop_name:
                    fallback_sql += " AND c.crop_name = ?"
                    fallback_params.append(crop_name)
                fallback_sql += " ORDER BY c.is_organic_priority DESC, md.demand_score DESC LIMIT 8"
                fallback_rows = conn.execute(fallback_sql, fallback_params).fetchall()

                farmer_name_pool = [
                    "Farmer Collective A",
                    "Green Soil Growers",
                    "Village Harvest Group",
                    "Organic Field Network",
                    "Sustainable Farm Cluster",
                ]

                synthesized = []
                for idx, row in enumerate(fallback_rows):
                    qty = stable_int(f"{row['city']}:{row['crop_name']}:listing_qty", 90, 500)
                    synthesized.append(
                        {
                            "farmer_id": None,
                            "full_name": farmer_name_pool[idx % len(farmer_name_pool)],
                            "city": row["city"],
                            "crop_name": row["crop_name"],
                            "farming_type": "Organic" if row["is_organic_priority"] == 1 else "Standard",
                            "available_qty": f"{qty} kg",
                            "preferred_price_inr": row["average_price_inr"],
                        }
                    )
                conn.close()
                return json_response(self, 200, {"listings": synthesized})

            conn.close()
            return json_response(self, 200, {"listings": [dict(r) for r in rows]})

        if path.startswith("/api/cities/") and path.endswith("/demand"):
            city = unquote(path.split("/")[3])
            organic_first = query.get("organic_first", ["true"])[0].lower() != "false"
            crop_id = query.get("crop_id", [None])[0]
            conn = db_conn()
            order = (
                "c.is_organic_priority DESC, md.demand_score DESC, c.crop_name ASC"
                if organic_first
                else "md.demand_score DESC, c.crop_name ASC"
            )
            where = "WHERE m.city = ?"
            params = [city]
            if crop_id:
                where += " AND c.crop_id = ?"
                params.append(crop_id)
            rows = conn.execute(
                f"""
                SELECT c.crop_id, c.crop_name, c.category, c.preferred_unit,
                       c.is_organic_priority, md.demand_score,
                       md.average_price_inr, md.organic_profit_pct,
                       m.city, m.market_name, md.last_updated
                FROM market_demand md
                JOIN markets m ON m.market_id = md.market_id
                JOIN crops c ON c.crop_id = md.crop_id
                {where}
                ORDER BY {order}
                """,
                params,
            ).fetchall()
            conn.close()
            return json_response(self, 200, {"city": city, "count": len(rows), "crops": [dict(r) for r in rows]})

        if path == "/api/catalog/preferences":
            farmer_id = query.get("farmer_id", [None])[0]
            if not farmer_id:
                return json_response(self, 400, {"error": "farmer_id is required"})
            conn = db_conn()
            rows = conn.execute(
                """
                SELECT fcp.preference_id, fcp.farmer_id, c.crop_name, fcp.preferred_price_inr, fcp.updated_at
                FROM farmer_catalog_preferences fcp
                JOIN crops c ON c.crop_id = fcp.crop_id
                WHERE fcp.farmer_id = ?
                ORDER BY c.crop_name
                """,
                (farmer_id,),
            ).fetchall()
            conn.close()
            return json_response(self, 200, {"farmer_id": farmer_id, "preferences": [dict(r) for r in rows]})

        return self.serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/farmers":
            payload = read_json(self)
            required = ["full_name", "city", "soil_type", "farming_experience_years"]
            missing = [field for field in required if not payload.get(field)]
            if missing:
                return json_response(self, 400, {"error": f"missing required fields: {', '.join(missing)}"})
            if not payload.get("email") and not payload.get("phone"):
                return json_response(self, 400, {"error": "email or phone is required"})

            conn = db_conn()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO farmers
                (full_name, city, state_name, soil_type, farming_experience_years, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["full_name"],
                    payload["city"],
                    payload.get("state_name"),
                    payload["soil_type"],
                    int(payload["farming_experience_years"]),
                    payload.get("email"),
                    payload.get("phone"),
                ),
            )
            farmer_id = cur.lastrowid

            crops_harvested = payload.get("crops_harvested", [])
            if isinstance(crops_harvested, list):
                for crop_name in crops_harvested:
                    crop_row = conn.execute(
                        "SELECT crop_id FROM crops WHERE crop_name = ?",
                        (crop_name,),
                    ).fetchone()
                    if crop_row:
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO farmer_harvests
                            (farmer_id, crop_id, season_label, harvested_quantity)
                            VALUES (?, ?, ?, ?)
                            """,
                            (farmer_id, crop_row["crop_id"], payload.get("season_label", "Recent"), payload.get("harvested_quantity", 0)),
                        )

            conn.commit()
            conn.close()
            return json_response(self, 201, {"message": "farmer created", "farmer_id": farmer_id})

        if path == "/api/catalog/preferences":
            payload = read_json(self)
            required = ["farmer_id", "crop_id", "preferred_price_inr"]
            missing = [field for field in required if payload.get(field) is None]
            if missing:
                return json_response(self, 400, {"error": f"missing required fields: {', '.join(missing)}"})

            conn = db_conn()
            conn.execute(
                """
                INSERT INTO farmer_catalog_preferences (farmer_id, crop_id, preferred_price_inr)
                VALUES (?, ?, ?)
                ON CONFLICT(farmer_id, crop_id)
                DO UPDATE SET preferred_price_inr=excluded.preferred_price_inr, updated_at=CURRENT_TIMESTAMP
                """,
                (int(payload["farmer_id"]), int(payload["crop_id"]), float(payload["preferred_price_inr"])),
            )
            conn.commit()
            conn.close()
            return json_response(self, 200, {"message": "preference saved"})

        if path == "/api/ai/ask":
            payload = read_json(self)
            question = str(payload.get("question", "")).strip()
            city = str(payload.get("city", "Bengaluru")).strip()
            crop_name = str(payload.get("crop_name", "")).strip() or None
            soil_type = str(payload.get("soil_type", "")).strip() or None
            experience_years = payload.get("experience_years")
            try:
                experience_years = int(experience_years) if experience_years is not None else None
            except Exception:
                experience_years = None
            if not question:
                return json_response(self, 400, {"error": "question is required"})

            conn = db_conn()
            answer, provider = ask_gemini(
                conn,
                question,
                city,
                crop_name=crop_name,
                soil_type=soil_type,
                experience_years=experience_years,
            )
            conn.close()
            return json_response(self, 200, {"answer": answer, "provider": provider})

        return json_response(self, 404, {"error": "not found"})

    def serve_static(self, path):
        target = "index.html" if path in ("", "/") else path.lstrip("/")
        file_path = (WEB_DIR / target).resolve()

        if not str(file_path).startswith(str(WEB_DIR.resolve())) or not file_path.exists() or not file_path.is_file():
            return json_response(self, 404, {"error": "not found"})

        mime = "text/plain"
        if file_path.suffix == ".html":
            mime = "text/html; charset=utf-8"
        elif file_path.suffix == ".css":
            mime = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            mime = "application/javascript; charset=utf-8"
        elif file_path.suffix == ".json":
            mime = "application/json; charset=utf-8"

        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"FarmBridge server running on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
