from src.connection_fetcher import fetch_connections
from src.job_scraper import scrape_saved_jobs
from src.matcher import match_jobs_with_connections
from src.messenger import send_messages
import json
from datetime import datetime
from pathlib import Path
from data.storage import update_connections, update_jobs

def main():
    print("Fetching latest LinkedIn connections...")
    new_connections = fetch_connections()
    all_connections = update_connections(new_connections)
    
    print("Scraping saved jobs from LinkedIn...")
    new_jobs = scrape_saved_jobs()
    all_jobs = update_jobs(new_jobs)
    
    print(f"Total connections: {len(all_connections)}")
    print(f"Total saved jobs: {len(all_jobs)}")
    
    print("Matching jobs with connections...")
    matched = match_jobs_with_connections(all_jobs, all_connections)
    
    if not matched:
        print("No new matches found.")
        return
    
    print(f"{len(matched)} new matches found. Ready to send messages.")
    send_messages(matched)

if __name__ == "__main__":
    main()