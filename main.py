import argparse
import os
import sys
import time
from contextlib import contextmanager
from typing import Optional

# Ensure the script runs from the project root containing this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

# Import modules from subdirectories (namespace packages)
try:
    from Dulac.dulac_showtimes_fetcher import DulacShowtimesFetcher
    from UGC.ugc_cinema_showtimes_fetcher import UGCCinemaShowtimesFetcher
    from Paris_Cinema_Club.paris_cinema_club_pdf_downloader import (
        get_pdf_urls_from_website,
        download_pdf,
    )
    from Paris_Cinema_Club.paris_cinema_club_pdf_parser import ParisCinemaClubPDFParser
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


def run_ugc() -> None:
    """Fetch UGC films list and film date availability, save to database."""
    fetcher = UGCCinemaShowtimesFetcher()

    showtimes_data = fetcher.fetch_showtimes_for_next_7_days()

    if showtimes_data.get("dates"):
        fetcher.save_showtimes(showtimes_data)
    else:
        print("No UGC cinema showtimes data found")

def timed_step(label: str, func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"{label} completed in {elapsed:.2f}s")
    return result


def main():
    parser = argparse.ArgumentParser(description="Run all showtime fetchers/parsers and produce combined_showtimes.csv")
    parser.add_argument("--skip-pcc", action="store_true", help="Skip Paris Cinema Club PDF parsing")
    parser.add_argument("--skip-pcc-download", action="store_true", help="Skip downloading PCC PDFs (use existing files)")
    parser.add_argument("--skip-dulac", action="store_true", help="Skip Dulac showtimes fetching")
    parser.add_argument("--skip-ugc", action="store_true", help="Skip UGC fetching/parsing")
    parser.add_argument("--max-ugc-films", type=int, default=5, help="Max number of UGC films to process (for speed)")
    args = parser.parse_args()

    total_start = time.perf_counter()

    if not args.skip_pcc:
        print("\n=== Step 1: Paris Cinema Club ===")
        timed_step("Paris Cinema Club", run_paris_cinema_club, skip_download=args.skip_pcc_download)
    else:
        print("Skipping Paris Cinema Club step")

    if not args.skip_dulac:
        print("\n=== Step 2: Dulac Cinemas ===")
        timed_step("Dulac", run_dulac)
    else:
        print("Skipping Dulac step")

    if not args.skip_ugc:
        print("\n=== Step 3: UGC ===")
        timed_step("UGC", run_ugc)
    else:
        print("Skipping UGC step")

    # print("\n=== Step 4: Combine to CSV ===")
    # csv_path = combine_to_csv()

    total_elapsed = time.perf_counter() - total_start
    print(f"\nAll done! Total runtime: {total_elapsed:.2f}s")
    # print(f"Output: {csv_path}")


if __name__ == "__main__":
    main()
