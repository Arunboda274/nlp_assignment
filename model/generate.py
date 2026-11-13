# ============================================================
# model/generate.py
#
# PURPOSE:
#   The main story generation module.
#   Ties together: model loading → preprocessing → inference → output.
#
# HOW GENERATION WORKS:
#   1. Tokenize the input prompt → get token ID tensor
#   2. Pass to model.generate() → get extended token ID tensor
#   3. Decode only the NEW tokens → return as string
#
# GENERATION PARAMETERS EXPLAINED:
#   do_sample=True         → Use sampling (not greedy/beam search)
#                            Greedy always picks the highest-prob token
#                            Sampling picks randomly from top candidates
#   temperature            → Controls randomness of sampling
#                            Low (0.3): focused, predictable output
#                            High (1.5): creative, unpredictable output
#   top_k=50               → Only sample from top 50 probable tokens
#   top_p=0.92             → Only sample from tokens covering 92% prob mass
#   max_new_tokens         → Maximum number of NEW tokens to generate
#   repetition_penalty=1.3 → Penalizes tokens that already appeared
#                            Prevents "the the the the..." repetition
# ============================================================

import os
import sys
import torch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import (
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    DEFAULT_REPETITION_PENALTY,
    SHORT_MAX_NEW_TOKENS,
    LONG_MAX_NEW_TOKENS,
)
from model.load_model import load_model_and_tokenizer
from model.preprocess import validate_input, tokenize_prompt, extract_continuation


# Module-level cache: model loaded once, reused for all requests
# This avoids reloading the 350 MB model on every generation call
_model = None
_tokenizer = None
_device = None


def get_model():
    """
    Returns the loaded model, tokenizer, and device.
    Uses module-level caching so the model is only loaded once
    per Python session (important for TorchServe and Streamlit).
    """
    global _model, _tokenizer, _device
    if _model is None:
        print("[INFO] First call — loading model into memory...")
        _model, _tokenizer, _device = load_model_and_tokenizer()
    return _model, _tokenizer, _device


def generate_story(
    prompt: str,
    length: str = "short",
    temperature: float = DEFAULT_TEMPERATURE,
    top_k: int = DEFAULT_TOP_K,
    top_p: float = DEFAULT_TOP_P,
    repetition_penalty: float = DEFAULT_REPETITION_PENALTY,
) -> dict:
    """
    Generate a story continuation for the given prompt.

    Args:
        prompt: The story beginning entered by the user.
        length: "short" (100 tokens) or "long" (250 tokens).
        temperature: Float between 0.1 and 2.0.
        top_k: Number of top tokens to consider (default 50).
        top_p: Cumulative probability threshold (default 0.92).
        repetition_penalty: Penalize repeated tokens (default 1.3).

    Returns:
        A dict with either:
          {"success": True,  "continuation": "...", "prompt": "..."}
          {"success": False, "error": "..."}
    """

    # --- Step 1: Determine number of tokens based on length ---
    if length.lower() == "long":
        max_new_tokens = LONG_MAX_NEW_TOKENS
    else:
        max_new_tokens = SHORT_MAX_NEW_TOKENS

    # --- Step 2: Validate all inputs ---
    validation = validate_input(prompt, temperature, max_new_tokens)
    if not validation["valid"]:
        return {"success": False, "error": validation["error"]}

    # --- Step 3: Load model (cached after first call) ---
    model, tokenizer, device = get_model()

    # --- Step 4: Tokenize the input prompt ---
    input_ids = tokenize_prompt(prompt.strip(), tokenizer, device)

    # --- Step 5: Generate continuation using PyTorch ---
    print(f"[INFO] Generating story... (length={length}, temperature={temperature})")

    try:
        with torch.no_grad():
            # torch.no_grad() saves memory by not computing gradients
            # (we don't need gradients — we're doing inference, not training)
            generated_ids = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,     # Only generate this many NEW tokens
                do_sample=True,                    # Use sampling (not greedy)
                temperature=temperature,           # Control creativity
                top_k=top_k,                       # Limit candidate tokens
                top_p=top_p,                       # Nucleus sampling
                repetition_penalty=repetition_penalty,  # Avoid repetition
                pad_token_id=tokenizer.eos_token_id,    # Silence padding warning
            )

    except Exception as e:
        return {"success": False, "error": f"Model generation failed: {str(e)}"}

    # --- Step 6: Extract only the new continuation text ---
    continuation = extract_continuation(generated_ids, input_ids, tokenizer)

    # --- Step 7: Handle edge case — empty continuation ---
    if not continuation or len(continuation.strip()) < 5:
        return {
            "success": False,
            "error": "The model generated an empty response. Try a different prompt or increase temperature."
        }

    print(f"[INFO] Generation complete! ({len(continuation.split())} words generated)")

    return {
        "success": True,
        "prompt": prompt.strip(),
        "continuation": continuation,
        "length": length,
        "temperature": temperature,
        "tokens_generated": max_new_tokens,
    }


# ============================================================
# QUICK TEST — Run this file directly:
#   python model/generate.py
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  AI Story Continuation System — Local Generation Test")
    print("=" * 60)

    # Test prompt
    test_prompt = "One day, a student discovered a mysterious box in the college library."

    print(f"\n📖 Story Prompt:\n   {test_prompt}\n")
    print("-" * 60)
    print("Generating continuation... (first run downloads ~350 MB)\n")

    result = generate_story(
        prompt=test_prompt,
        length="short",
        temperature=0.8
    )

    if result["success"]:
        print("✅ Generation Successful!\n")
        print(f"📖 Original Prompt:\n{result['prompt']}\n")
        print(f"✍️  Generated Continuation:\n{result['continuation']}\n")
        print(f"📊 Stats: {result['tokens_generated']} tokens | temperature={result['temperature']}")
    else:
        print(f"❌ Generation Failed: {result['error']}")
