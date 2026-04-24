import argparse
import os
import sys
from contextlib import contextmanager
from typing import Optional

# Ensure the script runs from the project root containing this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

# Import modules from subdirectories (namespace packages)
try:
    from Dulac.dulac_showtimes_fetcher import DulacShowtimesFetcher
    from UGC.ugc_films_parser import UGCFilmsParser
    from UGC.ugc_showtimes_fetcher import UGCShowtimesFetcher
    from Paris_Cinema_Club.paris_cinema_club_pdf_downloader import (
        get_pdf_urls_from_website,
        download_pdf,
    )
    from Paris_Cinema_Club.paris_cinema_club_pdf_parser import ParisCinemaClubPDFParser
    import combine_showtimes
except Exception as import_error:
    print(f"Error importing modules: {import_error}")
    print("Make sure you run this script from the 'Cinema-showtimes-app' directory and that dependencies are installed (pip install -r requirements.txt).")
    sys.exit(1)


@contextmanager
def pushd(path: str):
    """Temporarily change working directory."""
    previous = os.getcwd()
    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def run_paris_cinema_club(skip_download: bool = False) -> None:
    """Download PCC PDFs to Supabase Storage and parse them into Supabase."""
    pcc_dir = os.path.join(PROJECT_ROOT, "Paris_Cinema_Club")

    with pushd(pcc_dir):
        if not skip_download:
            urls = get_pdf_urls_from_website()
            # Fallback to skip if no URLs found
            if urls:
                downloaded = []
                for i, url in enumerate(urls):
                    if i == 0:
                        filename = "semainier_christine.pdf"
                    elif i == 1:
                        filename = "semainier_ecoles.pdf"
                    else:
                        filename = f"semainier_extra_{i+1}.pdf"
                    path = download_pdf(url, filename)
                    if path:
                        downloaded.append(path)
            else:
                print("No PCC PDF URLs found on website, skipping download step.")
        else:
            print("Skipping PCC PDF download as requested.")

        parser = ParisCinemaClubPDFParser()
        parser.run()


def run_dulac() -> None:
    """Fetch Dulac showtimes for next 7 days and sync to Supabase."""
    fetcher = DulacShowtimesFetcher()
    showtimes_data = fetcher.fetch_showtimes_for_next_7_days()
    fetcher.save_showtimes(showtimes_data)


def run_ugc(max_films: Optional[int] = 5) -> None:
    """Fetch UGC films list and film date availability, save under UGC/."""
    ugc_dir = os.path.join(PROJECT_ROOT, "UGC")
    ensure_dir(ugc_dir)

    # Step 1: Parse films list
    films_parser = UGCFilmsParser()
    films_data = films_parser.fetch_and_parse_films()
    if not films_data:
        raise RuntimeError("Failed to fetch/parse UGC films data")

    films_parsed_path = os.path.join(ugc_dir, "ugc_films_parsed.json")
    films_parser.save_data_to_file(films_data, films_parsed_path)

    # Step 2: Fetch dates/cinemas
    showtimes_fetcher = UGCShowtimesFetcher()
    loaded_films = showtimes_fetcher.load_films_data(films_parsed_path)
    if not loaded_films:
        raise RuntimeError("Failed to load ugc_films_parsed.json for UGC showtimes fetching")

    dates_data = showtimes_fetcher.fetch_all_film_dates(loaded_films, max_films=max_films or 5)

    dates_output_path = os.path.join(ugc_dir, "ugc_film_dates.json")
    showtimes_fetcher.save_dates_to_file(dates_data, dates_output_path)

    if not os.path.exists(dates_output_path):
        raise FileNotFoundError("UGC film dates JSON not created")


def combine_to_csv() -> str:
    """Combine all sources into a single CSV and JSON using combine_showtimes module."""
    df = combine_showtimes.combine_all_showtimes()
    if df is None or df.empty:
        raise RuntimeError("No data combined. Ensure source JSON files exist and contain data.")

    # Save JSON via module helper
    combine_showtimes.save_combined_data(df, output_file="combined_showtimes.json")

    # Save CSV
    csv_path = os.path.join(PROJECT_ROOT, "combined_showtimes.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"Combined CSV saved to {csv_path}")
    return csv_path


def main():
    parser = argparse.ArgumentParser(description="Run all showtime fetchers/parsers and produce combined_showtimes.csv")
    parser.add_argument("--skip-pcc", action="store_true", help="Skip Paris Cinema Club PDF parsing")
    parser.add_argument("--skip-pcc-download", action="store_true", help="Skip downloading PCC PDFs (use existing files)")
    parser.add_argument("--skip-dulac", action="store_true", help="Skip Dulac showtimes fetching")
    parser.add_argument("--skip-ugc", action="store_true", help="Skip UGC fetching/parsing")
    parser.add_argument("--max-ugc-films", type=int, default=5, help="Max number of UGC films to process (for speed)")
    args = parser.parse_args()

    if not args.skip_pcc:
        print("\n=== Step 1: Paris Cinema Club ===")
        run_paris_cinema_club(skip_download=args.skip_pcc_download)
    else:
        print("Skipping Paris Cinema Club step")

    if not args.skip_dulac:
        print("\n=== Step 2: Dulac Cinemas ===")
        run_dulac()
    else:
        print("Skipping Dulac step")

    # if not args.skip_ugc:
    #     print("\n=== Step 3: UGC ===")
    #     run_ugc(max_films=args.max_ugc_films)
    # else:
    #     print("Skipping UGC step")

    # print("\n=== Step 4: Combine to CSV ===")
    # csv_path = combine_to_csv()

    # print("\nAll done!")
    # print(f"Output: {csv_path}")


if __name__ == "__main__":
    main()
