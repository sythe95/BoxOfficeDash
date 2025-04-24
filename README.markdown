# Box Office Dash

Interactive Power BI dashboard analyzing box office revenue (2015–2023) by genre, studio, and runtime.

## Overview

This project scrapes, cleans, and visualizes box office data for 5,137 movies, enriched with IMDb genres and runtimes. The Power BI dashboard features a Pie Chart (genres &lt;0.5% gross as "Others"), Bar Chart, Treemap, and more, with slicers for year and genre.

## Process

1. **Scrape Data**: `scraper.py` extracts box office data (`movies_raw.csv`) from web sources (2015–2023).
2. **Clean Data**: `final_cleaning.py` deduplicates and cleans data (`movies_dedup.csv`, `movies_cleaned.csv`, 5,137 rows).
3. **Enrich Data**: `add_genre.py` matches \~82% of movies with IMDb genres/runtimes (`title.basics.tsv`).
4. **Load to MySQL**: `loader.py` imports `movies_cleaned.csv` to `movie_scraper` database, fixing `rank` keyword issue.
5. **Visualize**: `dashboard.pbix` creates interactive Power BI visuals (Pie Chart, Bar Chart, Treemap, etc.).

## Files

- `data/`:
  - `movies_cleaned.csv`: Final dataset (5,137 rows).
  - `movies_dedup.csv`: Deduplicated data (\~6,189 rows).
  - `movies_raw.csv`: Raw scraped data.
- `add_genre.py`: Matches IMDb genres/runtimes.
- `dashboard.pbix`: Power BI dashboard.
- `final_cleaning.py`: Cleans and deduplicates data.
- `loader.py`: Imports to MySQL.
- `scraper.py`: Scrapes box office data.

**IMDb Data**: Download `title.basics.tsv` from IMDb Datasets.

## Setup

1. **Clone Repo**:

   ```bash
   git clone https://github.com/username/BoxOfficeDash.git
   cd BoxOfficeDash
   ```

2. **Virtualenv**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install numpy pandas mysql-connector-python fuzzywuzzy python-Levenshtein
   ```

3. **MySQL**:

   - Create `movie_scraper` database.
   - Run `loader.py`.

4. **Power BI**:

   - Open `dashboard.pbix`.
   - Connect to `data/movies_cleaned.csv` or MySQL (`movie_scraper`).

## Usage

- Filter dashboard by year/genre.
- Analyze trends: Action (\~25%), Adventure (\~20%), \~$15B–$25B total gross.
- Export PDF for portfolio (`username.github.io`).

## License

MIT License.

## Contact

- **GitHub**: username
- **Portfolio**: username.github.io