import requests
import json
import re
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from datetime import datetime

class UGCFilmsParser:
    """
    A class to parse UGC films HTML content into structured JSON data
    """
    
    def __init__(self):
        self.base_url = "https://www.ugc.fr"
        self.films_url = "https://www.ugc.fr/films.html"
        self.api_endpoint = "https://www.ugc.fr/filmsAjaxAction!getFilmsAndFilters.action"
        
        # Headers to mimic a real browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_and_parse_films(self, page: int = 30010, cinema_id: str = "", reset: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch films data from UGC API endpoint and parse it into structured JSON
        
        Args:
            page (int): Page number (default: 30010)
            cinema_id (str): Cinema ID filter
            reset (bool): Reset parameter
            
        Returns:
            Dict containing structured film data or None if request fails
        """
        try:
            # Prepare parameters for the API request
            params = {
                'filter': '',
                'page': page,
                'cinemaId': cinema_id,
                'reset': str(reset).lower(),
                '': ''  # Empty parameter as seen in the URL
            }
            
            print(f"Fetching data from: {self.api_endpoint}")
            print(f"Parameters: {params}")
            
            # Make the request
            response = requests.get(
                self.api_endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            print(f"Response status code: {response.status_code}")
            print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
            
            # Parse the HTML content and extract structured data
            html_content = response.text
            structured_data = self.parse_html_to_json(html_content)
            
            return structured_data
                
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def parse_html_to_json(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract structured film data
        
        Args:
            html_content: Raw HTML content from the API
            
        Returns:
            Structured dictionary with film data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize the result structure
        result = {
            'sections': {},
            'total_films': 0,
            'metadata': {
                'source': 'UGC Films API',
                'parsed_at': datetime.now().isoformat(),
                'parser_version': '1.0'
            }
        }
        
        # Find all film sections
        sections = soup.find_all('div', class_='sub-nav-section')
        
        for section in sections:
            section_id = section.get('id', 'unknown')
            section_title = self.extract_section_title(section)
            
            # Extract films from this section
            films = self.extract_films_from_section(section)
            
            result['sections'][section_id] = {
                'title': section_title,
                'films': films,
                'film_count': len(films)
            }
            
            result['total_films'] += len(films)
        
        return result
    
    def extract_section_title(self, section) -> str:
        """Extract the title of a film section"""
        title_elem = section.find('h2', class_='title--medium-caps')
        if title_elem:
            return title_elem.get_text(strip=True)
        return "Unknown Section"
    
    def extract_films_from_section(self, section) -> List[Dict[str, Any]]:
        """Extract film information from a section"""
        films = []
        
        # Find all film tiles
        film_tiles = section.find_all('div', class_='component--film-tile')
        
        for tile in film_tiles:
            film_data = self.extract_film_data(tile)
            if film_data:
                films.append(film_data)
        
        return films
    
    def extract_film_data(self, tile) -> Optional[Dict[str, Any]]:
        """Extract individual film data from a tile"""
        try:
            # Extract film title
            title_elem = tile.find('a', class_='color--dark-blue')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            
            # Extract film URL
            film_url = title_elem.get('href') if title_elem else None
            
            # Extract film ID from URL or data attributes
            film_id = None
            if film_url:
                # Try to extract ID from URL like "film_dracula_17055.html"
                match = re.search(r'film_.*?_(\d+)\.html', film_url)
                if match:
                    film_id = match.group(1)
            
            # Extract film kind/genre
            film_kind = title_elem.get('data-film-kind') if title_elem else None
            
            # Extract film label
            film_label = title_elem.get('data-film-label') if title_elem else None
            
            # Extract poster image
            img_elem = tile.find('img', class_='lozad')
            poster_url = img_elem.get('data-src') if img_elem else None
            
            # Extract age restriction
            restriction_img = tile.find('img', alt='interdiction')
            age_restriction = None
            if restriction_img:
                src = restriction_img.get('src', '')
                # Extract age from URL like "picto-noir-12.png"
                age_match = re.search(r'picto-noir-(\d+)\.png', src)
                if age_match:
                    age_restriction = f"{age_match.group(1)}+"
            
            # Extract UGC label/tag
            label_elem = tile.find('span', class_='film-tag')
            ugc_label = label_elem.get_text(strip=True) if label_elem else None
            
            # Extract trailer availability
            trailer_elem = tile.find('a', class_='see-video')
            has_trailer = trailer_elem is not None
            
            return {
                'title': title,
                'film_id': film_id,
                'url': film_url,
                'genre': film_kind,
                'label': film_label,
                'poster_url': poster_url,
                'age_restriction': age_restriction,
                'ugc_label': ugc_label,
                'has_trailer': has_trailer
            }
            
        except Exception as e:
            print(f"Error extracting film data: {e}")
            return None
    
    def parse_existing_html_file(self, html_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse an existing HTML file that contains UGC films data
        
        Args:
            html_file_path: Path to the HTML file to parse
            
        Returns:
            Structured dictionary with film data or None if parsing fails
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return self.parse_html_to_json(html_content)
            
        except FileNotFoundError:
            print(f"HTML file not found: {html_file_path}")
            return None
        except Exception as e:
            print(f"Error parsing HTML file: {e}")
            return None
    
    def save_data_to_file(self, data: Any, filename: str) -> bool:
        """
        Save fetched data to a file
        
        Args:
            data: Data to save
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if isinstance(data, dict):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(data)
            
            print(f"Data saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving data to file: {e}")
            return False
    
    def count_movies(self, data: Dict[str, Any]) -> int:
        """
        Count the total number of movies in the parsed data
        
        Args:
            data: The parsed film data
            
        Returns:
            Total number of movies found
        """
        if not data:
            return 0
        
        total_movies = data.get('total_films', 0)
        print(f"Total movies found: {total_movies}")
        return total_movies


def main():
    """
    Main function to demonstrate the usage of UGCFilmsParser
    """
    print("=== UGC Films Parser ===")
    
    # Create parser instance
    parser = UGCFilmsParser()
    
    # Option 1: Fetch and parse from API
    print("\n1. Fetching and parsing films data from API...")
    films_data = parser.fetch_and_parse_films()
    
    if films_data:
        # Save the structured data
        parser.save_data_to_file(films_data, 'ugc_films_parsed.json')
        print("Films data saved to ugc_films_parsed.json")
        
        # Count movies
        parser.count_movies(films_data)
        
        # Option 2: Parse existing HTML file (if available)
        print("\n2. Checking for existing HTML file to parse...")
        existing_data = parser.parse_existing_html_file('ugc_films_data.html')
        if existing_data:
            parser.save_data_to_file(existing_data, 'ugc_films_from_html.json')
            print("Data from HTML file saved to ugc_films_from_html.json")
            parser.count_movies(existing_data)
        else:
            print("No existing HTML file found to parse")
    else:
        print("Failed to fetch and parse films data")
    
    print("\n=== Parsing completed ===")


if __name__ == "__main__":
    main() 