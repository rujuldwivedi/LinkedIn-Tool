from src.connection_fetcher import fetch_connections
from src.job_scraper import scrape_saved_jobs
from src.matcher import match_jobs_with_connections
from src.messenger import send_messages

def main():
    print("Fetching latest LinkedIn connections...")
    connections = fetch_connections()

    print("Scraping saved jobs from LinkedIn...")
    jobs = scrape_saved_jobs()

    print("Matching jobs with connections...")
    matched = match_jobs_with_connections(jobs, connections)

    if not matched:
        print("No matches found. Exiting.")
        return

    print(f"{len(matched)} matches found. Ready to send messages.")
    send_messages(matched)

if __name__ == "__main__":
    main()