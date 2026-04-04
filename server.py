import sys
import re
import argparse
import joblib
from urllib.parse import urlparse
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# 1. LOAD THE MODEL
# ==========================================
try:
    model = joblib.load('compressed_malicious_url_rf_model.pkl')
except Exception as e:
    print(f"[-] Error loading model: {e}")
    model = None


# ==========================================
# 2. FEATURE EXTRACTION FUNCTIONS
# ==========================================
def Shortining_Service(url):
    match = re.search(r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                      r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                      r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                      r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                      r'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                      r'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                      r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
                      r'tr\.im|link\.zip\.net', url)
    return 1 if match else 0

def having_ip_address(url):
    match = re.search(
        r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.'
        r'([01]?\d\d?|2[0-4]\d|25[0-5])\/)|'  # IPv4
        r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.'
        r'([01]?\d\d?|2[0-4]\d|25[0-5])\/)|'  # IPv4 with port
        r'((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)' # IPv4 in hex
        r'(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|'
        r'([0-9]+(?:\.[0-9]+){3}:[0-9]+)|'
        r'((?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5])\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:\/\d{1,2})?)', url)  # IPv6
    return 1 if match else 0

def abnormal_url(url):
    hostname = urlparse(url).hostname
    if hostname:
        match = re.search(hostname, url)
        if match:
            return 1
    return 0

def extract_features(url):
    """
    Extracts the EXACT 20 features expected by the RandomForest model.
    Order is critical here. Do not change it.
    """
    return [[
        len(url),                                   # 1. url_len
        url.count('@'),                             # 2. @
        url.count('?'),                             # 3. ?
        url.count('-'),                             # 4. -
        url.count('='),                             # 5. =
        url.count('.'),                             # 6. .
        url.count('#'),                             # 7. #
        url.count('%'),                             # 8. %
        url.count('+'),                             # 9. +
        url.count('$'),                             # 10. $
        url.count('!'),                             # 11. !
        url.count('*'),                             # 12. *
        url.count(','),                             # 13. ,
        url.count('//'),                            # 14. //
        abnormal_url(url),                          # 15. abnormal_url
        1 if urlparse(url).scheme == 'https' else 0,# 16. https
        sum(c.isdigit() for c in url),              # 17. digits
        sum(c.isalpha() for c in url),              # 18. letters
        Shortining_Service(url),                    # 19. Shortining_Service
        having_ip_address(url)                      # 20. having_ip_address
    ]]


# ==========================================
# 3. FLASK API ROUTES
# ==========================================
@app.route('/', methods=['GET'])
def home():
    # Fixes your 404 error by providing a basic root response!
    return jsonify({
        "status": "online",
        "message": "API is running. Send a POST request to /predict with {'url': 'your_link_here'}"
    })

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL in JSON payload.'}), 400
        
    url = data['url']
    
    try:
        features = extract_features(url)
        prediction = model.predict(features)[0]
        
        return jsonify({
            'url': url,
            'prediction_class': int(prediction)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# 4. STARTUP SCRIPT & TESTING FLAG
# ==========================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Flask Server or Test Model")
    parser.add_argument('--test', type=str, help='Test a URL instantly in the terminal')
    args = parser.parse_args()

    if args.test:
        print(f"\n[+] Extracting 20 features for: {args.test}")
        if model is None:
            print("[-] FATAL: Cannot test, model did not load.")
            sys.exit(1)
            
        features = extract_features(args.test)
        print(f"[+] Extracted features array: {features}")
        
        prediction = model.predict(features)[0]
        print(f"\n[>>>] PREDICTION CLASS: {prediction}\n")
        sys.exit(0)
        
    print("Starting Flask server on port 5000...")
    print("Use --test flag to test URLs in terminal without starting server")
    app.run(debug=True, port=5000)