from playwright.sync_api import sync_playwright

def scrape_saved_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🔐 Logging into LinkedIn for saved jobs...")
        page.goto("https://www.linkedin.com/login")
        page.fill("input#username", "{my email}")
        page.fill("input#password", "{my password}")
        page.click("button[type='submit']")

        page.wait_for_url("https://www.linkedin.com/feed/")
        page.goto("https://www.linkedin.com/my-items/saved-jobs/")

        page.wait_for_selector(".job-card-container")

        jobs = []
        cards = page.query_selector_all(".job-card-container")
        for card in cards:
            title = card.query_selector(".job-card-list__title").inner_text().strip()
            company = card.query_selector(".job-card-container__company-name").inner_text().strip()
            job_link = card.query_selector("a.job-card-list__title").get_attribute("href")
            jobs.append({
                "title": title,
                "company": company,
                "job_link": f"https://www.linkedin.com{job_link}"
            })

        browser.close()
        return jobs