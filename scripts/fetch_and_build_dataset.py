import os
import io
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def parse_html_table(table):
    """Accurately expands HTML tables with rowspan and colspan into a clean 2D rectangular grid."""
    rows = table.find_all('tr')
    grid = []
    for r_idx, r in enumerate(rows):
        cells = r.find_all(['th', 'td'])
        c_idx = 0
        while len(grid) <= r_idx:
            grid.append([])
        for cell in cells:
            rowspan = int(cell.get('rowspan', 1))
            colspan = int(cell.get('colspan', 1))
            text = cell.get_text(" ", strip=True)
            
            while c_idx < len(grid[r_idx]) and grid[r_idx][c_idx] is not None:
                c_idx += 1
            
            for dr in range(rowspan):
                while len(grid) <= r_idx + dr:
                    grid.append([])
                for dc in range(colspan):
                    while len(grid[r_idx + dr]) <= c_idx + dc:
                        grid[r_idx + dr].append(None)
                    grid[r_idx + dr][c_idx + dc] = text
            c_idx += colspan
    return grid

def fetch_wikipedia_tour(url, artist, tour_name, default_genre):
    print(f"Fetching Wikipedia tour: {artist} - {tour_name}...")
    try:
        req = requests.get(url, headers=HEADERS, timeout=30)
        if req.status_code != 200:
            print(f"  Failed with HTTP {req.status_code}")
            return []
        
        soup = BeautifulSoup(req.text, 'html.parser')
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        records = []
        for t in tables:
            grid = parse_html_table(t)
            if not grid or len(grid) < 2:
                continue
            
            headers = [str(h).lower() if h else "" for h in grid[0]]
            
            has_date = any('date' in h for h in headers)
            has_city = any('city' in h for h in headers)
            has_attendance = any('attendance' in h for h in headers)
            
            if not (has_date and has_city and has_attendance):
                continue
            
            date_idx = next(i for i, h in enumerate(headers) if 'date' in h)
            city_idx = next(i for i, h in enumerate(headers) if 'city' in h)
            country_idx = next((i for i, h in enumerate(headers) if 'country' in h), None)
            venue_idx = next((i for i, h in enumerate(headers) if 'venue' in h), None)
            att_idx = next(i for i, h in enumerate(headers) if 'attendance' in h)
            rev_idx = next((i for i, h in enumerate(headers) if 'revenue' in h or 'gross' in h), None)
            act_idx = next((i for i, h in enumerate(headers) if 'act' in h or 'support' in h), None)

            # Year hint from header or table caption
            year_hint = ""
            date_header = headers[date_idx]
            year_match = re.search(r'20\d\d|19\d\d', date_header)
            if year_match:
                year_hint = year_match.group(0)

            for row in grid[1:]:
                if len(row) <= att_idx:
                    continue
                
                date_val = str(row[date_idx]) if row[date_idx] else ""
                city_val = str(row[city_idx]) if row[city_idx] else ""
                country_val = str(row[country_idx]) if (country_idx is not None and row[country_idx]) else ""
                venue_val = str(row[venue_idx]) if (venue_idx is not None and row[venue_idx]) else ""
                att_val = str(row[att_idx]) if row[att_idx] else ""
                rev_val = str(row[rev_idx]) if (rev_idx is not None and len(row) > rev_idx and row[rev_idx]) else ""
                act_val = str(row[act_idx]) if (act_idx is not None and len(row) > act_idx and row[act_idx]) else ""

                # Filter cancelled, postponed, or footnotes
                full_text = " ".join([date_val, city_val, venue_val, att_val]).lower()
                if "cancelled" in full_text or "postponed" in full_text or "total" in full_text:
                    continue
                
                # Clean brackets [1], [a]
                date_clean = re.sub(r'\[.*?\]', '', date_val).strip()
                city_clean = re.sub(r'\[.*?\]', '', city_val).strip()
                country_clean = re.sub(r'\[.*?\]', '', country_val).strip()
                venue_clean = re.sub(r'\[.*?\]', '', venue_val).strip()
                att_clean = re.sub(r'\[.*?\]', '', att_val).strip()
                rev_clean = re.sub(r'\[.*?\]', '', rev_val).strip()
                act_clean = re.sub(r'\[.*?\]', '', act_val).strip()

                if not att_clean or att_clean in ["—", "TBA", "N/A", "-"]:
                    continue
                if not any(char.isdigit() for char in att_clean):
                    continue
                
                # Append year hint if date lacks year
                if year_hint and not re.search(r'20\d\d|19\d\d', date_clean):
                    date_clean = f"{date_clean} {year_hint}"

                records.append({
                    "artist": artist,
                    "tour": tour_name,
                    "genre": default_genre,
                    "date_str": date_clean,
                    "city": city_clean,
                    "country": country_clean,
                    "venue": venue_clean,
                    "opening_acts": act_clean,
                    "attendance_raw": att_clean,
                    "revenue_raw": rev_clean,
                    "source": "Wikipedia / Billboard Boxscore"
                })

        print(f"  Extracted {len(records)} clean tour records for {artist} ({tour_name})")
        return records
    except Exception as e:
        print(f"  Error parsing {url}: {e}")
        return []

if __name__ == "__main__":
    tours = [
        ("https://en.wikipedia.org/wiki/Music_of_the_Spheres_World_Tour", "Coldplay", "Music of the Spheres World Tour", "Alternative Rock"),
        ("https://en.wikipedia.org/wiki/Renaissance_World_Tour", "Beyoncé", "Renaissance World Tour", "R&B / Pop"),
        ("https://en.wikipedia.org/wiki/Love_on_Tour", "Harry Styles", "Love on Tour", "Pop Rock"),
        ("https://en.wikipedia.org/wiki/After_Hours_til_Dawn_Tour", "The Weeknd", "After Hours til Dawn Tour", "R&B / Pop"),
        ("https://en.wikipedia.org/wiki/U2_360%C2%B0_Tour", "U2", "U2 360° Tour", "Rock"),
        ("https://en.wikipedia.org/wiki/Farewell_Yellow_Brick_Road", "Elton John", "Farewell Yellow Brick Road", "Classic Rock"),
        ("https://en.wikipedia.org/wiki/World%27s_Hottest_Tour", "Bad Bunny", "World's Hottest Tour", "Latin / Reggaeton"),
        ("https://en.wikipedia.org/wiki/%C3%B7_Tour", "Ed Sheeran", "÷ Tour", "Pop / Singer-Songwriter"),
    ]
    
    all_recs = []
    for url, artist, tour, genre in tours:
        recs = fetch_wikipedia_tour(url, artist, tour, genre)
        all_recs.extend(recs)
        
    df_wiki = pd.DataFrame(all_recs)
    dest = os.path.join(RAW_DIR, "wikipedia_world_tours.csv")
    df_wiki.to_csv(dest, index=False, encoding='utf-8')
    print(f"\nSaved {len(df_wiki)} high-precision concert dates to {dest}")
