from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Go directly to feed (you should already be logged in via browser cookies)
    page.goto("https://www.linkedin.com/feed/")
    time.sleep(5)

    # Print ALL buttons on the page so we can find the right one
    buttons = page.locator("button").all()
    print(f"\n Found {len(buttons)} buttons:")
    for i, btn in enumerate(buttons):
        try:
            print(f"  [{i}] '{btn.inner_text().strip()}' — class: {btn.get_attribute('class')}")
        except:
            pass

    input("\nPress ENTER to close browser...")
    browser.close()