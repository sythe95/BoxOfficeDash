# Box Office Dash

![Dashboard Screenshot](dashboard_screenshot.png)  
*Interactive Power BI dashboard visualizing box office revenue (2015–2023).*

## Overview

This project analyzes 5,137 movies (2015–2023) by scraping box office data from Box Office Mojo, enriching with IMDb genres, loading into MySQL, and visualizing in Power BI. The dashboard includes a Pie Chart (genres <0.5% gross as "Others"), Bar Chart, Treemap, and more, with slicers for year and genre.

## Workflow

```mermaid
graph TD
    A[Box Office Mojo] -->|scraper.py| B[movies_raw.csv]
    B -->|final_cleaning.py| C[movies_dedup.csv]
    C -->|final_cleaning.py| D[movies_cleaned.csv]
    E[IMDb title.basics.tsv] -->|add_genre.py| D
    D -->|loader.py| F[MySQL movie_scraper]
    F -->|dashboard.pbix| G[Power BI Dashboard]
```

1. **Scrape**: `scraper.py` extracts data from Box Office Mojo (`movies_raw.csv`).
2. **Clean**: `final_cleaning.py` deduplicates and cleans (`movies_dedup.csv`, `movies_cleaned.csv`).
3. **Enrich**: `add_genre.py` adds IMDb genres/runtimes (~82% match).
4. **Load**: `loader.py` imports to MySQL (`movie_scraper`).
5. **Visualize**: `dashboard.pbix` builds Power BI visuals.

## Files

- `data/`:
  - `movies_cleaned.csv`: Final dataset (5,137 rows).
  - `movies_dedup.csv`: Deduplicated (~6,189 rows).
  - `movies_raw.csv`: Raw data.
- `add_genre.py`: Matches IMDb genres.
- `dashboard.pbix`: Power BI dashboard.
- `final_cleaning.py`: Cleans data.
- `loader.py`: Imports to MySQL.
- `scraper.py`: Scrapes data.

**IMDb Data**: Download `title.basics.tsv` from [IMDb Datasets](https://datasets.imdbws.com/).

## Setup

1. **Clone**:
   ```bash
   git clone https://github.com/username/BoxOfficeDash.git
   cd BoxOfficeDash
   ```

2. **Virtualenv**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **MySQL**:
   - Create `movie_scraper` database.
   - Run `loader.py`.

4. **Power BI**:
   - Open `dashboard.pbix`.
   - Connect to `data/movies_cleaned.csv` or MySQL.
