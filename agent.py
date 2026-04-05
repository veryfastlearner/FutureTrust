#!/usr/bin/env python3

import os
import json
import argparse
import sys
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

# =========================
# CONFIG
# =========================
DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MAX_RESULTS = 6

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or os.getenv("tavily-api-key")
MODEL = (os.getenv("MODEL") or DEFAULT_MODEL).strip().strip("\"'")

# Fallback if MODEL is invalid (contains only numbers or slashes)
if MODEL.isdigit() or MODEL.startswith("meta-llama"):
    print(f"[!] Invalid MODEL in .env: '{MODEL}', using default: {DEFAULT_MODEL}")
    MODEL = DEFAULT_MODEL

if not GROQ_API_KEY:
    print("❌ Missing GROQ_API_KEY in .env")
    sys.exit(1)

if not TAVILY_API_KEY:
    print("❌ Missing TAVILY_API_KEY in .env")
    sys.exit(1)

if not MODEL:
    MODEL = DEFAULT_MODEL


# =========================
# CLIENTS
# =========================
groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


# =========================
# HELPERS
# =========================
def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to recover JSON block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass

    raise ValueError("Model did not return valid JSON")


def search_web(query: str, max_results: int = DEFAULT_MAX_RESULTS):
    result = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results
    )
    return result.get("results", [])


def build_sources_text(results):
    lines = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        domain = extract_domain(url)

        lines.append(
            f"""
SOURCE {i}
TITLE: {title}
DOMAIN: {domain}
URL: {url}
CONTENT:
{content}
""".strip()
        )
    return "\n\n".join(lines)


def ask_llm_for_report(user_input: str, input_type: str, web_results):
    sources_block = build_sources_text(web_results)

    system_prompt = """
You are a source-checking and credibility analysis agent.

Your task:
- Evaluate whether the user's input appears trustworthy.
- Use ONLY the supplied web evidence.
- Do not invent facts.
- Be careful with uncertainty.
- Distinguish between:
  - verified information
  - unsupported claims
  - suspicious indicators
  - mixed evidence

Return ONLY valid JSON with this exact structure:

{
  "input": "string",
  "input_type": "claim|headline|url|post|article",
  "verdict": "credible|mixed|doubtful|false|insufficient_evidence",
  "credibility_score": 0,
  "confidence": "low|medium|high",
  "summary": "string",
  "red_flags": ["string"],
  "supporting_signals": ["string"],
  "recommended_action": "string",
  "sources": [
    {
      "title": "string",
      "domain": "string",
      "url": "string",
      "stance": "supports|contradicts|context_only|unclear",
      "trust_score": 0,
      "notes": "string"
    }
  ]
}

Rules:
- credibility_score must be 0 to 100
- trust_score must be 0 to 100
- If evidence is weak, say insufficient_evidence or doubtful
- Keep summary concise
- Return JSON only
""".strip()

    user_prompt = f"""
INPUT:
{user_input}

INPUT_TYPE:
{input_type}

WEB_EVIDENCE:
{sources_block}
""".strip()

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content or "{}"
    return safe_json_loads(content)


def analyze_input(user_input: str, input_type: str, max_results: int):
    results = search_web(user_input, max_results=max_results)

    if not results:
        return {
            "input": user_input,
            "input_type": input_type,
            "verdict": "insufficient_evidence",
            "credibility_score": 0,
            "confidence": "low",
            "summary": "No web evidence was retrieved for this input.",
            "red_flags": ["No supporting evidence found."],
            "supporting_signals": [],
            "recommended_action": "Try a more specific query, paste the exact claim, or provide a direct URL.",
            "sources": []
        }

    report = ask_llm_for_report(user_input, input_type, results)
    return report


# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser(description="Credibility Agent using Groq + Tavily")
    parser.add_argument("--input", required=True, help="Claim, headline, URL, or article text to analyze")
    parser.add_argument(
        "--type",
        default="claim",
        choices=["claim", "headline", "url", "post", "article"],
        help="Type of user input"
    )
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS, help="Number of Tavily results")
    parser.add_argument("--output", default=None, help="Optional output JSON file")
    args = parser.parse_args()

    print("🛡️ Credibility Agent Started")
    print(f"Model: {MODEL}")
    print(f"Time: {datetime.utcnow().isoformat()}Z")
    print(f"Analyzing: {args.input}\n")

    try:
        report = analyze_input(args.input, args.type, args.max_results)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved report to {args.output}")


if __name__ == "__main__":
    main()