from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers.walmart_scraper import scrape_walmart

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        # Scrape Walmart
        results = scrape_walmart(query)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'products': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)