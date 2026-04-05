import sys
import torch
from transformers import pipeline

MODEL_NAME = "CrabInHoney/urlbert-tiny-v4-malicious-url-classifier"

device = -1
if torch.cuda.is_available():
    device = 0

label_mapping = {
    "LABEL_0": "benign",
    "LABEL_1": "defacement",
    "LABEL_2": "malware",
    "LABEL_3": "phishing"
}

try:
    classifier = pipeline(
        "text-classification",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        device=device,
        top_k=None
    )
    print(f"[+] Loaded model: {MODEL_NAME}")
    print(f"[+] Device: {'GPU' if device == 0 else 'CPU'}")
except Exception as e:
    print(f"[-] Failed to load model: {e}")
    sys.exit(1)


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def test_url(url: str):
    url = normalize_url(url)
    results = classifier(url)[0]

    formatted = []
    for item in results:
        formatted.append({
            "label": label_mapping.get(item["label"], item["label"]),
            "score": round(float(item["score"]) * 100, 2)
        })

    formatted.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n[+] URL: {url}")
    print(f"[+] Top prediction: {formatted[0]['label']}")
    print("[+] Scores:")
    for row in formatted:
        print(f"    - {row['label']}: {row['score']}%")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python test_urlbert.py https://google.com")
        sys.exit(1)

    test_url(sys.argv[1])