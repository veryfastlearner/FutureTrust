from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
import torch
import io
import os

# Model configuration
MODEL_NAME = "prithivMLmods/x-bot-profile-detection"

# Class mapping
ID2LABEL = {
    0: "bot",
    1: "cyborg",
    2: "real",
    3: "verified"
}

# Lazy-loaded model and processor
_model = None
_processor = None

def get_model():
    """Lazy load the model and processor."""
    global _model, _processor
    if _model is None:
        print("[+] Loading bot detection model...")
        _model = SiglipForImageClassification.from_pretrained(MODEL_NAME)
        _processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
        print("[+] Bot detection model loaded.")
    return _model, _processor

def detect_profile_type(image_input):
    """
    Detect profile type from image.
    
    Args:
        image_input: Can be:
            - PIL Image
            - File path (str)
            - Bytes/BytesIO
            - numpy array
    
    Returns:
        dict with predictions for each class and the top prediction
    """
    model, processor = get_model()
    
    # Handle different input types
    if isinstance(image_input, str):
        # File path
        image = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, bytes):
        # Bytes
        image = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif hasattr(image_input, 'read'):
        # File-like object (BytesIO)
        image = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        # PIL Image
        image = image_input.convert("RGB")
    else:
        # Assume numpy array (from Gradio/opencv)
        image = Image.fromarray(image_input).convert("RGB")
    
    # Process image
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
    
    # Build prediction result
    predictions = {
        ID2LABEL[i]: round(probs[i], 4) for i in range(len(probs))
    }
    
    # Get top prediction
    top_class = max(predictions, key=predictions.get)
    top_confidence = predictions[top_class]
    
    return {
        "predictions": predictions,
        "top_prediction": {
            "class": top_class,
            "confidence": top_confidence
        },
        "model": MODEL_NAME
    }

# Gradio interface (only when run directly)
if __name__ == "__main__":
    import gradio as gr
    
    def gradio_wrapper(image):
        result = detect_profile_type(image)
        return result["predictions"]
    
    iface = gr.Interface(
        fn=gradio_wrapper,
        inputs=gr.Image(type="numpy"),
        outputs=gr.Label(num_top_classes=4, label="Predicted Profile Type"),
        title="x-bot-profile-detection",
        description="Upload a social media profile picture to classify it as Bot, Cyborg, Real, or Verified using a SigLIP2 model."
    )
    iface.launch()
