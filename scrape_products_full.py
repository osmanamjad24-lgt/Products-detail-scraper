"""
web-scraping.dev Product Scraper (listing + full detail pages)
---------------------------------------------------------------
1. Walks through all 6 pages of https://web-scraping.dev/products
2. Collects each product's listing-page info (name, price, image, link)
3. Visits EACH product's own detail page to grab fuller info
   (description, and anything else found there)
4. Saves everything to a CSV file

Install first:
    pip install playwright
    playwright install chromium
"""

import csv
from playwright.sync_api import sync_playwright

BASE_LISTING_URL = "https://web-scraping.dev/products?page={}"
TOTAL_PAGES = 6  # confirmed from the site: "page 1 of total 28 results in 6 pages"

all_products = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # --- Step 1: Walk through every listing page ---
    for page_num in range(1, TOTAL_PAGES + 1):
        url = BASE_LISTING_URL.format(page_num)
        print(f"\nListing page {page_num}: {url}")
        page.goto(url)

        # Try to wait for product cards to appear. If this page times out
        # or fails for any reason, don't crash the whole script -- log it,
        # take a screenshot so we can see what actually happened, and
        # move on to the next page.
        try:
            page.wait_for_selector(".product", timeout=10000)  # 10 sec, not 30
        except Exception as e:
            print(f"  Page {page_num} FAILED to load products: {e}")
            page.screenshot(path=f"debug_page_{page_num}.png")
            print(f"  Saved screenshot: debug_page_{page_num}.png -- check this to see what went wrong")
            continue  # skip this page, move on to the next one

        product_cards = page.query_selector_all(".product")
        print(f"  Found {len(product_cards)} products on this page")

        for card in product_cards:
            name_el = card.query_selector("h3 a")
            price_el = card.query_selector(".price")  # fallback if class differs, see note below

            name = name_el.inner_text() if name_el else None
            detail_link = name_el.get_attribute("href") if name_el else None
            price_listing = price_el.inner_text() if price_el else None

            all_products.append({
                "name": name,
                "price_from_listing": price_listing,
                "detail_url": detail_link,
                "description": None,  # filled in during Step 2
            })

    # --- Step 2: Visit each product's own detail page ---
    print(f"\nVisiting {len(all_products)} individual product pages...\n")

    for product in all_products:
        if not product["detail_url"]:
            continue

        full_url = "https://web-scraping.dev" + product["detail_url"] if product["detail_url"].startswith("/") else product["detail_url"]
        page.goto(full_url)

        try:
            page.wait_for_selector("h3.product-title", timeout=10000)
        except Exception as e:
            print(f"  FAILED on detail page {full_url}: {e}")
            continue  # skip this product, keep going with the rest

        title_el = page.query_selector("h3.product-title")
        price_el = page.query_selector(".product-price")
        desc_el = page.query_selector(".product-description")

        product["name"] = title_el.inner_text() if title_el else product["name"]
        product["price_detail"] = price_el.inner_text() if price_el else None
        product["description"] = desc_el.inner_text() if desc_el else None

        # Features table: a variable number of <tr class="feature"> rows,
        # each with a label cell and a value cell. We collect these into
        # a dictionary since different products may have different features
        # (e.g. "material" for one, "battery life" for another).
        feature_rows = page.query_selector_all("tr.feature")
        features = {}
        for row in feature_rows:
            label_el = row.query_selector(".feature-label")
            value_el = row.query_selector(".feature-value")
            if label_el and value_el:
                label = label_el.inner_text().strip()
                value = value_el.inner_text().strip()
                features[label] = value

        # Store as a single readable string for the CSV
        # (CSV columns don't handle variable-length dictionaries well)
        product["features"] = "; ".join(f"{k}: {v}" for k, v in features.items())

        print(f"  Scraped detail: {product['name']}")

    browser.close()

# --- Step 3: Save to CSV ---
fieldnames = ["name", "price_from_listing", "price_detail", "detail_url", "description", "features"]
with open("web_scraping_dev_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print(f"\nDone. Saved {len(all_products)} products to web_scraping_dev_products.csv")