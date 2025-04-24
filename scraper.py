import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_box_office():
    movies = []
    base_url = "https://www.boxofficemojo.com/weekly/chart/?yr={}&wk={:02d}"
    
    for year in range(2015, 2024):
        for week in range(1, 53):
            url = base_url.format(year, week)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch year {year}, week {week}: {e}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='mojo-body-table')
            
            if not table:
                print(f"No table found for year {year}, week {week}")
                continue
            
            rows = table.find_all('tr')[1:]
            movie_count = 0
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 11:
                    continue
                
                try:
                    gross_text = cols[3].text.strip().replace('$', '').replace(',', '')
                    if not gross_text.replace('.', '').replace('-', '').isdigit():
                        continue
                    
                    movie = {
                        'rank': int(cols[0].text.strip() or 0),
                        'title': cols[2].text.strip(),
                        'gross': float(gross_text or 0),
                        'studio': cols[10].text.strip() or 'Unknown',
                        'week': week,
                        'release_year': year
                    }
                    movies.append(movie)
                    movie_count += 1
                except (ValueError, IndexError):
                    continue
            
            print(f"Scraped year {year}, week {week}: {movie_count} movies")
            time.sleep(2)  # Ethical scraping
    
    df = pd.DataFrame(movies)
    print(f"Raw movies scraped: {len(df)}")
    return df

def main():
    print("Starting scrape...")
    movies_data = scrape_box_office()
    
    if movies_data.empty:
        print("No data scraped. Check logs for errors.")
        return
    
    # Save to CSV
    print("Saving to CSV...")
    movies_data.to_csv('movies_raw.csv', index=False)
    print("Data saved to movies_raw.csv")
    print(movies_data.head())

if __name__ == "__main__":
    main()