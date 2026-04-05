import streamlit as st
import numpy as np
import torch
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor
from torchvision.transforms.functional import hflip, adjust_brightness

# ── Threshold ─────────────────────────────────────────────────
VIT_THRESHOLD = 0.5

# ── Load ViT ──────────────────────────────────────────────────
@st.cache_resource
def load_vit():
    name = "prithivMLmods/Deep-Fake-Detector-v2-Model"
    processor = ViTImageProcessor.from_pretrained(name)
    model = ViTForImageClassification.from_pretrained(name)
    model.eval()
    return processor, model

# ── Face crop ─────────────────────────────────────────────────
@st.cache_resource
def load_face_detector():
    from facenet_pytorch import MTCNN
    return MTCNN(keep_all=False, device="cpu")

def crop_face(image: Image.Image) -> Image.Image:
    try:
        mtcnn = load_face_detector()
        boxes, _ = mtcnn.detect(image)
        if boxes is not None:
            x1, y1, x2, y2 = [int(b) for b in boxes[0]]
            w, h = x2 - x1, y2 - y1
            x1 = max(0, x1 - int(w * 0.2))
            y1 = max(0, y1 - int(h * 0.2))
            x2 = min(image.width,  x2 + int(w * 0.2))
            y2 = min(image.height, y2 + int(h * 0.2))
            return image.crop((x1, y1, x2, y2))
    except Exception:
        pass
    return image  # fallback: full image

# ── Inference with TTA ────────────────────────────────────────
def _vit_single(processor, model, image: Image.Image) -> float:
    inputs = processor(images=image.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0]
    labels = model.config.id2label
    fake_idx = [i for i, l in labels.items() if "deep" in l.lower() or "fake" in l.lower()]
    return float(probs[fake_idx[0]]) if fake_idx else float(probs[1])

def run_vit(processor, model, image: Image.Image) -> float:
    img = crop_face(image)
    versions = [
        img,
        hflip(img),
        adjust_brightness(img, 0.9),
        adjust_brightness(img, 1.1),
    ]
    scores = [_vit_single(processor, model, v) for v in versions]
    return float(np.mean(scores))

# ── UI ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deepfake Detector — MenaCraft",
    page_icon="🔍",
    layout="centered"
)
st.title("🔍 Deepfake Detector")
st.markdown("Upload an image. The **ViT model** will classify it as real or deepfake.")
st.divider()

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "bmp"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    with st.spinner("Analyzing..."):
        proc, vit_model = load_vit()
        score = run_vit(proc, vit_model, image)

    if score >= VIT_THRESHOLD:
        verdict, color, confidence = "⚠️ DEEPFAKE", "red", score
    else:
        verdict, color, confidence = "✅ REAL", "green", 1.0 - score

    st.divider()
    st.markdown(f"### Verdict: :{color}[{verdict}]")
    st.metric("Confidence", f"{confidence * 100:.1f}%")
    st.progress(min(score, 1.0))

    st.divider()
    st.markdown("**Score breakdown**")
    st.write(f"P(Deepfake) = `{score:.4f}`")
    st.write(f"P(Real)     = `{1 - score:.4f}`")
    st.info("Model: ViT Deepfake Detector v2 | Face crop + TTA | 92% accuracy")
