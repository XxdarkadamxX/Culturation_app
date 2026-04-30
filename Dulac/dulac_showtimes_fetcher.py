import requests
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import time
from dotenv import load_dotenv
from supabase import Client, create_client
import os


#test
class DulacShowtimesFetcher:
    """
    A class to fetch movie showtimes from Dulac Cinemas
    """
    
    def __init__(self):
        load_dotenv()
        self.base_url = "https://dulaccinemas.com"
        self.showtimes_endpoint = "https://dulaccinemas.com/portail/seances"
        self.supabase_table = os.getenv("DULAC_SUPABASE_TABLE")
        
        # Headers to mimic a real browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def flatten_showtimes_format(self, showtimes_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Flatten scraped showtimes into one record per movie/cinema/day for Supabase.
        """
        records: List[Dict[str, Any]] = []

        for date_str, date_data in showtimes_data.get("dates", {}).items():
            for cinema in date_data.get("cinemas", []):
                cinema_name = cinema.get("name", "Unknown")

                for film in cinema.get("films", []):
                    showtimes = film.get("showtimes", [])
                    records.append({
                        "movie": film.get("title", "Unknown"),
                        "cinema": cinema_name,
                        "showtime_day": date_str,
                        "nb_showings": film.get("showtime_count", len(showtimes)),
                        "showtimes": showtimes,
                    })

        return records

    def create_supabase_client(self) -> Client:
        """
        Create and return a Supabase client using environment variables.
        """
        load_dotenv()

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your environment.")

        return create_client(supabase_url, supabase_key)

    def save_showtimes(self, showtimes_data: Dict[str, Any]) -> int:
        """
        Write Dulac showtimes directly to Supabase database.

        Existing rows for the fetched dates are removed first to avoid duplicates.

        Returns:
            Number of records written
        """
        records = self.flatten_showtimes_format(showtimes_data)
        if not records:
            print("No Dulac showtime records to write to Supabase.")
            return 0

        supabase = self.create_supabase_client()

        supabase.table(self.supabase_table).delete().neq("movie", 0).execute()

        batch_size = 500
        inserted_count = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            supabase.table(self.supabase_table).insert(batch).execute()
            inserted_count += len(batch)

        print(f"Wrote {inserted_count} records to Supabase table '{self.supabase_table}'.")
        return inserted_count
    
    def get_showtimes_for_date(self, date_str: str) -> Dict[str, Any]:
        """
        Get showtimes for a specific date
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing showtimes data with cinema information
        """
        try:
            url = f"{self.showtimes_endpoint}/{date_str}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse the HTML to extract showtimes
            soup = BeautifulSoup(response.text, 'html.parser')
            
            showtimes_data = {
                'date': date_str,
                'cinemas': []
            }
            
            # Find cinema sections
            cinema_sections = soup.find_all('div', class_='wrapper-salle')
            
            if not cinema_sections:
                return showtimes_data
            
            for section in cinema_sections:
                # Find cinema name in the section
                cinema_name_elem = section.find('h2')
                if cinema_name_elem:
                    cinema_name = cinema_name_elem.get_text(strip=True)
                    cinema_id = cinema_name_elem.get('data-cinema-id', '')
                else:
                    cinema_name = "Unknown Cinema"
                    cinema_id = ""
                
                cinema_data = {
                    'name': cinema_name,
                    'cinema_id': cinema_id,
                    'films': []
                }
                
                # Find all film items in this cinema
                film_items = section.find_all('li', class_='film-item-affiche')
                
                for film_item in film_items:
                    # Extract film title
                    title_elem = film_item.find('div', class_='movie-title')
                    if title_elem:
                        film_title = title_elem.get_text(strip=True)
                    else:
                        continue  # Skip if no title found
                    
                    # Extract film details
                    film_kind_elem = film_item.find('span', class_='film-kind')
                    film_kind = film_kind_elem.get_text(strip=True) if film_kind_elem else ""
                    
                    film_duration_elem = film_item.find('span', class_='film-duration')
                    film_duration = film_duration_elem.get_text(strip=True) if film_duration_elem else ""
                    
                    # Extract showtimes
                    showtimes = []
                    horaires_list = film_item.find('ul', class_='list-horaires')
                    if horaires_list:
                        horaires_items = horaires_list.find_all('li', class_='item-horaire')
                        for item in horaires_items:
                            time_elem = item.find('div', class_='field-content field_seance_date')
                            if time_elem:
                                time_text = time_elem.get_text(strip=True)
                                # Extract time pattern (HH:MM)
                                time_match = re.search(r'(\d{2}:\d{2})', time_text)
                                if time_match:
                                    showtimes.append(time_match.group(1))
                    
                    film_data = {
                        'title': film_title,
                        'kind': film_kind,
                        'duration': film_duration,
                        'showtimes': showtimes,
                        'showtime_count': len(showtimes)
                    }
                    
                    cinema_data['films'].append(film_data)
                
                showtimes_data['cinemas'].append(cinema_data)
            
            return showtimes_data
            
        except Exception as e:
            print(f"Error getting showtimes for date {date_str}: {e}")
            return {
                'date': date_str,
                'cinemas': [],
                'error': str(e)
            }
    
    def fetch_showtimes_for_next_7_days(self) -> Dict[str, Any]:
        """
        Fetch showtimes for the next 7 days
        
        Returns:
            Dictionary containing all showtimes data
        """
        all_showtimes = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'source': 'Dulac Cinemas',
                'base_url': self.base_url,
                'date_range': 'Next 7 days from today'
            },
            'dates': {}
        }
        
        # Generate dates for next 7 days
        today = date.today()
        dates_to_fetch = []
        for i in range(7):
            target_date = today + timedelta(days=i)
            dates_to_fetch.append(target_date.strftime('%Y-%m-%d'))
        
        print(f"Fetching showtimes for the next 7 days: {', '.join(dates_to_fetch)}")
        
        for date_str in dates_to_fetch:
            print(f"Fetching showtimes for {date_str}...")
            
            showtimes_data = self.get_showtimes_for_date(date_str)
            all_showtimes['dates'][date_str] = showtimes_data
            
            # Add a delay to be respectful to the server
            time.sleep(1)
        
        return all_showtimes
    
    def print_showtimes_summary(self, showtimes_data: Dict[str, Any]) -> None:
        """
        Print a summary of the fetched showtimes
        
        Args:
            showtimes_data: The showtimes data
        """
        metadata = showtimes_data.get('metadata', {})
        dates = showtimes_data.get('dates', {})
        
        print(f"\n=== Dulac Cinemas Showtimes Summary ===")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Date range: {metadata.get('date_range', 'Unknown')}")
        print(f"Fetched at: {metadata.get('fetched_at', 'Unknown')}")
        
        total_cinemas = set()
        total_films = set()
        total_showtimes = 0
        
        for date_str, date_data in dates.items():
            cinemas = date_data.get('cinemas', [])
            print(f"\n{date_str}:")
            
            for cinema in cinemas:
                cinema_name = cinema.get('name', 'Unknown')
                total_cinemas.add(cinema_name)
                films = cinema.get('films', [])
                
                print(f"  {cinema_name}:")
                for film in films:
                    film_title = film.get('title', 'Unknown')
                    total_films.add(film_title)
                    showtime_count = film.get('showtime_count', 0)
                    total_showtimes += showtime_count
                    
                    print(f"    - {film_title}: {showtime_count} showtimes")
        
        print(f"\n=== Summary ===")
        print(f"Total unique cinemas: {len(total_cinemas)}")
        print(f"Total unique films: {len(total_films)}")
        print(f"Total showtimes: {total_showtimes}")
        print(f"Cinemas found: {', '.join(sorted(total_cinemas))}")


def main():
    """
    Main function to demonstrate the usage of DulacShowtimesFetcher
    """
    print("=== Dulac Cinemas Showtimes Fetcher ===")
    
    # Create fetcher instance
    fetcher = DulacShowtimesFetcher()
    
    # Fetch showtimes for next 7 days
    print("\n1. Fetching showtimes for the next 7 days...")
    showtimes_data = fetcher.fetch_showtimes_for_next_7_days()
    
    if showtimes_data['dates']:
        fetcher.save_showtimes(showtimes_data)
        fetcher.print_showtimes_summary(showtimes_data)
    else:
        print("No showtimes data found")
    
    print("\n=== Showtimes fetching completed ===")


if __name__ == "__main__":
    main() 
