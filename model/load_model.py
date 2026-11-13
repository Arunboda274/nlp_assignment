# ============================================================
# model/load_model.py
#
# PURPOSE:
#   Downloads DistilGPT2 from Hugging Face Hub (first run only)
#   and loads the model + tokenizer into memory using PyTorch.
#
# HOW IT WORKS:
#   - GPT2Tokenizer converts text → numbers (token IDs)
#   - GPT2LMHeadModel is the neural network that predicts next tokens
#   - torch.device selects CPU (we don't need GPU for this project)
# ============================================================

import os
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Import our shared settings
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import MODEL_NAME, MODEL_CACHE_DIR


def get_device():
    """
    Determine whether to run on GPU or CPU.
    For this college project, CPU is sufficient.
    Returns the appropriate torch.device.
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[INFO] GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("[INFO] Running on CPU (no GPU detected — this is fine!)")
    return device


def load_tokenizer():
    """
    Load the DistilGPT2 tokenizer.

    The tokenizer converts:
      Text  →  Token IDs  (for model input)
      Token IDs  →  Text  (to decode model output)

    First run: downloads ~0.5 MB from Hugging Face Hub.
    Subsequent runs: loads from local cache instantly.
    """
    print(f"[INFO] Loading tokenizer for '{MODEL_NAME}'...")

    tokenizer = GPT2Tokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=MODEL_CACHE_DIR
    )

    # GPT2 does not have a default pad token.
    # We set it to the end-of-sequence token to avoid warnings.
    tokenizer.pad_token = tokenizer.eos_token

    print("[INFO] Tokenizer loaded successfully.")
    return tokenizer


def load_model(device):
    """
    Load the pretrained DistilGPT2 language model.

    GPT2LMHeadModel is the full model with:
      - Transformer layers (attention + feed-forward)
      - A language model head (outputs probabilities for next token)

    First run: downloads ~350 MB from Hugging Face Hub.
    Subsequent runs: loads from local cache in ~2–5 seconds.

    Args:
        device: torch.device (cpu or cuda)

    Returns:
        model: the loaded PyTorch model in evaluation mode
    """
    print(f"[INFO] Loading model '{MODEL_NAME}'...")
    print("[INFO] First run will download ~350 MB. Please wait...")

    model = GPT2LMHeadModel.from_pretrained(
        MODEL_NAME,
        cache_dir=MODEL_CACHE_DIR
    )

    # Move the model to the selected device (CPU in our case)
    model = model.to(device)

    # Set to evaluation mode:
    # This disables dropout layers (used only during training).
    # Always do this before inference!
    model.eval()

    print(f"[INFO] Model loaded successfully on {device}.")
    return model


def load_model_and_tokenizer():
    """
    Convenience function: loads both model and tokenizer together.
    This is what other modules call — they don't need to know the details.

    Returns:
        model: GPT2LMHeadModel
        tokenizer: GPT2Tokenizer
        device: torch.device
    """
    device = get_device()
    tokenizer = load_tokenizer()
    model = load_model(device)
    return model, tokenizer, device


# ============================================================
# QUICK TEST — Run this file directly to verify model loading:
#   python model/load_model.py
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  Testing DistilGPT2 Model Loading")
    print("=" * 55)

    model, tokenizer, device = load_model_and_tokenizer()

    # Print model parameter count
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n[INFO] Model parameters: {total_params:,}")
    print(f"[INFO] Model size: ~{total_params * 4 / 1024 / 1024:.1f} MB")
    print("\n✅ Model and tokenizer loaded successfully!")
    print("   Ready for story generation.")
