import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned_concert_turnout.csv")
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "..", "website", "assets", "charts")
SUMMARY_JSON_FILE = os.path.join(os.path.dirname(__file__), "..", "website", "data", "analysis_summary.json")

os.makedirs(CHARTS_DIR, exist_ok=True)

# Dark theme palette
DARK_BG = "#0B0F19"
PANEL_BG = "#111827"
TEXT_COLOR = "#F3F4F6"
MUTED_COLOR = "#9CA3AF"
GRID_COLOR = "#1F2937"
ACCENT_PRIMARY = "#6366F1"    # Indigo
ACCENT_SECONDARY = "#10B981"  # Emerald
ACCENT_TERTIARY = "#F59E0B"   # Amber
ACCENT_PINK = "#EC4899"       # Pink
ACCENT_CYAN = "#06B6D4"       # Cyan
ACCENT_VIOLET = "#8B5CF6"     # Violet

def apply_dark_theme(fig, ax):
    fig.patch.set_facecolor(DARK_BG)
    if isinstance(ax, np.ndarray):
        for a in ax.flat:
            a.set_facecolor(PANEL_BG)
            a.tick_params(colors=MUTED_COLOR, labelsize=10)
            a.xaxis.label.set_color(TEXT_COLOR)
            a.yaxis.label.set_color(TEXT_COLOR)
            a.title.set_color(TEXT_COLOR)
            for spine in a.spines.values():
                spine.set_color(GRID_COLOR)
            a.grid(True, linestyle="--", alpha=0.3, color=GRID_COLOR)
    else:
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=MUTED_COLOR, labelsize=10)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)
        ax.grid(True, linestyle="--", alpha=0.3, color=GRID_COLOR)

def run_analysis():
    print("Loading cleaned dataset for exploratory and predictive analysis...")
    df = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(df)} records across {len(df.columns)} features.")

    # -------------------------------------------------------------
    # 1. CORE DESCRIPTIVE & FACTOR STATISTICS
    # -------------------------------------------------------------
    summary_data = {
        "global_metrics": {
            "total_concerts": int(len(df)),
            "total_attendance": int(df['attendance'].sum()),
            "total_gross_usd": float(round(df['gross_usd'].sum(), 2)),
            "avg_attendance_per_show": float(round(df['attendance'].mean(), 1)),
            "median_attendance": float(round(df['attendance'].median(), 1)),
            "avg_occupancy_rate": float(round(df['occupancy_rate'].mean(), 2)),
            "sellout_percentage": float(round((df['is_sellout'].sum() / len(df)) * 100, 2)),
            "avg_ticket_price": float(round(df['avg_ticket_price'].mean(), 2)),
            "total_artists": int(df['artist'].nunique()),
            "total_continents": int(df['continent'].nunique()),
            "total_countries": int(df['country'].nunique()),
            "total_cities": int(df['city'].nunique())
        }
    }

    # Factor 1: Venue Type Distribution
    venue_stats = df.groupby('venue_type').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        median_attendance=('attendance', 'median'),
        mean_capacity=('capacity', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean'),
        total_gross=('gross_usd', 'sum'),
        mean_ticket_price=('avg_ticket_price', 'mean')
    ).round(2).reset_index().to_dict(orient='records')
    summary_data['venue_analysis'] = venue_stats

    # Factor 2: Ticket Price Elasticity & Tiers
    price_stats = df.groupby('price_tier').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean'),
        total_attendance=('attendance', 'sum'),
        total_gross=('gross_usd', 'sum'),
        mean_price=('avg_ticket_price', 'mean')
    ).round(2).reset_index().to_dict(orient='records')
    summary_data['price_tier_analysis'] = price_stats

    # Factor 3: Geographic & Continental Disparities
    continent_stats = df.groupby('continent').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        total_attendance=('attendance', 'sum'),
        mean_occupancy=('occupancy_rate', 'mean'),
        total_gross=('gross_usd', 'sum'),
        mean_ticket_price=('avg_ticket_price', 'mean')
    ).round(2).reset_index().sort_values(by='mean_attendance', ascending=False).to_dict(orient='records')
    summary_data['continent_analysis'] = continent_stats

    # Market Tier Disparities
    market_stats = df.groupby('market_tier').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        total_attendance=('attendance', 'sum'),
        mean_occupancy=('occupancy_rate', 'mean'),
        mean_ticket_price=('avg_ticket_price', 'mean')
    ).round(2).reset_index().sort_values('mean_occupancy', ascending=False).to_dict(orient='records')
    summary_data['market_tier_analysis'] = market_stats

    # Factor 4: Residency Density / Multi-Night Effect
    df['residency_category'] = pd.cut(
        df['shows_in_city'],
        bins=[0, 1, 2, 4, 15],
        labels=['Single Show (1)', 'Double Date (2)', 'Multi-Night Run (3-4)', 'Mega-Residency (5+)']
    )
    residency_stats = df.groupby('residency_category', observed=False).agg(
        shows=('attendance', 'count'),
        mean_per_show_attendance=('attendance', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean'),
        mean_ticket_price=('avg_ticket_price', 'mean')
    ).round(2).reset_index().to_dict(orient='records')
    summary_data['residency_analysis'] = residency_stats

    # Factor 5: Temporal & Day of Week
    day_stats = df.groupby('day_of_week').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean')
    ).round(2).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index().to_dict(orient='records')
    summary_data['day_of_week_analysis'] = day_stats

    season_stats = df.groupby('season').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        total_attendance=('attendance', 'sum')
    ).round(2).reset_index().to_dict(orient='records')
    summary_data['season_analysis'] = season_stats

    # Timeline Evolution
    year_stats = df.groupby('year').agg(
        shows=('attendance', 'count'),
        total_attendance=('attendance', 'sum'),
        mean_attendance=('attendance', 'mean'),
        total_gross=('gross_usd', 'sum'),
        avg_price=('avg_ticket_price', 'mean')
    ).round(2).reset_index().sort_values(by='year').to_dict(orient='records')
    summary_data['timeline_analysis'] = year_stats

    # Factor 6: Genre & Artist Draw
    genre_stats = df.groupby('genre').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        total_attendance=('attendance', 'sum'),
        mean_ticket_price=('avg_ticket_price', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean')
    ).round(2).reset_index().sort_values(by='mean_attendance', ascending=False).to_dict(orient='records')
    summary_data['genre_analysis'] = genre_stats

    artist_stats = df.groupby('artist').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        total_attendance=('attendance', 'sum'),
        total_gross=('gross_usd', 'sum'),
        mean_price=('avg_ticket_price', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean')
    ).round(2).reset_index().sort_values(by='total_attendance', ascending=False).to_dict(orient='records')
    summary_data['artist_analysis'] = artist_stats

    # Artist Tier Analysis (most important causal factor for occupancy)
    artist_tier_order = ['Emerging Artist', 'Mid-Tier Touring Artist', 'Major Touring Artist', 'Stadium Headliner', 'Legendary Reunion', 'Global Mega-Superstar']
    artist_tier_stats = df.groupby('artist_tier').agg(
        shows=('attendance', 'count'),
        mean_attendance=('attendance', 'mean'),
        mean_occupancy=('occupancy_rate', 'mean'),
        mean_capacity=('capacity', 'mean'),
        mean_ticket_price=('avg_ticket_price', 'mean'),
        total_gross=('gross_usd', 'sum')
    ).round(2).reset_index()
    tier_sort = {t: i for i, t in enumerate(artist_tier_order)}
    artist_tier_stats['_sort'] = artist_tier_stats['artist_tier'].map(tier_sort).fillna(99)
    artist_tier_stats = artist_tier_stats.sort_values('_sort').drop(columns='_sort')
    summary_data['artist_tier_analysis'] = artist_tier_stats.to_dict(orient='records')

    # -------------------------------------------------------------
    # 2. MACHINE LEARNING MODELING FOR VENUE OCCUPANCY & FILL RATE
    # (Predicting occupancy_rate to eliminate capacity target leakage)
    # -------------------------------------------------------------
    print("Training Machine Learning models to quantify factor influence on fill rate...")
    
    # Feature matrix preparation (excluding capacity to eliminate target leakage)
    feature_cols = [
        'avg_ticket_price', 'opening_acts_count', 'shows_in_city',
        'is_weekend', 'year', 'month'
    ]
    categorical_cols = ['artist_tier', 'market_tier', 'genre', 'venue_type', 'continent', 'season']
    
    df_encoded = pd.get_dummies(df[feature_cols + categorical_cols], drop_first=True)
    X = df_encoded
    y = df['occupancy_rate']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_model = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

    print(f"Model Performance (Occupancy Rate) -> R2: {r2:.4f}, RMSE: {rmse:.2f}%, MAE: {mae:.2f}%, MAPE: {mape:.2f}%")

    # Feature Importance
    importances = rf_model.feature_importances_
    feat_names = X.columns
    feat_imp_df = pd.DataFrame({'feature': feat_names, 'importance': importances}).sort_values(by='importance', ascending=False)
    
    # Group dummy variable importances back to high-level parent factors
    factor_importance_grouped = {
        "Venue Scale & Configuration": float(feat_imp_df[feat_imp_df['feature'].str.startswith('venue_type')]['importance'].sum()),
        "Artist Fame & Star Power (Tier)": float(feat_imp_df[feat_imp_df['feature'].str.startswith('artist_tier')]['importance'].sum()),
        "Musical Genre & Appeal": float(feat_imp_df[feat_imp_df['feature'].str.startswith('genre')]['importance'].sum()),
        "Day of Week & Calendar (Weekend/Month)": float(feat_imp_df[feat_imp_df['feature'].isin(['is_weekend', 'month']) | feat_imp_df['feature'].str.startswith('season')]['importance'].sum()),
        "Ticket Price & Economics": float(feat_imp_df[feat_imp_df['feature'] == 'avg_ticket_price']['importance'].sum()),
        "City Market Tier & Demand Depth": float(feat_imp_df[feat_imp_df['feature'].str.startswith('market_tier')]['importance'].sum()),
        "Macroeconomic Era / Tour Year": float(feat_imp_df[feat_imp_df['feature'] == 'year']['importance'].sum()),
        "Supporting Acts & Tour Lineup": float(feat_imp_df[feat_imp_df['feature'] == 'opening_acts_count']['importance'].sum()),
        "Geographic Region (Continent)": float(feat_imp_df[feat_imp_df['feature'].str.startswith('continent')]['importance'].sum()),
        "Residency Stacking (Shows in City)": float(feat_imp_df[feat_imp_df['feature'] == 'shows_in_city']['importance'].sum()),
    }
    
    # Normalize to 100%
    total_grouped = sum(factor_importance_grouped.values())
    factor_importance_pct = {k: round((v / total_grouped) * 100, 2) for k, v in factor_importance_grouped.items()}

    summary_data['ml_model'] = {
        "algorithm": "Random Forest Regressor (150 Trees)",
        "r2_score": round(r2, 4),
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "mape_percent": round(mape, 2),
        "factor_importance": factor_importance_pct,
        "top_features": feat_imp_df.head(10).to_dict(orient='records')
    }

    # Save summary JSON
    with open(SUMMARY_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved analysis summary to {SUMMARY_JSON_FILE}")

    # -------------------------------------------------------------
    # 3. HIGH-RESOLUTION MATPLOTLIB VISUALIZATIONS
    # -------------------------------------------------------------
    print("Generating high-resolution dark-themed visualization charts...")

    # --- CHART 1: Venue Capacity vs Actual Turnout ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax)
    
    for vt, col in [('Stadium', ACCENT_PRIMARY), ('Arena', ACCENT_SECONDARY), ('Amphitheater / Park', ACCENT_TERTIARY)]:
        subset = df[df['venue_type'] == vt]
        ax.scatter(subset['capacity'] / 1000, subset['attendance'] / 1000, label=vt, alpha=0.65, edgecolors='none', s=45, color=col)
    
    # 1:1 reference line (sellout)
    lims = [0, 115]
    ax.plot(lims, lims, '--', color=MUTED_COLOR, alpha=0.6, label='100% Sellout Benchmark')
    
    ax.set_title("Venue Capacity vs Actual Audience Turnout", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Physical Capacity (Thousands of Seats)", fontsize=11, labelpad=10)
    ax.set_ylabel("Audience Turnout (Thousands of Attendees)", fontsize=11, labelpad=10)
    ax.legend(frameon=True, facecolor=PANEL_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart1_capacity_vs_turnout.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 2: Average Ticket Price vs Turnout & Gross ---
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax1)
    ax2 = ax1.twinx()
    ax2.set_facecolor(PANEL_BG)
    ax2.tick_params(colors=MUTED_COLOR, labelsize=10)
    ax2.yaxis.label.set_color(TEXT_COLOR)
    for spine in ax2.spines.values():
        spine.set_color(GRID_COLOR)

    tier_order = ['Budget (<$75)', 'Standard ($75-$150)', 'Premium ($150-$250)', 'VIP / Luxury (>$250)']
    pt_df = df.groupby('price_tier').agg({'attendance': 'mean', 'gross_usd': 'mean'}).reindex(tier_order).reset_index()

    x = np.arange(len(tier_order))
    width = 0.35

    bars1 = ax1.bar(x - width/2, pt_df['attendance'] / 1000, width, label='Avg Turnout (k)', color=ACCENT_PRIMARY, alpha=0.85)
    bars2 = ax2.bar(x + width/2, pt_df['gross_usd'] / 1e6, width, label='Avg Gross ($M)', color=ACCENT_SECONDARY, alpha=0.85)

    ax1.set_title("Ticket Price Tier Dynamics: Turnout Stability vs Revenue Surge", fontsize=14, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(tier_order, rotation=10, ha='right')
    ax1.set_ylabel("Average Turnout per Show (Thousands)", fontsize=11)
    ax2.set_ylabel("Average Gross per Show ($ Millions USD)", fontsize=11)
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor=PANEL_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart2_price_elasticity.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 3: Artist Tier vs Occupancy Rate ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax)
    at_df = artist_tier_stats.copy()
    tier_colors = [ACCENT_CYAN, ACCENT_VIOLET, ACCENT_TERTIARY, ACCENT_SECONDARY, ACCENT_PINK, ACCENT_PRIMARY]
    bars = ax.bar(at_df['artist_tier'], at_df['mean_occupancy'],
                  color=tier_colors[:len(at_df)], alpha=0.88, width=0.6)
    ax.set_title("Artist Fame Tier vs Average Venue Occupancy Rate", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Artist Career Tier", fontsize=11, labelpad=10)
    ax.set_ylabel("Average Occupancy Rate (%)", fontsize=11, labelpad=10)
    ax.set_ylim(0, 110)
    ax.tick_params(axis='x', rotation=18)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1.5,
                f"{h:.1f}%", ha='center', va='bottom', color=TEXT_COLOR, fontweight='bold', fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart3_artist_tier.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 4: Day of Week & Seasonality Dynamics ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    apply_dark_theme(fig, ax1)
    apply_dark_theme(fig, ax2)

    # Day of week
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_df = df.groupby('day_of_week').agg({'attendance': 'mean', 'concert_id': 'count'}).reindex(dow_order)
    
    colors_dow = [ACCENT_PRIMARY if d in ['Friday', 'Saturday', 'Sunday'] else ACCENT_VIOLET for d in dow_order]
    ax1.bar(dow_df.index, dow_df['attendance'] / 1000, color=colors_dow, alpha=0.85)
    ax1.set_title("Average Turnout by Day of Week", fontsize=12, fontweight='bold', pad=12)
    ax1.set_ylabel("Turnout (Thousands)", fontsize=10)
    ax1.tick_params(axis='x', rotation=35)

    # Seasonality
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    season_df = df.groupby('season').agg({'attendance': 'sum', 'concert_id': 'count'}).reindex(season_order)
    ax2.bar(season_df.index, season_df['attendance'] / 1e6, color=ACCENT_TERTIARY, alpha=0.85)
    ax2.set_title("Total Global Tickets Sold by Season", fontsize=12, fontweight='bold', pad=12)
    ax2.set_ylabel("Total Attendance (Millions)", fontsize=10)

    fig.suptitle("Temporal Influences: Weekend Clustering & Summer Stadium Domination", fontsize=14, fontweight='bold', y=1.02, color=TEXT_COLOR)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart4_day_of_week_seasonality.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 5: Market Tier Disparity ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax)
    mkt_plot = df.groupby('market_tier').agg(
        mean_occupancy=('occupancy_rate', 'mean'),
        mean_attendance=('attendance', 'mean'),
        shows=('attendance', 'count')
    ).round(2).reset_index().sort_values('mean_occupancy', ascending=True)

    bars = ax.barh(mkt_plot['market_tier'], mkt_plot['mean_occupancy'], color=ACCENT_SECONDARY, alpha=0.88, height=0.5)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.8, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', ha='left', color=TEXT_COLOR, fontweight='bold', fontsize=10)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Average Venue Occupancy Rate (%)", fontsize=11, labelpad=10)
    ax.set_title("City Market Tier vs Average Venue Fill Rate", fontsize=13, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart5_market_tier.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 6: Genre Comparison ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax)

    genre_df = df.groupby('genre').agg({'attendance': 'mean'}).sort_values(by='attendance', ascending=True)
    bars = ax.barh(genre_df.index, genre_df['attendance'] / 1000, color=ACCENT_SECONDARY, alpha=0.85, height=0.55)
    ax.set_title("Average Stadium/Arena Turnout by Musical Genre", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Average Turnout (Thousands of Fans)", fontsize=11, labelpad=10)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height()/2, f"{w:.1f}k", va='center', ha='left', color=TEXT_COLOR, fontweight='bold', fontsize=10)

    ax.set_xlim(0, max(genre_df['attendance'] / 1000) * 1.15)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart6_genre_artist_comparison.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 7: Machine Learning Factor Importance ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax)

    factors_sorted = sorted(factor_importance_pct.items(), key=lambda x: x[1], reverse=True)
    names = [f[0] for f in reversed(factors_sorted)]
    vals = [f[1] for f in reversed(factors_sorted)]

    bars = ax.barh(names, vals, color=ACCENT_PRIMARY, alpha=0.88, height=0.55)
    ax.set_title("Machine Learning Factor Importance on Venue Fill Rate (Random Forest)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Relative Predictive Importance (%) — Free of Capacity Target Leakage", fontsize=10, labelpad=10)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.8, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', ha='left', color=TEXT_COLOR, fontweight='bold', fontsize=10)

    ax.set_xlim(0, max(vals) * 1.15)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart7_ml_feature_importance.png"), facecolor=DARK_BG)
    plt.close(fig)

    # --- CHART 8: Timeline Evolution (2009-2025) ---
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=200)
    apply_dark_theme(fig, ax1)
    ax2 = ax1.twinx()
    ax2.set_facecolor(PANEL_BG)
    ax2.tick_params(colors=MUTED_COLOR, labelsize=10)
    ax2.yaxis.label.set_color(TEXT_COLOR)
    for spine in ax2.spines.values():
        spine.set_color(GRID_COLOR)

    yr_df = df.groupby('year').agg({'attendance': ['sum', 'mean']}).reset_index()
    yr_df.columns = ['year', 'total_att', 'mean_att']
    yr_df = yr_df[yr_df['year'] >= 2009]

    ax1.bar(yr_df['year'], yr_df['total_att'] / 1e6, color=ACCENT_PRIMARY, alpha=0.5, label='Total Attendance (M)')
    ax2.plot(yr_df['year'], yr_df['mean_att'] / 1000, color=ACCENT_TERTIARY, marker='s', linewidth=2.5, label='Avg Turnout per Show (k)')

    ax1.set_title("The Live Music Super-Cycle: Turnout Explosion Post-2020", fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel("Tour Year", fontsize=11, labelpad=10)
    ax1.set_ylabel("Total Global Tickets (Millions)", fontsize=11)
    ax2.set_ylabel("Average Turnout per Show (Thousands)", fontsize=11)

    l1, b1 = ax1.get_legend_handles_labels()
    l2, b2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, b1 + b2, loc='upper left', frameon=True, facecolor=PANEL_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)

    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "chart8_timeline_evolution.png"), facecolor=DARK_BG)
    plt.close(fig)

    print("All 8 analytical charts generated successfully.")

if __name__ == "__main__":
    run_analysis()
