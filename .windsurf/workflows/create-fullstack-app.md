---
description: Create a simple fullstack URL classification app with Flask backend and React frontend
---

# Simple URL Scanner Fullstack App

This workflow creates a minimal fullstack application that uses the Flask ML API to classify URLs.

## Prerequisites

- Python 3.x with Flask, flask-cors, joblib, scikit-learn, pandas
- Node.js with npm

## Steps

### 1. Backend Setup (Flask)

The `server.py` should:
- Load the ML model
- Enable CORS for frontend access
- Have a `/predict` endpoint that accepts POST requests with `{"url": "..."}`
- Return `{"prediction_class": N}` where N is 0-3

Key requirements:
```python
from flask_cors import CORS
CORS(app)  # Enable CORS
```

### 2. Frontend Setup (React + Vite)

Create a minimal React component that:
- Has an input field for URL
- Sends POST request to `http://localhost:5000/predict`
- Displays the raw server response
- Shows class mapping (0=Benign, 1=Defacement, 2=Phishing, 3=Malware)

### 3. Running the App

Terminal 1 - Backend:
```bash
cd FutureTrust
python server.py
```

Terminal 2 - Frontend:
```bash
cd FutureTrust/frontend
npm run dev
```

### 4. Testing

1. Open browser to the Vite dev server URL (usually http://localhost:5173)
2. Enter a URL like `https://google.com`
3. Click Scan
4. View the prediction result

## Troubleshooting

- **"Failed to fetch"**: Make sure Flask server is running and CORS is enabled
- **"Model not loaded"**: Check that `compressed_malicious_url_rf_model.pkl` exists and scikit-learn is installed
- **All predictions are the same**: The feature extraction might not match the model's training data

## Class Reference

| Class | Name | Description |
|-------|------|-------------|
| 0 | Benign | Safe, normal URLs |
| 1 | Defacement | Hacked websites |
| 2 | Phishing | Fake login pages |
| 3 | Malware | Virus download links |
