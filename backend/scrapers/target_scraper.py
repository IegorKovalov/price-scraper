import requests
import json
import urllib.parse
from config.settings import SCRAPE_DO_TOKEN, SCRAPE_DO_API_URL

def scrape_target(query, max_results=5):
    """
    Scrape Target using ScrapeDo to bypass restrictions
    """
    
    try:
        print(f"[DEBUG] Target search for: {query}")
        
        # Target's search API URL
        target_api = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
        
        params = {
            'key': '9f36aeafbe60771e321a7cc95a78140772ab3e96',
            'channel': 'WEB',
            'count': '24',
            'default_purchasability_filter': 'true',
            'include_sponsored': 'true',
            'keyword': query,
            'offset': '0',
            'page': f'/s?searchTerm={urllib.parse.quote(query)}',
            'platform': 'desktop',
            'pricing_store_id': '3991',
            'useragent': 'Mozilla/5.0',
            'visitor_id': '019B5F508E770201A1BCC5D6CBD6547A'
        }
        
        # Build full URL
        api_url = f"{target_api}?{urllib.parse.urlencode(params)}"
        
        print(f"[DEBUG] Using ScrapeDo proxy for Target API")
        
        # Call through ScrapeDo
        response = requests.get(
            SCRAPE_DO_API_URL,
            params={
                'token': SCRAPE_DO_TOKEN,
                'url': api_url,
                'render': 'false'  # Don't need JS rendering for API
            },
            timeout=30
        )
        
        print(f"[DEBUG] ScrapeDo Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[DEBUG] ScrapeDo failed: {response.text[:200]}")
            return []
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("[DEBUG] Response is not JSON, trying to parse as text")
            return []
        
        # Save for debugging
        with open('target_api_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("[DEBUG] Saved API response")
        
        # Parse products
        products = []
        
        # Navigate JSON: data -> search -> products
        if 'data' in data and 'search' in data['data']:
            search_data = data['data']['search']
            products_list = search_data.get('products', [])
            
            print(f"[DEBUG] Found {len(products_list)} products")
            
            for product in products_list[:max_results]:
                try:
                    tcin = product.get('tcin', '')
                    item = product.get('item', {})
                    
                    # Name
                    title = item.get('product_description', {}).get('title', '')
                    
                    # Price
                    price_data = product.get('price', {})
                    price = price_data.get('current_retail', 0)
                    if price == 0:
                        formatted = price_data.get('formatted_current_price', '$0')
                        try:
                            price = float(formatted.replace('$', '').replace(',', ''))
                        except:
                            price = 0
                    
                    # Image
                    images = item.get('enrichment', {}).get('images', {})
                    image = images.get('primary_image_url', '')
                    
                    # URL
                    url = item.get('enrichment', {}).get('buy_url', '')
                    if not url and tcin:
                        url = f'https://www.target.com/p/-/A-{tcin}'
                    
                    if title and price > 0:
                        products.append({
                            'name': title,
                            'price': float(price),
                            'image': image,
                            'link': url,
                            'store': 'Target'
                        })
                        print(f"[DEBUG] Added: {title[:40]}... - ${price}")
                
                except Exception as e:
                    print(f"[DEBUG] Error parsing product: {e}")
                    continue
        else:
            print(f"[DEBUG] Unexpected JSON structure. Keys: {list(data.keys())}")
        
        print(f"[DEBUG] Total Target products: {len(products)}")
        return products
    
    except requests.Timeout:
        print("[DEBUG] Target API timeout")
        return []
    except Exception as e:
        print(f"[DEBUG] Target scraper error: {e}")
        import traceback
        traceback.print_exc()
        return []