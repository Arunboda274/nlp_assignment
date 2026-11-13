# ============================================================
# config/settings.py
# Shared configuration constants for the entire project.
# All other files import from here — change once, affects all.
# ============================================================

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# ---- Model Settings ----------------------------------------
# The pretrained model we use from Hugging Face Hub
MODEL_NAME = "distilgpt2"

# Local folder to cache the downloaded model (avoids re-downloading)
MODEL_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "model", "distilgpt2_local")

# ---- Generation Defaults -----------------------------------
# Short continuation: ~100 new tokens (~75 words)
SHORT_MAX_NEW_TOKENS = 100

# Long continuation: ~250 new tokens (~190 words)
LONG_MAX_NEW_TOKENS = 250

# Default temperature (0.1 = very focused, 2.0 = very creative)
DEFAULT_TEMPERATURE = 0.8

# Sampling settings for diverse, quality output
DEFAULT_TOP_K = 50          # Consider top 50 candidate tokens at each step
DEFAULT_TOP_P = 0.92        # Nucleus sampling: consider tokens covering 92% probability
DEFAULT_REPETITION_PENALTY = 1.3  # Penalize repeating the same words

# Maximum input prompt length (in characters) to prevent abuse
MAX_INPUT_LENGTH = 1000

# Minimum input prompt length (in characters)
MIN_INPUT_LENGTH = 10

# ---- Inference Mode ----------------------------------------
# "local"       → use model/generate.py directly (Phase 2-4)
# "torchserve"  → call local TorchServe API (Phase 6-7)
# "sagemaker"   → call AWS SageMaker endpoint (Phase 9+)
INFERENCE_MODE = os.getenv("INFERENCE_MODE", "local")

# ---- TorchServe Settings -----------------------------------
TORCHSERVE_HOST = os.getenv("TORCHSERVE_HOST", "localhost")
TORCHSERVE_PORT = int(os.getenv("TORCHSERVE_PORT", "8080"))
TORCHSERVE_MODEL_NAME = os.getenv("TORCHSERVE_MODEL_NAME", "story_generator")

# ---- AWS / SageMaker Settings ------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "ai-story-continuation-endpoint")
SAGEMAKER_ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN", "")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
