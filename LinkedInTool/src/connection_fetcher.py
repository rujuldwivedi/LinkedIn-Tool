from playwright.sync_api import sync_playwright

def fetch_connections():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🔐 Logging into LinkedIn...")
        page.goto("https://www.linkedin.com/login")
        page.fill("input#username", "{my email}")
        page.fill("input#password", "{my password}")
        page.click("button[type='submit']")

        page.wait_for_url("https://www.linkedin.com/feed/")
        page.goto("https://www.linkedin.com/mynetwork/invite-connect/connections/")

        page.wait_for_selector("ul.mn-connection-card__list")

        connections = []
        for _ in range(5):  # You can increase scrolls
            cards = page.query_selector_all("li.mn-connection-card")
            for card in cards:
                name = card.query_selector("span.mn-connection-card__name").inner_text().strip()
                occupation = card.query_selector("span.mn-connection-card__occupation").inner_text().strip()
                profile_url = card.query_selector("a.mn-connection-card__link").get_attribute("href")
                connections.append({
                    "name": name,
                    "occupation": occupation,
                    "profile_url": f"https://www.linkedin.com{profile_url}"
                })
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1500)

        browser.close()
        return connections
