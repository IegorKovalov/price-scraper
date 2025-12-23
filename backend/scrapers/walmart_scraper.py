import requests
import json
from bs4 import BeautifulSoup
from config.settings import SCRAPE_DO_TOKEN, SCRAPE_DO_API_URL, WALMART_SEARCH_URL

def scrape_walmart(query, max_results=3):
    """Scrape Walmart for products matching the query"""
    try:
        search_url = WALMART_SEARCH_URL.format(query=query.replace(' ', '+'))
        
        response = requests.get(
            SCRAPE_DO_API_URL,
            params={
                'token': SCRAPE_DO_TOKEN,
                'url': search_url
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
        
        if not next_data_script:
            return []
        
        data = json.loads(next_data_script.string)
        
        # Navigate: props > pageProps > initialData > searchResult > itemStacks > items
        search_result = data['props']['pageProps']['initialData']['searchResult']
        item_stacks = search_result.get('itemStacks', [])
        
        products = []
        count = 0
        
        for stack in item_stacks:
            if count >= max_results:
                break
            
            items = stack.get('items', [])
            
            for item in items:
                if count >= max_results:
                    break
                
                # Extract data
                name = item.get('name', '')
                
                # Price from priceInfo.minPrice
                price_info = item.get('priceInfo', {})
                price = price_info.get('minPrice', 0.0)
                
                # Image from imageInfo.thumbnailUrl
                image_info = item.get('imageInfo', {})
                image_url = image_info.get('thumbnailUrl', '')
                
                # Link from canonicalUrl
                canonical_url = item.get('canonicalUrl', '')
                link = f"https://www.walmart.com{canonical_url}" if canonical_url else ''
                
                if name and price > 0:
                    product = {
                        'name': name,
                        'price': float(price),
                        'image': image_url,
                        'link': link,
                        'store': 'Walmart'
                    }
                    products.append(product)
                    count += 1
        
        return products
    
    except Exception as e:
        print(f"[ERROR] Walmart scraper: {e}")
        return []