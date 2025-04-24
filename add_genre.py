import pandas as pd
import mysql.connector
from fuzzywuzzy import process, fuzz
import warnings
import re
warnings.filterwarnings("ignore")

def load_imdb_data(imdb_file):
    print("Loading IMDb data...")
    dtypes = {
        'tconst': str,
        'titleType': str,
        'primaryTitle': str,
        'originalTitle': str,
        'isAdult': str,
        'startYear': str,
        'endYear': str,
        'runtimeMinutes': str,
        'genres': str
    }
    imdb_df = pd.read_csv(imdb_file, sep='\t', dtype=dtypes, low_memory=False)
    imdb_df['startYear'] = pd.to_numeric(imdb_df['startYear'], errors='coerce')
    imdb_df = imdb_df[(imdb_df['titleType'] == 'movie') & 
                      (imdb_df['startYear'].notna()) &
                      (imdb_df['startYear'].between(2015, 2023))]
    imdb_df = imdb_df.replace('\\N', pd.NA)
    imdb_df['runtimeMinutes'] = pd.to_numeric(imdb_df['runtimeMinutes'], errors='coerce')
    imdb_df['isAdult'] = pd.to_numeric(imdb_df['isAdult'], errors='coerce').fillna(0).astype(int)
    imdb_df = imdb_df[['primaryTitle', 'startYear', 'genres', 'runtimeMinutes', 'isAdult']]
    imdb_df = imdb_df.dropna(subset=['primaryTitle', 'startYear'])
    imdb_df['title_lower'] = imdb_df['primaryTitle'].str.lower()
    print(f"IMDb movies loaded: {len(imdb_df)}")
    return imdb_df

def merge_imdb_features(movies_df, imdb_df):
    print("Merging IMDb features...")
    movies_df['title_lower'] = movies_df['title'].str.lower()
    movies_df['genre'] = None
    movies_df['runtime_minutes'] = None
    movies_df['is_adult'] = 0
    match_count = 0
    matched_titles = []
    unmatched_titles = []

    # Group IMDb by year for faster lookup
    imdb_groups = imdb_df.groupby('startYear')

    for idx, movie in movies_df.iterrows():
        title = movie['title_lower']
        year = movie['release_year']
        # Get candidates for year ±1
        candidate_years = [y for y in [year-1, year, year+1] if y in imdb_groups.groups]
        candidates = pd.concat([imdb_groups.get_group(y) for y in candidate_years])
        
        if not candidates.empty:
            # Use fuzzywuzzy.process to score top match
            choices = candidates['title_lower'].tolist()
            result = process.extractOne(title, choices, scorer=fuzz.token_sort_ratio)
            if result and result[1] > 75:  # Lowered threshold
                best_title, score = result
                match = candidates[candidates['title_lower'] == best_title].iloc[0]
                # Prefer exact year match if score is close
                exact_year_matches = candidates[candidates['startYear'] == year]
                if not exact_year_matches.empty:
                    exact_result = process.extractOne(title, exact_year_matches['title_lower'].tolist(), scorer=fuzz.token_sort_ratio)
                    if exact_result and exact_result[1] >= result[1] - 5:  # Within 5 points
                        best_title, score = exact_result
                        match = exact_year_matches[exact_year_matches['title_lower'] == best_title].iloc[0]
                movies_df.loc[idx, 'genre'] = match['genres'].split(',')[0] if pd.notna(match['genres']) else 'Unknown'
                movies_df.loc[idx, 'runtime_minutes'] = match['runtimeMinutes']
                movies_df.loc[idx, 'is_adult'] = match['isAdult']
                match_count += 1
                matched_titles.append((title, best_title, score, match['startYear']))
            else:
                unmatched_titles.append((title, year))
        else:
            unmatched_titles.append((title, year))

    print(f"Matched {match_count} movies with IMDb features")
    print(f"Matched titles (sample): {matched_titles[:5]}")
    print(f"Unmatched titles (sample): {unmatched_titles[:5]}")
    movies_df = movies_df.drop(columns=['title_lower'])
    movies_df['genre'] = movies_df['genre'].fillna('Unknown')
    movies_df['runtime_minutes'] = movies_df['runtime_minutes'].astype('Int64')
    movies_df['is_adult'] = movies_df['is_adult'].astype(int)
    return movies_df

def update_mysql(movies_df):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Unknown@0",
            database="movie_scraper"
        )
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM movies LIKE 'genre';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE movies ADD genre VARCHAR(50) DEFAULT 'Unknown' AFTER release_year;")
        cursor.execute("SHOW COLUMNS FROM movies LIKE 'runtime_minutes';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE movies ADD runtime_minutes INT NULL AFTER genre;")
        cursor.execute("SHOW COLUMNS FROM movies LIKE 'is_adult';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE movies ADD is_adult TINYINT DEFAULT 0 AFTER runtime_minutes;")
        
        update_query = """
        UPDATE movies
        SET genre = %s, runtime_minutes = %s, is_adult = %s
        WHERE title = %s AND release_year = %s
        """
        for _, row in movies_df.iterrows():
            cursor.execute(update_query, (
                row['genre'],
                row['runtime_minutes'] if pd.notna(row['runtime_minutes']) else None,
                row['is_adult'],
                row['title'],
                row['release_year']
            ))
        
        conn.commit()
        print(f"Updated {len(movies_df)} records in MySQL")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    print("Loading movies...")
    try:
        movies_df = pd.read_csv('data/movies_dedup.csv')
    except FileNotFoundError:
        print("movies_dedup.csv not found in D:\\scrape&bi\\data.")
        return
    print(f"Movies loaded: {len(movies_df)}")
    
    imdb_file = 'data/title.basics.tsv'
    imdb_df = load_imdb_data(imdb_file)
    
    movies_df = merge_imdb_features(movies_df, imdb_df)
    
    print("Saving to CSV...")
    movies_df.to_csv('data/movies_dedup.csv', index=False)
    print("Data saved to data/movies_dedup.csv")
    print(movies_df[['title', 'release_year', 'genre', 'runtime_minutes', 'is_adult']].head())
    
    print("Updating MySQL...")
    update_mysql(movies_df)
    print("Done.")

if __name__ == "__main__":
    main()