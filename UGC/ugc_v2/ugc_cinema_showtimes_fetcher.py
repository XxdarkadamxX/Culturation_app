import json
import re
import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


class UGCCinemaShowtimesFetcher:
    """
    Fetch UGC showtimes by cinema page for Paris cinemas.
    """

    def __init__(self):
        self.base_url = "https://www.ugc.fr"
        self.showings_endpoint = (
            "https://www.ugc.fr/showingsCinemaAjaxAction!getShowingsForCinemaPage.action"
        )
        self.paris_cinemas = [
            {"cinema_id": "1", "name": "UGC Ciné Cité Châtelet Les Halles"},
            {"cinema_id": "2", "name": "UGC Ciné Cité Bercy"},
            {"cinema_id": "5", "name": "UGC Gobelins"},
            {"cinema_id": "6", "name": "UGC Opéra"},
            {"cinema_id": "4", "name": "UGC Danton"},
            {"cinema_id": "13", "name": "UGC Odéon"},
            {"cinema_id": "14", "name": "UGC Montparnasse"},
            {"cinema_id": "15", "name": "UGC Rotonde"},
            {"cinema_id": "16", "name": "UGC Maillot"},
            {"cinema_id": "17", "name": "UGC Bastille"},
            {"cinema_id": "37", "name": "UGC Ciné Cité Paris 19"},
            {"cinema_id": "21", "name": "UGC Ciné Cité La Défense"},
        ]

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def parse_film_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse film blocks from the cinema showings response.

        The cinema-page endpoint returns one film per `div.slider-item` block.
        """
        films: List[Dict[str, Any]] = []
        seen_titles = set()
        blocks = soup.select("div.slider-item")

        for block in blocks:
            title = ""
            title_elem = block.select_one(".component--film-presentation a[title]")
            if title_elem:
                title = title_elem.get("title", "").strip()

            if not title or title in seen_titles:
                continue

            block_text = block.get_text("\n", strip=True)
            showtimes = sorted(set(re.findall(r"(\d{2}:\d{2})", block_text)))

            seen_titles.add(title)
            films.append(
                {
                    "title": title,
                    "showtimes": showtimes,
                    "showtime_count": len(showtimes),
                }
            )

        return films

    # def get_showtimes_for_cinema(self, cinema: Dict[str, str], date_str: str) -> Dict[str, Any]:
    #     """
    #     Fetch all film showtimes for one cinema on one date.
    #     """
    #     try:
    #         response = requests.get(
    #             self.showings_endpoint,
    #             params={"cinemaId": cinema["cinema_id"], "date": date_str},
    #             headers=self.headers,
    #             timeout=30,
    #         )
    #         response.raise_for_status()

    #         soup = BeautifulSoup(response.text, "html.parser")
    #         films = self.parse_film_blocks(soup)

    #         return {
    #             "date": date_str,
    #             "cinema_id": cinema["cinema_id"],
    #             "name": cinema["name"],
    #             "films": films,
    #         }

    #     except Exception as e:
    #         print(f"Error getting UGC showtimes for {cinema['name']} on {date_str}: {e}")
    #         return {
    #             "date": date_str,
    #             "cinema_id": cinema["cinema_id"],
    #             "name": cinema["name"],
    #             "films": [],
    #             "error": str(e),
    #         }

    def get_showtimes_for_cinema(self, cinema: Dict[str, str], date_str: str) -> Dict[str, Any]:
        try:
            response = requests.get(
                self.showings_endpoint,
                params={"cinemaId": cinema["cinema_id"], "date": date_str},
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            films = self.parse_film_blocks(soup)

            return {
                "date": date_str,
                "cinema_id": cinema["cinema_id"],
                "name": cinema["name"],
                "films": films,
            }

        except Exception as e:
            print(f"Error getting UGC showtimes for {cinema['name']} on {date_str}: {e}")
            return {
                "date": date_str,
                "cinema_id": cinema["cinema_id"],
                "name": cinema["name"],
                "films": [],
                "error": str(e),
            }


    def fetch_showtimes_for_next_7_days(self) -> Dict[str, Any]:
        """
        Fetch Paris UGC cinema showtimes for the next 7 days.
        """
        all_showtimes = {
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "source": "UGC cinema page endpoint",
                "base_url": self.base_url,
                "date_range": "Next 7 days from today",
            },
            "dates": {},
        }

        cinemas = self.paris_cinemas
        if not cinemas:
            print("No Paris UGC cinemas found.")
            return all_showtimes

        today = date.today()
        dates_to_fetch = [
            (today + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(7)
        ]

        print(f"Found {len(cinemas)} Paris UGC cinemas")
        print(f"Fetching showtimes for: {', '.join(dates_to_fetch)}")

        for date_str in dates_to_fetch:
            print(f"Fetching Paris UGC showtimes for {date_str}...")
            all_showtimes["dates"][date_str] = {
                "date": date_str,
                "cinemas": [],
            }

            for cinema in cinemas:
                cinema_data = self.get_showtimes_for_cinema(cinema, date_str)
                all_showtimes["dates"][date_str]["cinemas"].append(cinema_data)
                time.sleep(0.3)

        return all_showtimes

    def save_showtimes_to_file(self, showtimes_data: Dict[str, Any], filename: str) -> bool:
        """
        Save fetched UGC cinema showtimes to a JSON file.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(showtimes_data, f, indent=2, ensure_ascii=False)

            print(f"UGC cinema showtimes saved to {filename}")
            return True

        except Exception as e:
            print(f"Error saving UGC cinema showtimes: {e}")
            return False


def main():
    print("=== UGC Cinema Showtimes Fetcher V2 ===")

    fetcher = UGCCinemaShowtimesFetcher()
    showtimes_data = fetcher.fetch_showtimes_for_next_7_days()

    if showtimes_data.get("dates"):
        fetcher.save_showtimes_to_file(showtimes_data, "ugc_cinema_showtimes_v2.json")
    else:
        print("No UGC cinema showtimes data found")


if __name__ == "__main__":
    main()
