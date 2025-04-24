import pandas as pd
import mysql.connector

# Load the data
df = pd.read_csv('data/movies_dedup.csv')

# Filter out rows with 'Unknown' genre or missing runtime_minutes
cleaned_df = df[(df['genre'] != 'Unknown') & (~df['runtime_minutes'].isna())]

# Save to a new CSV
cleaned_df.to_csv('data/movies_cleaned.csv', index=False)
print(f"Cleaned data saved. Rows remaining: {len(cleaned_df)}")

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Unknown@0',
    database='movie_scraper'
)
cursor = conn.cursor()

# Update MySQL

# Optional: truncate existing table (if you want a full replace)
cursor.execute("TRUNCATE TABLE movies")

# Insert cleaned data
for _, row in cleaned_df.iterrows():
    cursor.execute("""
        INSERT INTO movies (title, release_year, genre, runtime_minutes, is_adult)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        row['title'],
        int(row['release_year']),
        row['genre'],
        float(row['runtime_minutes']),
        int(row['is_adult'])
    ))

conn.commit()
cursor.close()
conn.close()

print("MySQL database updated with cleaned data.")