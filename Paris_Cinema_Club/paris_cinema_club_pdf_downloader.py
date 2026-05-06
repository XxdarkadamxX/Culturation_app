import requests
import os
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup
from supabase import Client, create_client
import re


def get_pdf_urls_from_website():
    """
    Scrape the Paris Cinéma Club website to find current PDF URLs
    """
    url = "https://pariscinemaclub.com/programmation-et-horaires/"
    
    try:
        print("Scraping website for PDF links...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all PDF links
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                pdf_links.append(href)
        
        # Filter for the specific PDFs we want (semainier files)
        semainier_pdfs = [link for link in pdf_links if 'semainier' in link.lower()]
        
        print(f"Found {len(semainier_pdfs)} semainier PDF files:")
        for pdf in semainier_pdfs:
            print(f"  - {pdf}")
        
        return semainier_pdfs
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def create_supabase_client(supabase_url: str = None, supabase_key: str = None):
    """
    Create and return a Supabase client using environment variables or provided credentials.
    """
    supabase_url = supabase_url or os.getenv("SUPABASE_URL")
    supabase_key = supabase_key or os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your environment or passed as arguments.")

    return create_client(supabase_url, supabase_key)

def download_pdf(url, filename):
    """
    Download the pdf files and save them in database
    """
    try:
        print(f"Downloading: {url}")
        print(f"Filename: {filename}")
        
        # Send request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        supabase_client = create_supabase_client()

        bucket = os.getenv("PDF_BUCKET")
        if not bucket:
            raise ValueError("PDF_BUCKET must be set in the environment or secrets.")
        
        # Upload the file to the supabase bucket
        supabase_client.storage.from_(bucket).update(
            f"semainier_paris_cinema_club/{filename}",
            response.content,
            file_options={"content-type": "application/pdf", "upsert":"true"}
        )
        
        print(f"Successfully downloaded: {bucket}/{filename}")
        return f"{bucket}/{filename}"
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading {url}: {e}")
        return None

def main():
    """
    Download the PDF files from Paris Cinéma Club with dynamic URL detection
    """
    print("Starting dynamic download of Paris Cinéma Club PDF files...")
    print("=" * 60)
    
    # Get current PDF URLs from the website
    pdf_urls = get_pdf_urls_from_website()

    if not pdf_urls:
        print("No PDF files found on the website!")
        return
    
    downloaded_files = []
    
    # Download each PDF with specific names
    for i, url in enumerate(pdf_urls):
        if i == 0:
            filename = "semainier_christine.pdf"
        elif i == 1:
            filename = "semainier_ecoles.pdf"
        else:
            # For any additional PDFs, use a generic name
            filename = f"semainier_extra_{i+1}.pdf"
        
        filepath = download_pdf(url, filename)
        if filepath:
            downloaded_files.append(filepath)
        
        # Add a small delay between downloads
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Download Summary:")
    print(f"Successfully downloaded {len(downloaded_files)} files:")
    for filepath in downloaded_files:
        print(f"  - {filepath}")

if __name__ == "__main__":
    main() 
