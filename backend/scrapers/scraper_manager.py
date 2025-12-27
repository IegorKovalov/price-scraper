from concurrent.futures import ThreadPoolExecutor, as_completed
from .walmart_scraper import scrape_walmart
from .amazon_scraper import scrape_amazon
from .costco_scraper import scrape_costco

def scrape_all_sites(query, max_results_per_site=3):
    results = {
        'walmart': [],
        'amazon': [],
        'costco': [],
        'errors': []
    }
    
    scrapers = {
        'walmart': lambda: scrape_walmart(query, max_results_per_site),
        'amazon': lambda: scrape_amazon(query, max_results_per_site),
        'costco': lambda: scrape_costco(query, max_results_per_site)
    }
    
    print(f"[INFO] Starting concurrent scraping for query: {query}")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_store = {
            executor.submit(scraper_func): store_name 
            for store_name, scraper_func in scrapers.items()
        }
        
        for future in as_completed(future_to_store):
            store_name = future_to_store[future]
            try:
                products = future.result()
                results[store_name] = products
                print(f"[INFO] {store_name.capitalize()} returned {len(products)} products")
            except Exception as e:
                error_msg = f"{store_name.capitalize()} scraper failed: {str(e)}"
                print(f"[ERROR] {error_msg}")
                results['errors'].append(error_msg)
    
    all_products = []
    all_products.extend(results['walmart'])
    all_products.extend(results['amazon'])
    all_products.extend(results['costco'])  
    
    print(f"[INFO] Total products scraped: {len(all_products)}")
    
    return {
        'products': all_products,
        'by_store': {
            'walmart': results['walmart'],
            'amazon': results['amazon'],
            'costco': results['costco']
        },
        'errors': results['errors']
    }