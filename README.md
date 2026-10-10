# Products Detail Scraper

A Python web scraping project that collects product details from [web-scraping.dev](https://web-scraping.dev/products), a site built for practicing scraping.

## What it does

1. Walks through the paginated product listing pages
2. Collects each product's name, listing price and link to its own page
3. Visits every product's detail page and scrapes the title, price, description and features table
4. Saves everything to `web_scraping_dev_products.csv`

If a page fails to load, the script logs the error, saves a debug screenshot (`debug_page_N.png`) and moves on instead of crashing.

## Setup

```
pip install -r requirements.txt
playwright install chromium
```

The second command downloads the browser Playwright controls. It is a separate step from `pip install`, so don't skip it.

## Usage

```
python scrape_products_full.py
```

## Output

A CSV file with these columns: `name`, `price_from_listing`, `price_detail`, `detail_url`, `description`, `features`.

## Notes

- The site reports 6 pages of results, but only 5 contain products (25 in total). The script skips the empty page.
- Built with [Playwright](https://playwright.dev/python/) for Python.
