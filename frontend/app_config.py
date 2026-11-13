# ============================================================
# frontend/app_config.py
#
# PURPOSE:
#   Frontend-specific configuration.
#   Renamed from config.py to avoid name collision with config/settings.py
# ============================================================

import os
import sys

# Add project root to path
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from config.settings import (
    SHORT_MAX_NEW_TOKENS,
    LONG_MAX_NEW_TOKENS,
    DEFAULT_TEMPERATURE,
    MAX_INPUT_LENGTH,
    INFERENCE_MODE,
    TORCHSERVE_HOST,
    TORCHSERVE_PORT,
    TORCHSERVE_MODEL_NAME,
    SAGEMAKER_ENDPOINT_NAME,
    AWS_REGION,
)

# ---- App Identity ------------------------------------------
APP_TITLE       = "AI Story Continuation System"
APP_SUBTITLE    = "Powered by DistilGPT2 · PyTorch · Hugging Face"
APP_ICON        = "📖"
APP_LAYOUT      = "centered"

# ---- Continuation Length Labels ----------------------------
LENGTH_OPTIONS  = {"Short (~75 words)": "short", "Long (~190 words)": "long"}

# ---- Temperature Slider ------------------------------------
TEMPERATURE_MIN     = 0.1
TEMPERATURE_MAX     = 2.0
TEMPERATURE_DEFAULT = DEFAULT_TEMPERATURE
TEMPERATURE_STEP    = 0.1

# ---- Input Limits ------------------------------------------
MAX_CHARS = MAX_INPUT_LENGTH

# ---- Inference Mode ----------------------------------------
CURRENT_MODE = INFERENCE_MODE   # "local", "torchserve", or "sagemaker"

# ---- TorchServe Endpoint -----------------------------------
TORCHSERVE_URL = (
    f"http://{TORCHSERVE_HOST}:{TORCHSERVE_PORT}"
    f"/predictions/{TORCHSERVE_MODEL_NAME}"
)

# ---- Placeholder text for the input box --------------------
INPUT_PLACEHOLDER = (
    "Example: One day, a student discovered a mysterious box "
    "in the college library..."
)

# ---- Example prompts shown in sidebar ----------------------
EXAMPLE_PROMPTS = [
    "One day, a student discovered a mysterious box in the college library...",
    "A robot entered the classroom for the first time...",
    "It was a dark and rainy night when the lights went out...",
    "A young boy found a secret door behind his house...",
    "An astronaut landed on an unknown planet and saw...",
    "A girl received a mysterious letter with no return address...",
    "A scientist invented a machine that could travel through time...",
    "An old man discovered a hidden treasure in his backyard...",
    "A dog went missing in a small village and nobody knew why...",
    "A student woke up and discovered that nobody could see him...",
]
