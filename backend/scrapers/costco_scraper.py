import requests
import time
from bs4 import BeautifulSoup
from config.settings import SCRAPE_DO_TOKEN, SCRAPE_DO_API_URL

COSTCO_SEARCH_URL = 'https://www.costco.com/CatalogSearch?keyword={query}'

def scrape_costco(query, max_results=3):
    """Scrape Costco for products matching the query"""
    
    # Try 3 times with longer timeout
    for attempt in range(3):
        try:
            search_url = COSTCO_SEARCH_URL.format(query=query.replace(' ', '+'))
            print(f"[DEBUG] Costco attempt {attempt + 1}/3: {search_url}")
            
            response = requests.get(
                SCRAPE_DO_API_URL,
                params={
                    'token': SCRAPE_DO_TOKEN,
                    'url': search_url
                },
                timeout=30  # Increased timeout
            )
            
            print(f"[DEBUG] Costco Status: {response.status_code}")
            
            if response.status_code != 200:
                if attempt < 2:
                    time.sleep(2)
                    continue
                return []
            
            # Save HTML for debugging
            with open('debug_costco.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("[DEBUG] Saved Costco HTML")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # Try multiple selectors
            items = soup.find_all('div', class_='product')
            if not items:
                items = soup.find_all('div', class_='product-tile')
            if not items:
                items = soup.find_all('div', attrs={'automation-id': 'productTile'})
            
            print(f"[DEBUG] Found {len(items)} Costco items")
            
            for item in items[:max_results * 2]:
                if len(products) >= max_results:
                    break
                
                try:
                    # Name
                    name_elem = item.find('span', class_='description')
                    if not name_elem:
                        name_elem = item.find('a', class_='product-title')
                    if not name_elem:
                        name_elem = item.find('h2')
                    
                    name = name_elem.get_text(strip=True) if name_elem else None
                    
                    # Price
                    price_elem = item.find('div', class_='price')
                    if not price_elem:
                        price_elem = item.find('span', class_='value')
                    
                    price = 0.0
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price_text = price_text.replace('$', '').replace(',', '').strip()
                        try:
                            price = float(price_text)
                        except:
                            pass
                    
                    # Image
                    img_elem = item.find('img')
                    image = ''
                    if img_elem:
                        image = img_elem.get('src', '') or img_elem.get('data-src', '')
                        if image and not image.startswith('http'):
                            image = 'https://www.costco.com' + image
                    
                    # Link
                    link_elem = item.find('a', href=True)
                    link = ''
                    if link_elem:
                        href = link_elem.get('href', '')
                        if href.startswith('http'):
                            link = href
                        elif href:
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
                        print(f"[DEBUG] Added Costco product: {name[:50]}... - ${price}")
                
                except Exception as e:
                    print(f"[DEBUG] Error parsing Costco item: {e}")
                    continue
            
            return products
        
        except requests.exceptions.Timeout:
            if attempt < 2:
                print(f"[DEBUG] Costco timeout on attempt {attempt + 1}, retrying...")
                time.sleep(2)
                continue
            print(f"[ERROR] Costco scraper: Timeout after 3 attempts")
            return []
        
        except Exception as e:
            if attempt < 2:
                print(f"[DEBUG] Costco error on attempt {attempt + 1}: {e}, retrying...")
                time.sleep(2)
                continue
            print(f"[ERROR] Costco scraper: {e}")
            return []
    
    return []

