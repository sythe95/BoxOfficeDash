import pandas as pd
import mysql.connector

def store_in_mysql(df):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Unknown@0",
            database="movie_scraper"
        )
        cursor = conn.cursor()
        
        # Drop table if exists
        cursor.execute("DROP TABLE IF EXISTS movies;")
        
        # Create table with movie_rank
        cursor.execute("""
        CREATE TABLE movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_rank INT,
            title VARCHAR(255) NOT NULL,
            gross DECIMAL(15,2),
            studio VARCHAR(100),
            week INT,
            release_year INT
        )
        """)
        
        # Insert data
        insert_query = """
        INSERT INTO movies (movie_rank, title, gross, studio, week, release_year)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for _, row in df.iterrows():
            cursor.execute(insert_query, (
                row['rank'],  # Map 'rank' from CSV
                row['title'],
                row['gross'],
                row['studio'],
                row['week'],
                row['release_year']
            ))
        
        conn.commit()
        print(f"Inserted {len(df)} records into MySQL")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    print("Loading data...")
    try:
        movies_data = pd.read_csv('movies_raw.csv')
    except FileNotFoundError:
        print("movies_raw.csv not found in D:\\scrape&bi.")
        return
    
    print(f"Raw movies loaded: {len(movies_data)}")
    
    # Deduplicate
    movies_dedup = movies_data.drop_duplicates(subset=['title', 'release_year'], keep='first')
    print(f"Unique movies after deduplication: {len(movies_dedup)}")
    
    # Save to CSV
    print("Saving to CSV...")
    movies_dedup.to_csv('movies_dedup.csv', index=False)
    print("Data saved to movies_dedup.csv")
    print(movies_dedup.head())
    
    # Store in MySQL
    print("Storing in MySQL...")
    store_in_mysql(movies_dedup)
    print("Done.")

if __name__ == "__main__":
    main()