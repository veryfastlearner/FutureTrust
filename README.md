presentation_link:https://canva.link/bmrk6piv22m2ozo

please check the following branches:




ahmed for source credibility


bacem for missinformation checking agent



rayen for ai generation detection

# FutureTrust
because of lacking of trusting in ai generated content we see we decided to create a tool that focuses on content auth (fake or not) , decting missinformation, and checking sources
#architecture:
fact check agent, check missinfo agent, check source agent
all towards judge agent that will give confidence score


utureTrust is a multi-layered content authentication and misinformation detection platform. Built to address the growing concern over AI-generated fake news and untrustworthy content, FutureTrust combines classical Machine Learning with advanced LLM-based autonomous agents to evaluate the credibility of text, URLs, and social media profiles.

## Architecture & How It Works

FutureTrust uses a multi-staged pipeline to assess content:

1. **Content Inspector (Layer 1):** Scans input text for obvious red flags, extracts URLs, and identifies potential accounts.
2. **URL Safety Check (Layer 2):** Uses a trained Random Forest model (`compressed_malicious_url_rf_model.pkl`) to instantly predict if a URL is Benign, Defacement, Phishing, or Malware based on 20 extracted features.
3. **Bot Detection (Layer 3):** Analyzes profile images to determine if an account is a bot, cyborg, or a real user.
4. **Credibility Agent (Tavily + Groq):** Performs an in-depth fact-checking process by searching the web and applying LLM reasoning to determine if claims are credible, doubtful, or false.
5. **Final Frontier Agent (Layer 4):** Synthesizes the results from all previous layers and gives a final, readable verdict with clear justifications and a confidence score.

## Key Features

- **Multi-Layer Threat Analysis:** Fuses standard heuristic checks, ML threat detection, and advanced LLM reasoning.
- **URL Danger Detection:** Detects malicious links (Phishing, Malware) using a highly compressed Random Forest model.
- **Autonomous Agent Verification:** Uses Groq (LLMs) and Tavily (web search API) to verify claims in real-time.
- **Bot Profile Recognition:** Image-based analysis to identify fake accounts and bots.
- **Modern Tech Stack:** Flask/Python backend and Vite/React frontend.
- **Dockerized Setup:** Easily run the whole stack via `docker-compose`.

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended for easy setup)
- Node.js (if running frontend locally)
- Python 3.9+ (if running backend locally)
- API Keys: `GROQ_API_KEY` and `TAVILY_API_KEY` (needed in `.env` for Agent features to work)

### Running with Docker (Recommended)

1. Ensure your `.env` file in the root directory contains your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```
2. Build and start the services:
   ```bash
   docker-compose up --build
   ```
3. The Vite frontend will be available at `http://localhost:5174` and the Flask backend at `http://localhost:5000`.

### Running Locally without Docker

#### Backend
```bash
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Start Flask server
python server.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /analyze-content`: Runs the full 4-layer inspection on a piece of content.
- `POST /check-credibility`: Deep LLM fact-checking of claims and headlines.
- `POST /check-credibility-stream`: Fast URL safety check using ML, paired with an override mechanism by the Agent.
- `POST /detect-bot`: Upload a profile picture to determine account realness.
- `GET /health` & `GET /diagnose`: System health and model diagnostic info.

## Future Plans

- Enhancing the fact-checking capabilities by integrating more reliable source databases.
- Expanding bot detection to analyze user behavior over time.
- Adding browser extensions for real-time browsing protection.
