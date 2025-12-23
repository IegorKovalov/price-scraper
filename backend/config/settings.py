import os
from dotenv import load_dotenv
from pathlib import Path

# Get the backend directory path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from backend directory
load_dotenv(BASE_DIR / '.env')

SCRAPE_DO_TOKEN = os.getenv("SCRAPE_DO_TOKEN")
SCRAPE_DO_API_URL = 'http://api.scrape.do/'

WALMART_SEARCH_URL = 'https://www.walmart.com/search?q={query}'
WALMART_SELECTORS = {
    'product_container': 'div[data-item-id]',
    'name': 'span[data-automation-id="product-title"]',
    'price': 'div[data-automation-id="product-price"] span',
    'image': 'img[data-testid="productTileImage"]',
    'link': 'a[link-identifier]'
}