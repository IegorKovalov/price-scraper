from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers.scraper_manager import scrape_all_sites

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        print(f"[API] Received search request: {query}")
        
        # Scrape all sites together
        results = scrape_all_sites(query, max_results_per_site=3)
        
        return jsonify({
            'success': True,
            'count': len(results['products']),
            'products': results['products'],
            'by_store': results['by_store'],
            'errors': results['errors']
        })
    
    except Exception as e:
        print(f"[ERROR] API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)