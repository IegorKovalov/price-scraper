from concurrent.futures import ThreadPoolExecutor, as_completed
from .walmart_scraper import scrape_walmart
from .amazon_scraper import scrape_amazon
# from .costco_scraper import scrape_costco  # Disabled for now

def scrape_all_sites(query, max_results_per_site=3):
    """
    Scrape Walmart and Amazon concurrently using ThreadPoolExecutor
    Returns aggregated results from both sites
    """
    results = {
        'walmart': [],
        'amazon': [],
        # 'costco': [],  # Disabled
        'errors': []
    }
    
    # Define scraper functions (only Walmart and Amazon)
    scrapers = {
        'walmart': lambda: scrape_walmart(query, max_results_per_site),
        'amazon': lambda: scrape_amazon(query, max_results_per_site),
    }
    
    print(f"[INFO] Starting concurrent scraping for query: {query}")
    
    # Execute all scrapers concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all tasks
        future_to_store = {
            executor.submit(scraper_func): store_name 
            for store_name, scraper_func in scrapers.items()
        }
        
        # Collect results as they complete
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
    
    # Aggregate all products
    all_products = []
    all_products.extend(results['walmart'])
    all_products.extend(results['amazon'])
    
    print(f"[INFO] Total products scraped: {len(all_products)}")
    
    return {
        'products': all_products,
        'by_store': {
            'walmart': results['walmart'],
            'amazon': results['amazon'],
        },
        'errors': results['errors']
    }