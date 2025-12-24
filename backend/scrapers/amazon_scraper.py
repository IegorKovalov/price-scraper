import requests
import json
from bs4 import BeautifulSoup
from config.settings import SCRAPE_DO_TOKEN, SCRAPE_DO_API_URL

AMAZON_SEARCH_URL = 'https://www.amazon.com/s?k={query}'

def scrape_amazon(query, max_results=3):
    """Scrape Amazon for products matching the query"""
    try:
        search_url = AMAZON_SEARCH_URL.format(query=query.replace(' ', '+'))
        print(f"[DEBUG] Amazon Search URL: {search_url}")
        
        response = requests.get(
            SCRAPE_DO_API_URL,
            params={
                'token': SCRAPE_DO_TOKEN,
                'url': search_url
            },
            timeout=30
        )
        
        print(f"[DEBUG] Amazon Status: {response.status_code}")
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # Amazon uses data-component-type="s-search-result"
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        print(f"[DEBUG] Found {len(items)} Amazon items")
        
        for item in items[:max_results * 3]:  # Get more items to increase success rate
            if len(products) >= max_results:
                break
                
            try:
                # Product name - try multiple selectors
                name_elem = item.find('h2')
                if not name_elem:
                    name_elem = item.find('span', {'class': 'a-size-base-plus'})
                if not name_elem:
                    name_elem = item.find('span', {'class': 'a-size-medium'})
                
                # Get all text from h2 or span
                name = name_elem.get_text(strip=True) if name_elem else None
                
                # Price - multiple possible locations
                price_elem = item.find('span', {'class': 'a-price'})
                price = 0.0
                if price_elem:
                    price_whole = price_elem.find('span', {'class': 'a-price-whole'})
                    price_fraction = price_elem.find('span', {'class': 'a-price-fraction'})
                    if price_whole:
                        price_str = price_whole.get_text(strip=True).replace(',', '').replace('.', '')
                        if price_fraction:
                            price_str += '.' + price_fraction.get_text(strip=True)
                        try:
                            price = float(price_str)
                        except:
                            price = 0.0
                
                # Image
                img_elem = item.find('img', {'class': 's-image'})
                image = img_elem.get('src', '') if img_elem else ''
                
                # Link
                link_elem = item.find('a', {'class': 'a-link-normal'})
                link = 'https://www.amazon.com' + link_elem.get('href', '') if link_elem else ''
                
                # Only add if we have name AND price
                if name and price > 0:
                    product = {
                        'name': name,
                        'price': float(price),
                        'image': image,
                        'link': link,
                        'store': 'Amazon'
                    }
                    products.append(product)
                    print(f"[DEBUG] Added Amazon product: {name[:50]}... - ${price}")
                else:
                    print(f"[DEBUG] Skipped item - name: {bool(name)}, price: {price}")
            
            except Exception as e:
                print(f"[DEBUG] Error parsing Amazon item: {e}")
                continue
        
        return products
    
    except Exception as e:
        print(f"[ERROR] Amazon scraper: {e}")
        import traceback
        traceback.print_exc()
        return []