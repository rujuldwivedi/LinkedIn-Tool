from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import time
from debugger.debug_helper import save_debug_info

load_dotenv()

def fetch_connections():
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
            print("🔐 Logging into LinkedIn...")
            page.goto("https://www.linkedin.com/login", timeout=30000)
            page.fill("input#username", email)
            page.fill("input#password", password)
            page.click("button[type='submit']")
            
            # Wait for feed or possible 2FA
            try:
                page.wait_for_selector("div.feed-identity-module", timeout=15000)
            except:
                print("⚠️ May require 2FA - please check browser")
                save_debug_info(page, "2fa_required")
                input("Press Enter after completing login/2FA...")

            # Step 2: Navigate to connections
            print("🌐 Navigating to connections page...")
            page.goto("https://www.linkedin.com/mynetwork/invite-connect/connections/", timeout=30000)
            
            # Wait for connections to load
            try:
                page.wait_for_selector(
                    "div.mn-connections__header, "
                    "div.artdeco-empty-state", 
                    timeout=20000
                )
            except:
                print("⚠️ Connections page didn't load as expected")
                debug_path = save_debug_info(page, "connections_failed")
                print(f"Check {debug_path} to see what loaded")
                return []

            # Check for empty state
            if page.query_selector("div.artdeco-empty-state"):
                print("ℹ️ No connections found")
                return []

            # Step 3: Scroll to load all connections
            print("🔄 Scrolling to load connections...")
            scroll_attempts = 0
            last_count = 0
            
            while scroll_attempts < 10:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)  # Increased wait time
                
                current_cards = page.query_selector_all("li.mn-connection-card")
                print(f"🔍 Found {len(current_cards)} connections so far...")
                
                if len(current_cards) > last_count:
                    last_count = len(current_cards)
                    scroll_attempts = 0
                else:
                    scroll_attempts += 1

            # Step 4: Extract connection data
            connections = []
            cards = page.query_selector_all("li.mn-connection-card")
            print(f"📊 Processing {len(cards)} connections...")
            
            for card in cards:
                try:
                    name = card.query_selector("span.mn-connection-card__name").inner_text().strip()
                    occupation = card.query_selector("span.mn-connection-card__occupation").inner_text().strip()
                    profile_url = card.query_selector("a.mn-connection-card__link").get_attribute("href").split('?')[0]
                    
                    if not profile_url.startswith("http"):
                        profile_url = f"https://www.linkedin.com{profile_url}"
                    
                    connections.append({
                        "name": name,
                        "occupation": occupation,
                        "profile_url": profile_url
                    })
                except Exception as e:
                    print(f"⚠️ Skipping connection: {str(e)}")
                    continue

            print(f"✅ Successfully fetched {len(connections)} connections")
            return connections

        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            save_debug_info(page, "critical_error")
            return []
        finally:
            browser.close()