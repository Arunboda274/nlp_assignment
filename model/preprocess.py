# ============================================================
# model/preprocess.py
#
# PURPOSE:
#   Validates and tokenizes user input before sending to model.
#   Also cleans and extracts the generated continuation after inference.
#
# WHY THIS FILE EXISTS:
#   Keeping preprocessing separate from generation makes the code
#   clean, testable, and reusable across local/TorchServe/SageMaker.
# ============================================================

import os
import sys
import torch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import MAX_INPUT_LENGTH, MIN_INPUT_LENGTH


def validate_input(prompt: str, temperature: float, max_new_tokens: int) -> dict:
    """
    Validate all user inputs before processing.

    Returns a dict:
      {"valid": True}                       if everything is OK
      {"valid": False, "error": "message"}  if something is wrong
    """

    # --- Check 1: Prompt must not be empty ---
    if not prompt or not prompt.strip():
        return {"valid": False, "error": "Story prompt cannot be empty. Please enter the beginning of your story."}

    # --- Check 2: Prompt must meet minimum length ---
    if len(prompt.strip()) < MIN_INPUT_LENGTH:
        return {
            "valid": False,
            "error": f"Story prompt is too short (minimum {MIN_INPUT_LENGTH} characters). Please write more."
        }

    # --- Check 3: Prompt must not exceed maximum length ---
    if len(prompt.strip()) > MAX_INPUT_LENGTH:
        return {
            "valid": False,
            "error": f"Story prompt is too long (maximum {MAX_INPUT_LENGTH} characters). Please shorten it."
        }

    # --- Check 4: Temperature must be a valid float ---
    try:
        temp = float(temperature)
    except (TypeError, ValueError):
        return {"valid": False, "error": "Temperature must be a number between 0.1 and 2.0."}

    if not (0.1 <= temp <= 2.0):
        return {"valid": False, "error": "Temperature must be between 0.1 and 2.0."}

    # --- Check 5: max_new_tokens must be a positive integer ---
    try:
        tokens = int(max_new_tokens)
    except (TypeError, ValueError):
        return {"valid": False, "error": "max_new_tokens must be a whole number (e.g., 100 or 250)."}

    if tokens < 20 or tokens > 500:
        return {"valid": False, "error": "max_new_tokens must be between 20 and 500."}

    return {"valid": True}


def tokenize_prompt(prompt: str, tokenizer, device):
    """
    Convert a text prompt into token IDs for the model.

    Example:
      "Once upon a time" → tensor([[1once, 2upon, 3a, 4time]])

    Args:
        prompt: the story prompt string
        tokenizer: loaded GPT2Tokenizer
        device: torch.device (cpu or cuda)

    Returns:
        input_ids: torch.Tensor of shape [1, sequence_length]
    """
    # Encode the prompt text to token IDs
    # return_tensors="pt" means return PyTorch tensors
    encoded = tokenizer.encode(
        prompt,
        return_tensors="pt",   # Return as PyTorch tensor
        truncation=True,       # Truncate if somehow too long
        max_length=512         # GPT2's maximum context window
    )

    # Move tensor to the same device as the model
    input_ids = encoded.to(device)
    return input_ids


def extract_continuation(generated_ids, input_ids, tokenizer):
    """
    After the model generates tokens, extract ONLY the new part
    (the continuation), not the original prompt.

    Why? The model returns: [original_prompt_tokens + new_tokens]
    We only want to show the user the [new_tokens] part.

    Args:
        generated_ids: tensor of all token IDs (prompt + continuation)
        input_ids: tensor of original prompt token IDs
        tokenizer: loaded GPT2Tokenizer

    Returns:
        continuation: string of only the generated continuation text
    """
    # Number of tokens in the original prompt
    prompt_length = input_ids.shape[1]

    # Slice out only the NEW tokens (after the prompt)
    new_token_ids = generated_ids[0][prompt_length:]

    # Decode token IDs back to text
    continuation = tokenizer.decode(
        new_token_ids,
        skip_special_tokens=True  # Remove [EOS], [PAD], etc.
    )

    # Clean up: strip leading/trailing whitespace
    continuation = continuation.strip()

    return continuation
