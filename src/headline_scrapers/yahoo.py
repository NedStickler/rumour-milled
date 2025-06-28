from playwright.sync_api import sync_playwright


if __name__ == "__main__":
    with sync_playwright() as p:
        p.selectors.set_test_id_attribute("data-test-locator")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://news.yahoo.com/")
        page.locator("button", has_text="reject").click()
        page.wait_for_selector("a.stream-title")
        stream_item_titles = page.locator(
            '[data-test-locator="stream-item-title"]'
        ).all()
        item_titles = page.locator('[data-test-locator="item-title"]').all()
        headlines = page.locator('[data-test-locator="headline"]').all()
        hrefs = [element.get_attribute("href") for element in page.locator("a").all()]
        print(hrefs)
