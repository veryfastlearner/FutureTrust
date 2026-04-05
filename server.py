import sys
import re
import argparse
import joblib
import pandas as pd
import json
import os
from urllib.parse import urlparse
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import agent functions for credibility checking
from agent import analyze_input, MODEL, GROQ_API_KEY, TAVILY_API_KEY

# Import multi-layer architecture
from inspector import ContentInspector, get_inspector
from final_agent import FinalFrontierAgent, get_final_agent, synthesize_results

# Import bot detection (lazy loaded)
from botdetection import detect_profile_type

app = Flask(__name__)
CORS(app)

MODEL_PATH = "compressed_malicious_url_rf_model.pkl"

# Change this only if you are 100% sure your numeric labels map this way.
CLASS_LABELS = {
    0: "Benign",
    1: "Defacement",
    2: "Phishing",
    3: "Malware",
}

try:
    model = joblib.load(MODEL_PATH)
    print("[+] Model loaded successfully")
    print("[+] Model classes_:", getattr(model, "classes_", None))
except Exception as e:
    print(f"[-] Error loading model: {e}")
    model = None

FEATURE_NAMES = [
    "url_len",
    "@",
    "?",
    "-",
    "=",
    ".",
    "#",
    "%",
    "+",
    "$",
    "!",
    "*",
    ",",
    "//",
    "abnormal_url",
    "https",
    "digits",
    "letters",
    "Shortining_Service",
    "having_ip_address",
]


def normalize_url(url: str) -> str:
    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def Shortining_Service(url: str) -> int:
    match = re.search(
        r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
        r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
        r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
        r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|"
        r"db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|"
        r"q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|"
        r"x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
        r"tr\.im|link\.zip\.net",
        url,
        re.IGNORECASE,
    )
    return 1 if match else 0


def having_ip_address(url: str) -> int:
    match = re.search(
        r"(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\."
        r"([01]?\d\d?|2[0-4]\d|25[0-5])\/)|"
        r"(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\."
        r"([01]?\d\d?|2[0-4]\d|25[0-5])\/)|"
        r"((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)"
        r"(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|"
        r"([0-9]+(?:\.[0-9]+){3}:[0-9]+)|"
        r"((?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5])\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:\/\d{1,2})?)",
        url,
    )
    return 1 if match else 0


def abnormal_url(url: str) -> int:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return 1
    return 0


def extract_features(url: str) -> pd.DataFrame:
    features = {
        "url_len": len(url),
        "@": url.count("@"),
        "?": url.count("?"),
        "-": url.count("-"),
        "=": url.count("="),
        ".": url.count("."),
        "#": url.count("#"),
        "%": url.count("%"),
        "+": url.count("+"),
        "$": url.count("$"),
        "!": url.count("!"),
        "*": url.count("*"),
        ",": url.count(","),
        "//": url.count("//"),
        "abnormal_url": abnormal_url(url),
        "https": 1 if urlparse(url).scheme == "https" else 0,
        "digits": sum(c.isdigit() for c in url),
        "letters": sum(c.isalpha() for c in url),
        "Shortining_Service": Shortining_Service(url),
        "having_ip_address": having_ip_address(url),
    }
    return pd.DataFrame([features], columns=FEATURE_NAMES)


def get_prediction_label(prediction):
    try:
        prediction_int = int(prediction)
        return CLASS_LABELS.get(prediction_int, f"Class {prediction_int}")
    except Exception:
        return str(prediction)


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "status": "online",
            "message": "API is running. Send POST to /predict with {'url': 'https://example.com'}",
            "model_loaded": model is not None,
            "model_classes": [str(c) for c in getattr(model, "classes_", [])] if model is not None else [],
        }
    )


@app.route("/check-credibility", methods=["POST"])
def check_credibility():
    """Check credibility of content using agent.py logic"""
    if not GROQ_API_KEY or not TAVILY_API_KEY:
        return jsonify({"error": "Agent not configured. Check GROQ_API_KEY and TAVILY_API_KEY."}), 500
    
    data = request.get_json(silent=True)
    if not data or "input" not in data:
        return jsonify({"error": "Missing 'input' field in JSON payload."}), 400
    
    user_input = str(data["input"]).strip()
    input_type = data.get("type", "claim")  # claim, headline, url, post, article
    max_results = data.get("max_results", 6)
    
    if not user_input:
        return jsonify({"error": "Empty input provided."}), 400
    
    try:
        print(f"[CREDIBILITY] Analyzing: {user_input[:100]}...")
        print(f"[CREDIBILITY] Type: {input_type}")
        
        report = analyze_input(user_input, input_type, max_results)
        
        print(f"[CREDIBILITY] Verdict: {report.get('verdict')}")
        print(f"[CREDIBILITY] Score: {report.get('credibility_score')}")
        
        return jsonify({
            "input": user_input,
            "type": input_type,
            "verdict": report.get("verdict"),
            "credibility_score": report.get("credibility_score"),
            "confidence": report.get("confidence"),
            "summary": report.get("summary"),
            "red_flags": report.get("red_flags", []),
            "supporting_signals": report.get("supporting_signals", []),
            "recommended_action": report.get("recommended_action"),
            "sources": report.get("sources", []),
            "model_used": MODEL
        })
        
    except Exception as e:
        print(f"[CREDIBILITY ERROR] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/check-credibility-stream", methods=["POST"])
def check_credibility_stream():
    """Quick credibility check for URL content - combines URL safety + credibility"""
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL"}), 400
    
    url = str(data["url"]).strip()
    
    try:
        # First check URL safety with ML model
        url_result = None
        if model is not None:
            try:
                norm_url = normalize_url(url)
                if is_valid_url(norm_url):
                    features_df = extract_features(norm_url)
                    prediction = model.predict(features_df)[0]
                    probs = model.predict_proba(features_df)[0]
                    url_result = {
                        "prediction_class": int(prediction),
                        "prediction_label": get_prediction_label(prediction),
                        "confidence": max(probs) * 100
                    }
            except Exception as e:
                print(f"[URL CHECK ERROR] {e}")
        
        # Then check credibility of content at that URL
        credibility_result = None
        if GROQ_API_KEY and TAVILY_API_KEY:
            try:
                cred_report = analyze_input(url, "url", 4)
                credibility_result = {
                    "verdict": cred_report.get("verdict"),
                    "score": cred_report.get("credibility_score"),
                    "summary": cred_report.get("summary"),
                    "confidence": cred_report.get("confidence")
                }
            except Exception as e:
                print(f"[CREDIBILITY CHECK ERROR] {e}")
        
        # Override URL safety if agent is confident about content credibility
        final_url_result = url_result
        if url_result and credibility_result:
            cred_confidence = credibility_result.get("confidence", "low")
            cred_verdict = credibility_result.get("verdict", "unknown")
            
            # If agent is HIGHLY confident content is credible, trust benign URLs
            if cred_confidence == "high" and cred_verdict in ["credible", "mixed"]:
                if url_result["prediction_class"] in [2, 3]:  # Phishing or Malware
                    print(f"[OVERRIDE] Agent confident ({cred_confidence}) but URL model says {url_result['prediction_label']}")
                    final_url_result = {
                        "prediction_class": 0,  # Override to Benign
                        "prediction_label": "Benign",
                        "confidence": 100.0,
                        "overridden": True,
                        "override_reason": f"Agent {cred_confidence} confidence: {cred_verdict}"
                    }
            
            # If agent is HIGHLY confident content is false/doubtful, downgrade safe URLs
            elif cred_confidence == "high" and cred_verdict in ["false", "doubtful"]:
                if url_result["prediction_class"] == 0:  # Benign
                    print(f"[OVERRIDE] Agent {cred_confidence} confidence: {cred_verdict}")
                    final_url_result = {
                        "prediction_class": 2,  # Override to Phishing
                        "prediction_label": "Phishing", 
                        "confidence": 75.0,
                        "overridden": True,
                        "override_reason": f"Agent {cred_confidence} confidence: {cred_verdict}"
                    }
        
        return jsonify({
            "url": url,
            "url_safety": final_url_result,
            "content_credibility": credibility_result,
            "overall_risk": calculate_overall_risk(final_url_result, credibility_result)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def calculate_overall_risk(url_safety, credibility):
    """Calculate overall risk score combining URL safety and content credibility"""
    if not url_safety and not credibility:
        return "unknown"
    
    risk_score = 0
    factors = []
    
    # URL safety contributes 60%
    if url_safety:
        if url_safety["prediction_class"] == 0:  # Benign
            risk_score += 0
        elif url_safety["prediction_class"] == 1:  # Defacement
            risk_score += 30
            factors.append("Suspicious URL structure")
        elif url_safety["prediction_class"] == 2:  # Phishing
            risk_score += 50
            factors.append("Potential phishing URL")
        elif url_safety["prediction_class"] == 3:  # Malware
            risk_score += 60
            factors.append("Potential malware URL")
    
    # Content credibility contributes 40%
    if credibility:
        score = credibility.get("score", 50)
        verdict = credibility.get("verdict", "unknown")
        
        if verdict in ["false", "doubtful"]:
            risk_score += 40
            factors.append("Low credibility content")
        elif verdict == "insufficient_evidence":
            risk_score += 20
            factors.append("Unverifiable content")
        elif verdict == "mixed":
            risk_score += 15
        # credible = 0 risk
    
    # Determine overall risk
    if risk_score >= 50:
        return {"level": "high", "score": risk_score, "factors": factors}
    elif risk_score >= 25:
        return {"level": "medium", "score": risk_score, "factors": factors}
    else:
        return {"level": "low", "score": risk_score, "factors": factors}


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "model_loaded": model is not None,
            "model_classes": [str(c) for c in getattr(model, "classes_", [])] if model is not None else [],
            "agent_configured": GROQ_API_KEY is not None and TAVILY_API_KEY is not None,
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Check server logs."}), 500

    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL in JSON payload."}), 400

    try:
        raw_url = str(data["url"]).strip()
        url = normalize_url(raw_url)

        if not is_valid_url(url):
            return jsonify({"error": "Invalid URL format. Example: https://google.com"}), 400

        features_df = extract_features(url)
        prediction = model.predict(features_df)[0]
        probabilities = model.predict_proba(features_df)[0]

        model_classes = list(getattr(model, "classes_", []))
        if not model_classes:
            model_classes = [0, 1, 2, 3]

        probability_map = {}
        for cls, prob in zip(model_classes, probabilities):
            label = get_prediction_label(cls)
            probability_map[label] = round(float(prob) * 100, 2)

        predicted_label = get_prediction_label(prediction)

        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Model classes: {model_classes}")
        print(f"[DEBUG] Prediction raw: {prediction}")
        print(f"[DEBUG] Prediction label: {predicted_label}")
        print(f"[DEBUG] Features: {features_df.iloc[0].to_dict()}")
        print(f"[DEBUG] Probabilities: {probability_map}")

        return jsonify(
            {
                "url": url,
                "prediction_class": int(prediction) if str(prediction).isdigit() else str(prediction),
                "prediction_label": predicted_label,
                "model_classes": [str(c) for c in model_classes],
                "probabilities": probability_map,
                "features": features_df.iloc[0].to_dict(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze-content", methods=["POST"])
def analyze_content():
    """
    Multi-layer content analysis pipeline:
    Layer 1: Content Inspector - detects obvious red flags, URLs, accounts
    Layer 2: URL Safety Check (if URLs found) - RF model + agent verification
    Layer 3: Bot Detection (if accounts found) - profile analysis
    Layer 4: Final Frontier Agent - synthesizes all results with justification
    """
    data = request.get_json(silent=True)
    if not data or "content" not in data:
        return jsonify({"error": "Missing 'content' field"}), 400
    
    content = str(data["content"]).strip()
    if not content:
        return jsonify({"error": "Empty content"}), 400
    
    try:
        print(f"[MULTI-LAYER] Analyzing content: {content[:100]}...")
        
        # Initialize results
        layer_results = {
            "layer_1_inspector": None,
            "layer_2_url_check": None,
            "layer_3_bot_check": None,
            "layer_4_final_verdict": None
        }
        
        # ========== LAYER 1: CONTENT INSPECTOR ==========
        print("[LAYER 1] Running Content Inspector...")
        inspector = get_inspector()
        inspection = inspector.analyze(content)
        layer_results["layer_1_inspector"] = inspector.get_summary(inspection)
        
        # ========== LAYER 2: URL SAFETY CHECK (if needed) ==========
        url_result = None
        if inspection.needs_url_check and inspection.urls_found:
            print(f"[LAYER 2] Checking {len(inspection.urls_found)} URLs...")
            # Check first URL with our pipeline
            url = inspection.urls_found[0]
            url_result = check_url_pipeline(url)
            layer_results["layer_2_url_check"] = url_result
        
        # ========== LAYER 3: BOT DETECTION (if needed) ==========
        bot_result = None
        if inspection.needs_bot_check:
            print("[LAYER 3] Bot detection requested...")
            # Bot detection requires image - we'll note it but skip for text-only
            bot_result = {"note": "Bot detection requires profile image upload", "skipped": True}
            layer_results["layer_3_bot_check"] = bot_result
        
        # ========== LAYER 4: FINAL FRONTIER AGENT ==========
        print("[LAYER 4] Running Final Frontier Agent...")
        final_verdict = synthesize_results(
            inspector_result=layer_results["layer_1_inspector"],
            content=content,
            url_result=url_result,
            bot_result=bot_result
        )
        layer_results["layer_4_final_verdict"] = final_verdict
        
        print(f"[FINAL VERDICT] {final_verdict.get('verdict', 'unknown')} - {final_verdict.get('confidence', 'unknown')}")
        
        return jsonify({
            "content": content,
            "layers": layer_results,
            "final_verdict": final_verdict.get("verdict"),
            "final_confidence": final_verdict.get("confidence"),
            "final_summary": final_verdict.get("summary"),
            "recommendation": final_verdict.get("recommendation"),
            "risk_level": final_verdict.get("risk_level")
        })
        
    except Exception as e:
        print(f"[MULTI-LAYER ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def check_url_pipeline(url: str) -> dict:
    """Run URL through our safety pipeline"""
    result = {"url": url}
    
    # 1. ML Model check (if available)
    if model is not None:
        try:
            norm_url = normalize_url(url)
            if is_valid_url(norm_url):
                features_df = extract_features(norm_url)
                prediction = model.predict(features_df)[0]
                probs = model.predict_proba(features_df)[0]
                result["prediction_class"] = int(prediction)
                result["prediction_label"] = get_prediction_label(prediction)
                result["confidence"] = max(probs) * 100
        except Exception as e:
            print(f"[URL PIPELINE ERROR] {e}")
            result["model_error"] = str(e)
    
    # 2. Agent credibility check (if configured)
    if GROQ_API_KEY and TAVILY_API_KEY:
        try:
            from agent import analyze_input
            agent_report = analyze_input(url, "url", 4)
            result["agent_verdict"] = agent_report.get("verdict")
            result["agent_confidence"] = agent_report.get("confidence")
        except Exception as e:
            print(f"[URL AGENT ERROR] {e}")
            result["agent_error"] = str(e)
    
    return result


@app.route("/detect-bot", methods=["POST"])
def detect_bot():
    """Detect if a profile image is a bot, cyborg, real, or verified account"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Run detection
        result = detect_profile_type(image_bytes)
        
        return jsonify({
            "success": True,
            "filename": image_file.filename,
            "detection": result
        })
        
    except Exception as e:
        print(f"[BOT DETECTION ERROR] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Flask Server or test model")
    parser.add_argument("--test", type=str, help="Test a URL instantly in terminal")
    args = parser.parse_args()

    if args.test:
        if model is None:
            print("[-] FATAL: Cannot test, model did not load.")
            sys.exit(1)

        test_url = normalize_url(args.test)
        print(f"\n[+] Testing URL: {test_url}")

        if not is_valid_url(test_url):
            print("[-] Invalid URL")
            sys.exit(1)

        features = extract_features(test_url)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        model_classes = list(getattr(model, "classes_", [0, 1, 2, 3]))

        print("[+] Model classes:", model_classes)
        print("[+] Features:", features.iloc[0].to_dict())
        print("[+] Prediction raw:", prediction)
        print("[+] Prediction label:", get_prediction_label(prediction))
        print("[+] Probabilities:")
        for cls, prob in zip(model_classes, probabilities):
            print(f"    - {get_prediction_label(cls)}: {round(float(prob) * 100, 2)}%")
        sys.exit(0)

    print("Starting Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)