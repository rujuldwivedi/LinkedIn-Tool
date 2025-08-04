from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import time
from debugger.debug_helper import save_debug_info

load_dotenv()

def scrape_saved_jobs():
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            viewport={"width": 1280, "height": 1024},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Step 1: Login
            print("🔐 Logging into LinkedIn for jobs...")
            page.goto("https://www.linkedin.com/login", timeout=30000)
            page.fill("input#username", email)
            page.fill("input#password", password)
            page.click("button[type='submit']")
            
            # Wait for feed or possible 2FA
            try:
                page.wait_for_selector("div.feed-identity-module", timeout=15000)
            except:
                print("⚠️ May require 2FA - please check browser")
                save_debug_info(page, "jobs_2fa_required")
                input("Press Enter after completing login/2FA...")

            # Step 2: Navigate to saved jobs
            print("🌐 Navigating to saved jobs page...")
            page.goto("https://www.linkedin.com/my-items/saved-jobs/", timeout=30000)
            
            # Wait for jobs to load
            try:
                page.wait_for_selector(
                    "section.jobs-saved-jobs-list, "
                    "div.artdeco-empty-state", 
                    timeout=20000
                )
            except:
                print("⚠️ Jobs page didn't load as expected")
                debug_path = save_debug_info(page, "jobs_failed")
                print(f"Check {debug_path} to see what loaded")
                return []

            # Check for empty state
            if page.query_selector("div.artdeco-empty-state"):
                print("ℹ️ No saved jobs found")
                return []

            # Step 3: Scroll to load all jobs
            print("🔄 Scrolling to load jobs...")
            scroll_attempts = 0
            last_count = 0
            
            while scroll_attempts < 10:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)  # Increased wait time
                
                current_jobs = page.query_selector_all("li.jobs-saved-jobs-list__list-item")
                print(f"🔍 Found {len(current_jobs)} jobs so far...")
                
                if len(current_jobs) > last_count:
                    last_count = len(current_jobs)
                    scroll_attempts = 0
                else:
                    scroll_attempts += 1

            # Step 4: Extract job data
            jobs = []
            job_cards = page.query_selector_all("li.jobs-saved-jobs-list__list-item")
            print(f"📊 Processing {len(job_cards)} jobs...")
            
            for card in job_cards:
                try:
                    title = card.query_selector("a.job-card-list__title").inner_text().strip()
                    company = card.query_selector("span.job-card-container__company-name").inner_text().strip()
                    job_url = card.query_selector("a.job-card-list__title").get_attribute("href").split('?')[0]
                    
                    if not job_url.startswith("http"):
                        job_url = f"https://www.linkedin.com{job_url}"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "job_url": job_url
                    })
                except Exception as e:
                    print(f"⚠️ Skipping job: {str(e)}")
                    continue

            print(f"✅ Successfully fetched {len(jobs)} saved jobs")
            return jobs

        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            save_debug_info(page, "jobs_critical_error")
            return []
        finally:
            browser.close()