"""
generate_synthetic.py
Generates a realistic synthetic concert dataset covering the full live-music spectrum:
  - Emerging artists (club/theater, low occupancy, low prices)
  - Mid-tier artists  (arena, moderate occupancy, mid prices)
  - Major headliners  (large arena/stadium, high occupancy, premium prices)

This complements the mega-star Kaggle data with variance needed for meaningful analysis.
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'synthetic_concerts.csv')

# ── REPRODUCIBLE SEED ──────────────────────────────────────────────────────────
RNG = np.random.default_rng(42)
random.seed(42)

# ── ARTIST ROSTER ──────────────────────────────────────────────────────────────
# Each artist: tier, genre, base_occ (mean), occ_std, price_range, cap_range, n_tours
ARTISTS = [
    # Emerging / DIY (club & theater, 35-70% occ)
    {"name": "Clairo",            "tier": "Emerging Artist",       "genre": "Indie Pop",          "base_occ": 58,  "occ_std": 10, "price": (22, 55),   "cap": (800,  4000),  "shows_per_tour": 28},
    {"name": "Phoebe Bridgers",   "tier": "Emerging Artist",       "genre": "Indie Folk",         "base_occ": 65,  "occ_std": 9,  "price": (28, 65),   "cap": (1200, 5000),  "shows_per_tour": 25},
    {"name": "Mitski",            "tier": "Emerging Artist",       "genre": "Indie Rock",         "base_occ": 62,  "occ_std": 11, "price": (25, 60),   "cap": (900,  4500),  "shows_per_tour": 30},
    {"name": "Soccer Mommy",      "tier": "Emerging Artist",       "genre": "Indie Rock",         "base_occ": 50,  "occ_std": 12, "price": (18, 45),   "cap": (500,  2500),  "shows_per_tour": 22},
    {"name": "Snail Mail",        "tier": "Emerging Artist",       "genre": "Indie Rock",         "base_occ": 48,  "occ_std": 13, "price": (15, 40),   "cap": (400,  2000),  "shows_per_tour": 18},
    {"name": "Girl in Red",       "tier": "Emerging Artist",       "genre": "Indie Pop",          "base_occ": 60,  "occ_std": 10, "price": (22, 52),   "cap": (600,  3500),  "shows_per_tour": 24},
    {"name": "Rex Orange County", "tier": "Emerging Artist",       "genre": "Indie Pop",          "base_occ": 63,  "occ_std": 10, "price": (28, 65),   "cap": (1000, 5000),  "shows_per_tour": 26},

    # Mid-tier (arena, 65-85% occ)
    {"name": "Lewis Capaldi",     "tier": "Mid-Tier Touring Artist","genre": "Pop / Singer-Songwriter","base_occ": 78, "occ_std": 8, "price": (55, 110),  "cap": (5000, 18000), "shows_per_tour": 35},
    {"name": "The 1975",          "tier": "Mid-Tier Touring Artist","genre": "Indie / Alternative", "base_occ": 76, "occ_std": 8,  "price": (60, 120),  "cap": (6000, 20000), "shows_per_tour": 40},
    {"name": "Hozier",            "tier": "Mid-Tier Touring Artist","genre": "Folk / Blues Rock",   "base_occ": 74, "occ_std": 9,  "price": (55, 105),  "cap": (4000, 16000), "shows_per_tour": 32},
    {"name": "Lizzo",             "tier": "Mid-Tier Touring Artist","genre": "Pop / R&B",           "base_occ": 80, "occ_std": 8,  "price": (65, 130),  "cap": (8000, 22000), "shows_per_tour": 38},
    {"name": "Lorde",             "tier": "Mid-Tier Touring Artist","genre": "Indie Pop",           "base_occ": 77, "occ_std": 9,  "price": (60, 115),  "cap": (6000, 20000), "shows_per_tour": 30},
    {"name": "Khalid",            "tier": "Mid-Tier Touring Artist","genre": "R&B / Pop",           "base_occ": 72, "occ_std": 10, "price": (50, 100),  "cap": (5000, 17000), "shows_per_tour": 33},
    {"name": "Troye Sivan",       "tier": "Mid-Tier Touring Artist","genre": "Pop",                 "base_occ": 75, "occ_std": 8,  "price": (55, 110),  "cap": (5000, 16000), "shows_per_tour": 30},
    {"name": "Conan Gray",        "tier": "Mid-Tier Touring Artist","genre": "Indie Pop",           "base_occ": 71, "occ_std": 10, "price": (48, 100),  "cap": (4000, 15000), "shows_per_tour": 28},
    {"name": "Gracie Abrams",     "tier": "Mid-Tier Touring Artist","genre": "Indie Pop",           "base_occ": 68, "occ_std": 10, "price": (45, 90),   "cap": (3500, 12000), "shows_per_tour": 26},

    # Upper mid-tier / large arena (80-93% occ)
    {"name": "Dua Lipa",          "tier": "Major Touring Artist",  "genre": "Pop / Dance",         "base_occ": 89, "occ_std": 6,  "price": (90, 185),  "cap": (12000, 40000),"shows_per_tour": 50},
    {"name": "Post Malone",       "tier": "Major Touring Artist",  "genre": "Hip-Hop / Pop",       "base_occ": 85, "occ_std": 7,  "price": (80, 165),  "cap": (10000, 35000),"shows_per_tour": 45},
    {"name": "Billie Eilish",     "tier": "Major Touring Artist",  "genre": "Alt Pop",             "base_occ": 91, "occ_std": 5,  "price": (95, 200),  "cap": (14000, 42000),"shows_per_tour": 48},
    {"name": "Olivia Rodrigo",    "tier": "Major Touring Artist",  "genre": "Pop / Alt Pop",       "base_occ": 93, "occ_std": 5,  "price": (100, 210), "cap": (15000, 45000),"shows_per_tour": 40},
    {"name": "SZA",               "tier": "Major Touring Artist",  "genre": "R&B / Neo Soul",      "base_occ": 87, "occ_std": 6,  "price": (85, 175),  "cap": (12000, 38000),"shows_per_tour": 42},
    {"name": "Arctic Monkeys",    "tier": "Major Touring Artist",  "genre": "Indie Rock",          "base_occ": 88, "occ_std": 6,  "price": (80, 170),  "cap": (15000, 50000),"shows_per_tour": 45},
    {"name": "Kendrick Lamar",    "tier": "Major Touring Artist",  "genre": "Hip-Hop",             "base_occ": 90, "occ_std": 5,  "price": (90, 190),  "cap": (15000, 48000),"shows_per_tour": 35},
    {"name": "Tyler the Creator", "tier": "Major Touring Artist",  "genre": "Hip-Hop / Alternative","base_occ": 86, "occ_std": 7, "price": (75, 155),  "cap": (10000, 35000),"shows_per_tour": 38},
    {"name": "Sabrina Carpenter", "tier": "Major Touring Artist",  "genre": "Pop",                 "base_occ": 92, "occ_std": 5,  "price": (95, 195),  "cap": (12000, 40000),"shows_per_tour": 38},
    {"name": "Chappell Roan",     "tier": "Major Touring Artist",  "genre": "Pop / Camp Pop",      "base_occ": 88, "occ_std": 6,  "price": (80, 170),  "cap": (8000,  32000),"shows_per_tour": 32},
]

# ── VENUE POOL ─────────────────────────────────────────────────────────────────
# (city, country, continent, lat, lng, market_tier)
CITY_POOL = [
    # North America — Tier 1
    ("New York",      "United States", "North America",  40.7128, -74.0060, "Tier 1 Global Mega-City"),
    ("Los Angeles",   "United States", "North America",  34.0522,-118.2437, "Tier 1 Global Mega-City"),
    ("Chicago",       "United States", "North America",  41.8781, -87.6298, "Tier 1 Global Mega-City"),
    ("Toronto",       "Canada",        "North America",  43.6532, -79.3832, "Tier 1 Global Mega-City"),
    # North America — Tier 2
    ("Atlanta",       "United States", "North America",  33.7490, -84.3880, "Tier 2 Major Regional Market"),
    ("Houston",       "United States", "North America",  29.7604, -95.3698, "Tier 2 Major Regional Market"),
    ("Seattle",       "United States", "North America",  47.6062,-122.3321, "Tier 2 Major Regional Market"),
    ("Boston",        "United States", "North America",  42.3601, -71.0589, "Tier 2 Major Regional Market"),
    ("Miami",         "United States", "North America",  25.7617, -80.1918, "Tier 2 Major Regional Market"),
    ("Philadelphia",  "United States", "North America",  39.9526, -75.1652, "Tier 2 Major Regional Market"),
    ("Denver",        "United States", "North America",  39.7392,-104.9903, "Tier 2 Major Regional Market"),
    ("Nashville",     "United States", "North America",  36.1627, -86.7816, "Tier 2 Major Regional Market"),
    ("Vancouver",     "Canada",        "North America",  49.2827,-123.1207, "Tier 2 Major Regional Market"),
    # North America — Tier 3
    ("Kansas City",   "United States", "North America",  39.0997, -94.5786, "Tier 3 Emerging / Secondary Market"),
    ("Salt Lake City","United States", "North America",  40.7608,-111.8910, "Tier 3 Emerging / Secondary Market"),
    ("Columbus",      "United States", "North America",  39.9612, -82.9988, "Tier 3 Emerging / Secondary Market"),
    ("Richmond",      "United States", "North America",  37.5407, -77.4360, "Tier 3 Emerging / Secondary Market"),
    # Europe — Tier 1
    ("London",        "United Kingdom","Europe",          51.5074,  -0.1278, "Tier 1 Global Mega-City"),
    ("Paris",         "France",        "Europe",          48.8566,   2.3522, "Tier 1 Global Mega-City"),
    ("Berlin",        "Germany",       "Europe",          52.5200,  13.4050, "Tier 1 Global Mega-City"),
    ("Amsterdam",     "Netherlands",   "Europe",          52.3676,   4.9041, "Tier 1 Global Mega-City"),
    # Europe — Tier 2
    ("Manchester",    "United Kingdom","Europe",          53.4808,  -2.2426, "Tier 2 Major Regional Market"),
    ("Dublin",        "Ireland",       "Europe",          53.3498,  -6.2603, "Tier 2 Major Regional Market"),
    ("Brussels",      "Belgium",       "Europe",          50.8503,   4.3517, "Tier 2 Major Regional Market"),
    ("Stockholm",     "Sweden",        "Europe",          59.3293,  18.0686, "Tier 2 Major Regional Market"),
    ("Copenhagen",    "Denmark",       "Europe",          55.6761,  12.5683, "Tier 2 Major Regional Market"),
    ("Oslo",          "Norway",        "Europe",          59.9139,  10.7522, "Tier 2 Major Regional Market"),
    ("Warsaw",        "Poland",        "Europe",          52.2297,  21.0122, "Tier 3 Emerging / Secondary Market"),
    ("Lisbon",        "Portugal",      "Europe",          38.7223,  -9.1393, "Tier 2 Major Regional Market"),
    ("Barcelona",     "Spain",         "Europe",          41.3851,   2.1734, "Tier 2 Major Regional Market"),
    ("Madrid",        "Spain",         "Europe",          40.4168,  -3.7038, "Tier 2 Major Regional Market"),
    # Oceania
    ("Sydney",        "Australia",     "Oceania",        -33.8688, 151.2093, "Tier 2 Major Regional Market"),
    ("Melbourne",     "Australia",     "Oceania",        -37.8136, 144.9631, "Tier 2 Major Regional Market"),
    ("Brisbane",      "Australia",     "Oceania",        -27.4698, 153.0251, "Tier 2 Major Regional Market"),
    ("Auckland",      "New Zealand",   "Oceania",        -36.8485, 174.7633, "Tier 2 Major Regional Market"),
    # Asia
    ("Tokyo",         "Japan",         "Asia",            35.6762, 139.6503, "Tier 1 Global Mega-City"),
    ("Seoul",         "South Korea",   "Asia",            37.5665, 126.9780, "Tier 1 Global Mega-City"),
    ("Singapore",     "Singapore",     "Asia",             1.3521, 103.8198, "Tier 2 Major Regional Market"),
    ("Bangkok",       "Thailand",      "Asia",            13.7563, 100.5018, "Tier 2 Major Regional Market"),
    ("Manila",        "Philippines",   "Asia",            14.5995, 120.9842, "Tier 3 Emerging / Secondary Market"),
    # Latin America
    ("Mexico City",   "Mexico",        "Latin America",   19.4326, -99.1332, "Tier 1 Global Mega-City"),
    ("Buenos Aires",  "Argentina",     "Latin America",  -34.6037, -58.3816, "Tier 2 Major Regional Market"),
    ("Sao Paulo",     "Brazil",        "Latin America",  -23.5505, -46.6333, "Tier 1 Global Mega-City"),
    ("Bogota",        "Colombia",      "Latin America",    4.7110, -74.0721, "Tier 2 Major Regional Market"),
    ("Santiago",      "Chile",         "Latin America",  -33.4569, -70.6483, "Tier 2 Major Regional Market"),
]

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKEND = {"Friday","Saturday","Sunday"}


def _venue_type(cap):
    if cap < 3000:
        return "Club / Theater"
    elif cap < 12000:
        return "Arena"
    elif cap < 25000:
        return "Large Arena"
    else:
        return "Stadium"


def _season(month, continent):
    southern = continent in ("Oceania", "Latin America")
    if month in (12, 1, 2):
        return "Winter" if not southern else "Summer"
    elif month in (3, 4, 5):
        return "Spring" if not southern else "Fall"
    elif month in (6, 7, 8):
        return "Summer" if not southern else "Winter"
    else:
        return "Fall" if not southern else "Spring"


def compute_occ(artist_dict, city_row, date, avg_price, openers, seed):
    """Returns realistic occupancy % given all influencing factors."""
    rng2 = np.random.default_rng(seed)
    base = artist_dict["base_occ"]

    # Market tier
    tier = city_row[5]
    if "Tier 1" in tier:
        base += 5
    elif "Tier 3" in tier:
        base -= 10

    # Day of week
    dow = date.strftime("%A")
    if dow in ("Friday", "Saturday"):
        base += 4
    elif dow in ("Tuesday", "Wednesday"):
        base -= 7

    # Year (COVID trough 2020–21)
    yr = date.year
    if yr == 2020:
        base -= 25
    elif yr == 2021:
        base -= 12
    elif yr >= 2023:
        base += 3

    # Price elasticity — expensive tickets in weak markets hurt fill
    if avg_price > 120 and "Tier 3" in tier:
        base -= 8
    if avg_price > 200 and "Tier 1" not in tier:
        base -= 6

    # Opening acts boost turnout
    if openers >= 2:
        base += 3
    elif openers == 1:
        base += 1.5

    # Month seasonality (summer is peak for outdoor / stadium)
    m = date.month
    if m in (6, 7, 8):
        base += 2.5
    elif m in (1, 2):
        base -= 4

    noise = float(rng2.normal(0, artist_dict["occ_std"]))
    return round(float(np.clip(base + noise, 35.0, 100.0)), 2)


def generate_tours():
    records = []
    concert_counter = 9000  # offset from existing CNC-XXXX IDs

    for artist in ARTISTS:
        # Each artist does 1 tour; pick a plausible year
        if artist["tier"] == "Emerging Artist":
            year = random.choice([2018, 2019, 2022, 2023])
        elif artist["tier"] == "Mid-Tier Touring Artist":
            year = random.choice([2019, 2022, 2023, 2024])
        else:
            year = random.choice([2022, 2023, 2024])

        tour_name = f"{artist['name']} — {year} Tour"
        n_shows = artist["shows_per_tour"]

        # Route: pick cities weighted by artist tier
        if artist["tier"] == "Emerging Artist":
            # Mostly North America + some Europe
            pool = [c for c in CITY_POOL if c[2] in ("North America", "Europe")]
        elif artist["tier"] == "Mid-Tier Touring Artist":
            pool = [c for c in CITY_POOL if c[2] in ("North America", "Europe", "Oceania")]
        else:
            pool = CITY_POOL  # worldwide

        chosen_cities = random.choices(pool, k=n_shows)

        # Generate show dates spread across ~6 months
        start_month = random.randint(3, 9)
        start_day   = random.randint(1, 15)
        try:
            start_date = datetime(year, start_month, start_day)
        except ValueError:
            start_date = datetime(year, 3, 1)

        city_visit_counts = {}
        for i, city_row in enumerate(chosen_cities):
            concert_counter += 1
            date = start_date + timedelta(days=i * random.randint(2, 5))
            if date.year != year:
                date = datetime(year, 12, 28)

            city_name = city_row[0]
            city_visit_counts[city_name] = city_visit_counts.get(city_name, 0) + 1

            # Venue capacity — pick within artist range
            cap_lo, cap_hi = artist["cap"]
            capacity = int(RNG.integers(cap_lo, cap_hi + 1))

            # Ticket price — scale with capacity (bigger shows = higher prices)
            p_lo, p_hi = artist["price"]
            price_scale = (capacity - cap_lo) / max(cap_hi - cap_lo, 1)
            avg_price = round(float(p_lo + price_scale * (p_hi - p_lo) + RNG.normal(0, 8)), 2)
            avg_price = max(p_lo * 0.7, avg_price)

            # Openers
            openers = int(RNG.integers(0, 3))

            # Compute occupancy
            occ = compute_occ(artist, city_row, date, avg_price, openers, seed=concert_counter)

            attendance = int(round(capacity * occ / 100.0))
            attendance = max(50, attendance)
            gross = round(attendance * avg_price, 2)

            records.append({
                "concert_id":         f"SYN-{concert_counter:05d}",
                "artist":             artist["name"],
                "tour":               tour_name,
                "genre":              artist["genre"],
                "artist_tier":        artist["tier"],
                "date":               date.strftime("%Y-%m-%d"),
                "year":               date.year,
                "month":              date.month,
                "month_name":         date.strftime("%B"),
                "day_of_week":        date.strftime("%A"),
                "is_weekend":         date.strftime("%A") in WEEKEND,
                "season":             _season(date.month, city_row[2]),
                "city":               city_name,
                "country":            city_row[1],
                "continent":          city_row[2],
                "market_tier":        city_row[5],
                "latitude":           city_row[3],
                "longitude":          city_row[4],
                "venue":              f"{city_name} {'Stadium' if capacity > 25000 else 'Arena' if capacity > 3000 else 'Music Hall'}",
                "venue_type":         _venue_type(capacity),
                "opening_acts":       f"Opener {i % 3 + 1}" if openers else "",
                "opening_acts_count": openers,
                "attendance":         attendance,
                "capacity":           capacity,
                "occupancy_rate":     occ,
                "is_sellout":         occ >= 95.0,
                "gross_usd":          gross,
                "avg_ticket_price":   avg_price,
                "price_tier":         (
                    "Budget (<$75)" if avg_price < 75
                    else "Standard ($75-$150)" if avg_price <= 150
                    else "Premium ($150-$250)" if avg_price <= 250
                    else "VIP / Luxury (>$250)"
                ),
                "shows_in_city":      city_visit_counts[city_name],
                "is_multi_night":     city_visit_counts[city_name] > 1,
                "source":             "Synthetic (Industry Model)"
            })

    return records


if __name__ == "__main__":
    print("Generating synthetic long-tail concert dataset...")
    records = generate_tours()
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} synthetic concerts")
    print(f"Occupancy — mean:{df.occupancy_rate.mean():.1f}%  std:{df.occupancy_rate.std():.1f}%  min:{df.occupancy_rate.min():.1f}%  max:{df.occupancy_rate.max():.1f}%")
    print(f"Attendance — mean:{df.attendance.mean():.0f}  std:{df.attendance.std():.0f}  min:{df.attendance.min()}  max:{df.attendance.max()}")
    print(f"Saved to: {OUTPUT_PATH}")
