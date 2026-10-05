# SONAR // Global Concert Turnout Intelligence & Econometrics

An end-to-end data science, machine learning, and web visualization project analyzing the factors governing audience turnout across **1,829 concert dates** worldwide, representing **86.97 million tickets sold** and **$11.70 billion** in global box office revenue.

---

## 🌟 Project Highlights

- **Dataset Acquisition**: Ingested and unified multiple Kaggle datasets (`gayu14/taylor-concert-tours-impact-on-attendance-and`, `tymonbot/taylor-swift-eras-toure`, `jessalynlim/ed-sheeran-tour`, `rodolfobrandao95/oasis-live-25`) alongside official Billboard Boxscore & Pollstar concert logs across 10 major global artists (Taylor Swift, Coldplay, Ed Sheeran, Beyoncé, Harry Styles, The Weeknd, U2, Elton John, Bad Bunny, Oasis).
- **Data Cleaning & Harmonization**: Standardized residency lump sums, currency formats, multi-format dates, venue taxonomy, and geocoded 289 unique world cities across 6 continents and 62 countries.
- **Statistical & Factor Analysis**: Explored 6 core drivers of live music turnout: Venue Capacity, Ticket Pricing, Continental Culture, Multi-Night Stacking, Day of Week / Seasonality, and Support Acts.
- **Machine Learning**: Trained a 120-tree Random Forest Regressor yielding **$R^2 = 0.9970$**, **RMSE = 1,374 attendees**, and **MAPE = 0.86%**.
- **Minimal Dark-Themed Website**: Sleek obsidian/slate web dashboard featuring real-time Chart.js visualizers, an interactive Leaflet world map with CartoDB Dark Matter tiles, a predictive what-if turnout simulator, and a searchable/exportable data explorer.

---

## 📊 Summary Metrics

| Metric | Value |
| :--- | :--- |
| **Total Concerts Analyzed** | **1,829 shows** |
| **Total Global Attendance** | **86,966,022 attendees** |
| **Total Gross Revenue** | **\$11,701,051,910 USD** |
| **Mean Turnout per Show** | **47,548 attendees** |
| **Average Occupancy Rate** | **99.62%** |
| **Strict Sellout Rate (≥99%)** | **95.79% of all shows** |
| **Average Ticket Price** | **\$129.45 USD** |
| **Geographic Scope** | **6 Continents &middot; 62 Countries &middot; 289 Cities** |

---

## 🔍 Key Analytical Findings

### 1. Physical Capacity as the Supreme Bottleneck
- In superstar touring, audience demand vastly exceeds venue supply.
- Stadiums average **62,340 fans/show** at **99.8% capacity**, while arenas average **19,410 fans/show**.
- Physical capacity correlates with turnout at **$r = 0.9985$**, accounting for **99.74%** of feature importance in predictive ML modeling.

### 2. Super-Fan Price Inelasticity (Veblen Good Dynamics)
- Average turnout remains steady at **>99.4% capacity** across all price tiers:
  - Budget Tier (<\$75): **99.4% occupancy**
  - Standard Tier (\$75–\$150): **99.6% occupancy**
  - Premium Tier (\$150–\$250): **99.7% occupancy**
  - VIP Tier (>\$250): **99.8% occupancy**
- Promoters capture exponential gross revenue by raising price without suffering audience decay.

### 3. Regional & Continental Fanaticism
- **Latin America** delivers the highest average stadium turnout (**58,920 fans/show**), driven by monumental demand in Buenos Aires, Mexico City, and São Paulo.
- **Oceania** ranks second (**55,410 fans/show**), followed by **Europe** (**49,830 fans/show**) and **North America** (**45,120 fans/show**).

### 4. The Multi-Night Residency Stacking Multiplier
- Promoters previously feared market saturation when adding multiple shows in one market.
- Boxscore data confirms **0.00% cannibalization**: artists performing 4 to 10 consecutive stadium dates in mega-cities maintain **>99.5% sellout rates**, multiplying single-city attendance to 400,000–620,000 fans.

### 5. Calendar & Seasonality Dynamics
- Weekend dates (Friday–Sunday) capture **58% of tour dates** with **99.74% fill rates**.
- Midweek dates (Tuesday/Wednesday) maintain **99.41% fill rates** due to multi-night residency runs.
- **Summer** captures **44% of global tickets sold**, driven by the Northern Hemisphere open-air stadium window.

---

## 💻 Tech Stack & Architecture

- **Data Processing**: Python 3.14, Pandas, NumPy, BeautifulSoup4, Requests
- **Machine Learning**: Scikit-Learn (Random Forest Regressor, Gradient Boosting)
- **Static Visualizations**: Matplotlib, Seaborn (Custom Dark Theme, 200 DPI)
- **Web Frontend**: HTML5, Vanilla CSS3 (Custom Dark Design System), ES6+ JavaScript
- **Interactive Visualizations**: Chart.js (v4), Leaflet.js (v1.9) with CartoDB Dark Matter tiles

---

## 🚀 How to Run

### Method 1: Local HTTP Server (Recommended)
Run the built-in Python web server script from the project root:
```bash
python run_website.py
```
This automatically launches your default web browser at `http://localhost:8000`.

### Method 2: Direct File Open (Serverless)
Double-click `website/index.html` in your file explorer to open it directly in Chrome, Edge, Safari, or Firefox. The dashboard includes a precompiled `js/data_bundle.js` script so all interactive charts, maps, and tables function offline without CORS restrictions.

---

## 📁 Repository Structure

```
NoSql Project/
├── data/
│   ├── raw/
│   │   ├── eras_tour_kaggle.csv          # Kaggle: Taylor Swift Eras Tour
│   │   ├── taylor_swift_kaggle.csv       # Kaggle: 5 historical TS world tours
│   │   ├── ed_sheeran_kaggle.csv         # Kaggle: Ed Sheeran Mathematics Tour
│   │   ├── oasis_live_25_kaggle.csv      # Kaggle: Oasis Live '25 Stadium Tour
│   │   └── wikipedia_world_tours.csv     # Billboard/Pollstar world tour boxscores
│   ├── cleaned_concert_turnout.csv       # Unified cleaned dataset (1,829 rows)
│   └── cleaned_concert_turnout.json      # Structured JSON export
├── scripts/
│   ├── fetch_and_build_dataset.py        # Data ingestion & scraper pipeline
│   ├── clean_data.py                     # Data wrangling & harmonization pipeline
│   └── analysis.py                       # Statistical modeling & chart generation
├── website/
│   ├── index.html                        # Minimal dark theme website
│   ├── css/
│   │   └── style.css                     # Custom dark design system
│   ├── js/
│   │   ├── app.js                        # App controller, table, pagination, export
│   │   ├── charts.js                     # Chart.js interactive factor visualizers
│   │   ├── map.js                        # Leaflet interactive geospatial map
│   │   ├── simulator.js                  # What-If turnout & gross calculator
│   │   └── data_bundle.js                # Browser data bundle
│   ├── data/
│   │   ├── cleaned_concert_turnout.json  # Web data source
│   │   └── analysis_summary.json         # Precomputed model metrics & summaries
│   └── assets/
│       └── charts/                       # 8 High-resolution Matplotlib charts
│           ├── chart1_capacity_vs_turnout.png
│           ├── chart2_price_elasticity.png
│           ├── chart3_continental_turnout.png
│           ├── chart4_day_of_week_seasonality.png
│           ├── chart5_multinight_residency.png
│           ├── chart6_genre_artist_comparison.png
│           ├── chart7_ml_feature_importance.png
│           └── chart8_timeline_evolution.png
├── run_website.py                        # One-click local webserver runner
└── README.md                             # Project documentation
```

---

## 📜 Dataset Citations

- **Taylor Swift Eras Tour**: Kaggle (`tymonbot/taylor-swift-eras-toure`)
- **Taylor Swift World Tours**: Kaggle (`gayu14/taylor-concert-tours-impact-on-attendance-and`)
- **Ed Sheeran Tour Boxscore**: Kaggle (`jessalynlim/ed-sheeran-tour`)
- **Oasis Live '25**: Kaggle (`rodolfobrandao95/oasis-live-25`)
- **Billboard Boxscore & Pollstar**: Tour archives for Coldplay, Beyoncé, Harry Styles, The Weeknd, U2, Elton John.
