import joblib
import re
from urllib.parse import urlparse
import numpy as np
import pandas as pd
import os
import sys

class EnhancedURLClassifier:
    def __init__(self, model_path):
        """Load the existing model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at: {model_path}")
        self.model = joblib.load(model_path)
        print(f"[+] Model loaded successfully from: {model_path}")
        
    def extract_features(self, url):
        """Extract features exactly as your original model expects"""
        features = {
            'url_len': len(url),
            '@': url.count('@'),
            '?': url.count('?'),
            '-': url.count('-'),
            '=': url.count('='),
            '.': url.count('.'),
            '#': url.count('#'),
            '%': url.count('%'),
            '+': url.count('+'),
            '$': url.count('$'),
            '!': url.count('!'),
            '*': url.count('*'),
            ',': url.count(','),
            '//': url.count('//'),
            'abnormal_url': self._check_abnormal_url(url),
            'https': 1 if url.startswith('https') else 0,
            'digits': sum(c.isdigit() for c in url),
            'letters': sum(c.isalpha() for c in url),
            'Shortining_Service': self._check_shortening_service(url),
            'having_ip_address': self._check_ip_address(url)
        }
        return features
    
    def _check_abnormal_url(self, url):
        """Check if hostname appears abnormally in URL"""
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if hostname and hostname in url:
                return 1
            return 0
        except:
            return 0
    
    def _check_shortening_service(self, url):
        """Check for URL shortening services"""
        shortening_services = [
            'bit.ly', 'goo.gl', 'shorte.st', 'go2l.ink', 'x.co', 'ow.ly', 't.co', 
            'tinyurl', 'tr.im', 'is.gd', 'cli.gs', 'yfrog.com', 'migre.me', 'ff.im',
            'tiny.cc', 'url4.eu', 'twit.ac', 'su.pr', 'twurl.nl', 'snipurl.com',
            'short.to', 'BudURL.com', 'ping.fm', 'post.ly', 'Just.as', 'bkite.com',
            'snipr.com', 'fic.kr', 'loopt.us', 'doiop.com', 'short.ie', 'kl.am',
            'wp.me', 'rubyurl.com', 'om.ly', 'to.ly', 'bit.do', 'lnkd.in', 'db.tt',
            'qr.ae', 'adf.ly', 'cur.lv', 'ity.im', 'q.gs', 'po.st', 'bc.vc',
            'twitthis.com', 'u.to', 'j.mp', 'buzurl.com', 'cutt.us', 'u.bb',
            'yourls.org', 'prettylinkpro.com', 'scrnch.me', 'filoops.info',
            'vzturl.com', 'qr.net', '1url.com', 'tweez.me', 'v.gd', 'tr.im'
        ]
        url_lower = url.lower()
        return 1 if any(service in url_lower for service in shortening_services) else 0
    
    def _check_ip_address(self, url):
        """Check if URL contains an IP address"""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        return 1 if re.search(ip_pattern, url) else 0
    
    def _is_whitelisted(self, url):
        """Check if URL is from a trusted domain"""
        trusted_domains = [
            'google.com', 'www.google.com',
            'facebook.com', 'www.facebook.com',
            'twitter.com', 'www.twitter.com',
            'github.com', 'www.github.com',
            'stackoverflow.com',
            'wikipedia.org', 'www.wikipedia.org',
            'amazon.com', 'www.amazon.com',
            'microsoft.com', 'www.microsoft.com',
            'apple.com', 'www.apple.com',
            'yahoo.com', 'www.yahoo.com',
            'bing.com', 'www.bing.com',
            'linkedin.com', 'www.linkedin.com',
            'reddit.com', 'www.reddit.com',
            'netflix.com', 'www.netflix.com',
            'paypal.com', 'www.paypal.com',
            'youtube.com', 'www.youtube.com',
            'instagram.com', 'www.instagram.com',
            'whatsapp.com', 'www.whatsapp.com',
            'zoom.us', 'www.zoom.us',
            'spotify.com', 'www.spotify.com',
            'bbc.com', 'www.bbc.com',
            'cnn.com', 'www.cnn.com',
            'nytimes.com', 'www.nytimes.com'
        ]
        url_lower = url.lower()
        return any(domain in url_lower for domain in trusted_domains)
    
    def _has_phishing_patterns(self, url):
        """Rule-based detection for patterns the model might miss"""
        url_lower = url.lower()
        patterns = []
        
        # Multiple query parameters
        if url.count('=') >= 2 and '?' in url:
            patterns.append(True)
        
        # Suspicious keywords
        suspicious_words = ['login', 'verify', 'secure', 'account', 'update', 
                           'confirm', 'signin', 'banking', 'password', 'credential']
        if any(word in url_lower for word in suspicious_words):
            patterns.append(True)
        
        # Unusual TLDs (common for phishing)
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.xyz', '.top', '.club', '.online']
        if any(tld in url_lower for tld in suspicious_tlds):
            patterns.append(True)
        
        # @ symbol (browser ignores everything before it)
        if '@' in url:
            patterns.append(True)
        
        # Double slash in path (redirection trick)
        try:
            parsed = urlparse(url)
            if '//' in parsed.path:
                patterns.append(True)
        except:
            pass
        
        # Excessive dots (subdomain abuse)
        if url.count('.') >= 4:
            patterns.append(True)
        
        # HTTPS missing on login page
        if 'login' in url_lower and not url.startswith('https'):
            patterns.append(True)
        
        return sum(patterns) >= 2
    
    def predict(self, url):
        """Predict with enhanced logic using existing model"""
        
        # 1. WHITELIST CHECK - Fixes google.com false positive
        if self._is_whitelisted(url):
            print(f"[!] Whitelist: {url} is trusted")
            return {
                'url': url,
                'prediction_class': 0,
                'prediction_label': 'Benign',
                'confidence': 100.0,
                'original_prediction': 'Benign',
                'original_confidence': 100.0,
                'probabilities': {'Benign': 100.0, 'Defacement': 0.0, 'Phishing': 0.0, 'Malware': 0.0},
                'features': self.extract_features(url),
                'overridden': True
            }
        
        # 2. Extract features
        features = self.extract_features(url)
        
        # 3. Create DataFrame with proper feature names (fixes the warning)
        feature_names = ['url_len', '@', '?', '-', '=', '.', '#', '%', '+', '$', '!', '*', ',', '//', 
                         'abnormal_url', 'https', 'digits', 'letters', 'Shortining_Service', 'having_ip_address']
        feature_values = pd.DataFrame([list(features.values())], columns=feature_names)
        
        # 4. Get model prediction
        pred_class = self.model.predict(feature_values)[0]
        pred_probs = self.model.predict_proba(feature_values)[0]
        
        # Map class numbers to names (adjust based on your model)
        class_names = {0: 'Benign', 1: 'Defacement', 2: 'Phishing', 3: 'Malware'}
        confidence = max(pred_probs) * 100
        
        # Get all class probabilities
        probs_dict = {class_names[i]: pred_probs[i] * 100 for i in range(len(pred_probs))}
        
        # Store original values
        original_pred = pred_class
        original_confidence = confidence
        
        # 5. Override low-confidence predictions with rules
        if confidence < 75:
            if self._has_phishing_patterns(url):
                # Override to phishing (class 2) if patterns detected
                if probs_dict.get('Phishing', 0) < 50:
                    pred_class = 2
                    confidence = 75
                    print(f"[!] Override: Low confidence ({original_confidence:.1f}%) + phishing patterns")
        
        # 6. Override for defacement (class 1) with query parameters
        if probs_dict.get('Defacement', 0) > 30 and pred_class == 0:
            if '?' in url and url.count('=') >= 1:
                pred_class = 1
                confidence = probs_dict.get('Defacement', 0)
                print(f"[!] Override: Query params detected -> Defacement")
        
        return {
            'url': url,
            'prediction_class': pred_class,
            'prediction_label': class_names[pred_class],
            'confidence': confidence,
            'original_prediction': class_names[original_pred],
            'original_confidence': original_confidence,
            'probabilities': probs_dict,
            'features': features,
            'overridden': original_pred != pred_class
        }
    
    def predict_batch(self, urls):
        """Predict multiple URLs"""
        results = []
        for url in urls:
            results.append(self.predict(url))
        return results


# ============= MAIN TEST CODE =============

if __name__ == "__main__":
    
    # Get the correct path to the model file
    script_directory = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(script_directory, 'compressed_malicious_url_rf_model.pkl')
    
    print(f"[DEBUG] Script location: {script_directory}")
    print(f"[DEBUG] Looking for model at: {MODEL_PATH}")
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found at: {MODEL_PATH}")
        print("[INFO] Files in script directory:")
        for file in os.listdir(script_directory):
            print(f"  - {file}")
        sys.exit(1)
    
    # Get URL from command line or use defaults
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    else:
        test_urls = [
            "http://example.com/index.php?option=com_content",
            "http://hacked-site.com/cgi-bin/index.php?id=123&page=45&user=admin",
            "https://www.google.com",
            "http://bit.ly/2qczflx",
            "http://login-secure-verify.xyz/account/update",
            "https://www.facebook.com",
            "https://www.github.com",
            "http://paypal.com.secure-login.xyz/verify"
        ]
    
    # Initialize classifier
    try:
        classifier = EnhancedURLClassifier(MODEL_PATH)
        
        for url in test_urls:
            result = classifier.predict(url)
            
            print(f"\n{'='*60}")
            print(f"URL: {result['url']}")
            print(f"{'='*60}")
            print(f"Prediction: {result['prediction_label']}")
            print(f"Confidence: {result['confidence']:.1f}%")
            
            if result['overridden']:
                print(f"[!] OVERRIDDEN: Was {result['original_prediction']} ({result['original_confidence']:.1f}%)")
            
            print(f"\n📊 Probabilities:")
            for label, prob in result['probabilities'].items():
                bar = '█' * int(prob // 5)
                print(f"  {label:12} : {prob:5.1f}% {bar}")
            
            print(f"\n🔧 Key Features:")
            features = result['features']
            print(f"  URL Length: {features['url_len']}")
            print(f"  HTTPS: {'Yes' if features['https'] else 'No'}")
            print(f"  Query Params (?): {features['?']}")
            print(f"  Equals Signs (=): {features['=']}")
            print(f"  Dots (.): {features['.']}")
            print(f"  Digits: {features['digits']}")
            print(f"  Shortening Service: {'Yes' if features['Shortining_Service'] else 'No'}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()