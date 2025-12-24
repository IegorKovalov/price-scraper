import requests
import json
from bs4 import BeautifulSoup
from config.settings import SCRAPE_DO_TOKEN, SCRAPE_DO_API_URL

COSTCO_SEARCH_URL = 'https://www.costco.com/CatalogSearch?keyword={query}'

def scrape_costco(query, max_results=3):
    """Scrape Costco for products matching the query"""
    try:
        search_url = COSTCO_SEARCH_URL.format(query=query.replace(' ', '+'))
        print(f"[DEBUG] Costco Search URL: {search_url}")
        
        response = requests.get(
            SCRAPE_DO_API_URL,
            params={
                'token': SCRAPE_DO_TOKEN,
                'url': search_url
            },
            timeout=30
        )
        
        print(f"[DEBUG] Costco Status: {response.status_code}")
        
        if response.status_code != 200:
            return []
        
        # Save HTML for debugging
        with open('debug_costco.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("[DEBUG] Saved Costco HTML")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # Costco products are in product grid
        items = soup.find_all('div', {'class': 'product'})
        if not items:
            items = soup.find_all('div', {'class': 'product-tile'})
        
        print(f"[DEBUG] Found {len(items)} Costco items")
        
        for item in items[:max_results]:
            try:
                # Product name
                name_elem = item.find('span', {'class': 'description'})
                if not name_elem:
                    name_elem = item.find('a', {'class': 'product-title'})
                
                name = name_elem.get_text(strip=True) if name_elem else None
                
                # Price
                price_elem = item.find('div', {'class': 'price'})
                if not price_elem:
                    price_elem = item.find('span', {'class': 'value'})
                
                price = 0.0
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Remove $ and commas
                    price_text = price_text.replace('$', '').replace(',', '').strip()
                    try:
                        price = float(price_text)
                    except:
                        price = 0.0
                
                # Image
                img_elem = item.find('img')
                image = img_elem.get('src', '') if img_elem else ''
                if image and not image.startswith('http'):
                    image = 'https://www.costco.com' + image
                
                # Link
                link_elem = item.find('a', href=True)
                link = ''
                if link_elem:
                    href = link_elem.get('href', '')
                    if href.startswith('http'):
                        link = href
                    else:
                        link = 'https://www.costco.com' + href
                
                if name and price > 0:
                    product = {
                        'name': name,
                        'price': float(price),
                        'image': image,
                        'link': link,
                        'store': 'Costco'
                    }
                    products.append(product)
                    print(f"[DEBUG] Added Costco product: {name} - ${price}")
            
            except Exception as e:
                print(f"[DEBUG] Error parsing Costco item: {e}")
                continue
        
        return products
    
    except Exception as e:
        print(f"[ERROR] Costco scraper: {e}")
        import traceback
        traceback.print_exc()
        return []