# ============================================================
# frontend/app.py
#
# PURPOSE:
#   Main Streamlit application — the entry point for the UI.
#   Run with:  streamlit run frontend/app.py
#
# HOW IT CONNECTS TO THE BACKEND:
#   INFERENCE_MODE = "local"      → calls model/generate.py directly
#   INFERENCE_MODE = "torchserve" → sends HTTP POST to TorchServe API
#   INFERENCE_MODE = "sagemaker"  → sends request to SageMaker endpoint
#
#   Right now we use "local" mode (Phase 3-4).
#   We switch to "torchserve" in Phase 6, "sagemaker" in Phase 9.
# ============================================================

import os
import sys
import json
import requests
import streamlit as st

# ---- Make sure project root is in path --------------------
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(ROOT)

# ---- Import project modules --------------------------------
from frontend.app_config import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, APP_LAYOUT,
    LENGTH_OPTIONS, TEMPERATURE_MIN, TEMPERATURE_MAX,
    TEMPERATURE_DEFAULT, TEMPERATURE_STEP,
    MAX_CHARS, INPUT_PLACEHOLDER, EXAMPLE_PROMPTS,
    CURRENT_MODE, TORCHSERVE_URL,
)
from frontend.ui_components import (
    apply_custom_css, render_header, render_mode_badge,
    render_prompt_card, render_story_card, render_stats,
    render_error, render_success_badge, render_sidebar,
)

# ---- Streamlit page configuration -------------------------
# MUST be the first Streamlit call in the script
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)


# ============================================================
# BACKEND CONNECTOR FUNCTIONS
# These handle communication between UI and inference backend.
# ============================================================

@st.cache_resource(show_spinner=False)
def load_local_model():
    """
    Load the DistilGPT2 model ONCE and cache it.
    @st.cache_resource means Streamlit will only run this function
    once per session, even if the page is refreshed.
    """
    from model.generate import get_model
    return get_model()


def run_local_inference(prompt: str, length: str, temperature: float) -> dict:
    """
    Run story generation using local PyTorch model.
    Used in Phase 3 and 4 (INFERENCE_MODE = "local").
    """
    from model.generate import generate_story
    return generate_story(
        prompt=prompt,
        length=length,
        temperature=temperature,
    )


def run_torchserve_inference(prompt: str, length: str, temperature: float) -> dict:
    """
    Send request to local TorchServe server.
    Used in Phase 6 and 7 (INFERENCE_MODE = "torchserve").
    """
    from config.settings import SHORT_MAX_NEW_TOKENS, LONG_MAX_NEW_TOKENS

    max_new_tokens = SHORT_MAX_NEW_TOKENS if length == "short" else LONG_MAX_NEW_TOKENS

    payload = {
        "prompt": prompt,
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "length": length,
    }

    try:
        response = requests.post(
            TORCHSERVE_URL,
            json=payload,
            timeout=120,  # 2 minutes timeout for slow CPU inference
        )
        if response.status_code == 200:
            data = response.json()
            # TorchServe returns {"generated_text": "..."}
            continuation = data.get("generated_text", "")
            if continuation:
                return {
                    "success": True,
                    "prompt": prompt,
                    "continuation": continuation,
                    "length": length,
                    "temperature": temperature,
                    "tokens_generated": max_new_tokens,
                }
            else:
                return {"success": False, "error": "TorchServe returned an empty response."}
        else:
            return {
                "success": False,
                "error": f"TorchServe error (HTTP {response.status_code}): {response.text[:200]}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to TorchServe. Make sure it is running on localhost:8080."
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "TorchServe request timed out (>120s). Try a shorter length."}
    except Exception as e:
        return {"success": False, "error": f"TorchServe request failed: {str(e)}"}


def run_sagemaker_inference(prompt: str, length: str, temperature: float) -> dict:
    """
    Send request to Amazon SageMaker endpoint.
    Used in Phase 9+ (INFERENCE_MODE = "sagemaker").
    """
    import boto3
    from config.settings import SAGEMAKER_ENDPOINT_NAME, AWS_REGION, SHORT_MAX_NEW_TOKENS, LONG_MAX_NEW_TOKENS

    max_new_tokens = SHORT_MAX_NEW_TOKENS if length == "short" else LONG_MAX_NEW_TOKENS

    payload = {
        "prompt": prompt,
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "length": length,
    }

    try:
        client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
        response = client.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(payload),
        )
        result = json.loads(response["Body"].read().decode("utf-8"))
        continuation = result.get("generated_text", "")
        if continuation:
            return {
                "success": True,
                "prompt": prompt,
                "continuation": continuation,
                "length": length,
                "temperature": temperature,
                "tokens_generated": max_new_tokens,
            }
        else:
            return {"success": False, "error": "SageMaker endpoint returned an empty response."}
    except Exception as e:
        return {"success": False, "error": f"SageMaker inference failed: {str(e)}"}


def run_inference(prompt: str, length: str, temperature: float) -> dict:
    """
    Route inference to the correct backend based on INFERENCE_MODE.
    This is the single function the UI calls — it doesn't need to
    know which backend is being used.
    """
    if CURRENT_MODE == "torchserve":
        return run_torchserve_inference(prompt, length, temperature)
    elif CURRENT_MODE == "sagemaker":
        return run_sagemaker_inference(prompt, length, temperature)
    else:
        # Default: local mode
        return run_local_inference(prompt, length, temperature)


# ============================================================
# MAIN APP
# ============================================================

def main():
    # ── Apply custom CSS styling ─────────────────────────────
    apply_custom_css()

    # ── Sidebar with example prompts ─────────────────────────
    selected_example = render_sidebar(EXAMPLE_PROMPTS)

    # ── App header ────────────────────────────────────────────
    render_header(APP_TITLE, APP_SUBTITLE, APP_ICON)
    render_mode_badge(CURRENT_MODE)

    # ── Session state: persists values across Streamlit reruns ─
    # Streamlit reruns the whole script on every interaction.
    # st.session_state keeps values between reruns.
    if "prompt_text" not in st.session_state:
        st.session_state.prompt_text = ""
    if "result" not in st.session_state:
        st.session_state.result = None
    if "error_msg" not in st.session_state:
        st.session_state.error_msg = None

    # If user clicked a sidebar example, load it
    if selected_example:
        st.session_state.prompt_text = selected_example
        st.session_state.result = None
        st.session_state.error_msg = None

    # ── Story Input ───────────────────────────────────────────
    st.markdown('<div class="section-label">✍️ Begin Your Story</div>', unsafe_allow_html=True)

    prompt = st.text_area(
        label="Story Prompt",
        value=st.session_state.prompt_text,
        placeholder=INPUT_PLACEHOLDER,
        height=130,
        max_chars=MAX_CHARS,
        label_visibility="collapsed",
        key="prompt_input",
    )

    # Update session state when user types
    st.session_state.prompt_text = prompt

    # Character counter
    char_count = len(prompt)
    counter_color = "#ff4e50" if char_count > MAX_CHARS * 0.9 else "rgba(255,255,255,0.35)"
    st.markdown(
        f'<div style="text-align:right; font-size:0.75rem; color:{counter_color};">'
        f'{char_count} / {MAX_CHARS} characters</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Continuation Length & Temperature ─────────────────────
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="section-label">📏 Length</div>', unsafe_allow_html=True)
        length_label = st.radio(
            "Length",
            options=list(LENGTH_OPTIONS.keys()),
            index=0,
            label_visibility="collapsed",
        )
        length = LENGTH_OPTIONS[length_label]

    with col2:
        st.markdown('<div class="section-label">🌡️ Creativity (Temperature)</div>', unsafe_allow_html=True)
        temperature = st.slider(
            "Temperature",
            min_value=TEMPERATURE_MIN,
            max_value=TEMPERATURE_MAX,
            value=TEMPERATURE_DEFAULT,
            step=TEMPERATURE_STEP,
            label_visibility="collapsed",
            help="Low = focused & predictable | High = creative & unpredictable",
        )

        # Show descriptive label below the slider
        if temperature <= 0.4:
            temp_label = "🧊 Very focused"
        elif temperature <= 0.7:
            temp_label = "🎯 Balanced"
        elif temperature <= 1.0:
            temp_label = "🌟 Creative"
        elif temperature <= 1.4:
            temp_label = "🎨 Very creative"
        else:
            temp_label = "🎲 Experimental"

        st.markdown(
            f'<div style="font-size:0.8rem; color:rgba(255,255,255,0.5); margin-top:-0.5rem;">'
            f'{temp_label} (value: {temperature})</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Action Buttons ────────────────────────────────────────
    col_gen, col_clear = st.columns([3, 1])

    with col_gen:
        generate_clicked = st.button(
            "🚀 Generate Story Continuation",
            use_container_width=True,
        )

    with col_clear:
        clear_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
        )

    # Handle Clear button
    if clear_clicked:
        st.session_state.prompt_text = ""
        st.session_state.result = None
        st.session_state.error_msg = None
        st.rerun()

    # ── Generation Logic ─────────────────────────────────────
    if generate_clicked:
        st.session_state.result = None
        st.session_state.error_msg = None

        # Basic client-side validation before calling backend
        if not prompt.strip():
            st.session_state.error_msg = "Please enter the beginning of your story before generating."
        elif len(prompt.strip()) < 10:
            st.session_state.error_msg = "Your story prompt is too short. Please write at least 10 characters."
        else:
            # Preload model in local mode (shows spinner once)
            if CURRENT_MODE == "local":
                with st.spinner("⚙️ Loading AI model (first time only)..."):
                    load_local_model()

            # Run inference with animated spinner
            with st.spinner("✍️ Generating your story continuation... Please wait..."):
                result = run_inference(
                    prompt=prompt.strip(),
                    length=length,
                    temperature=temperature,
                )

            st.session_state.result = result
            if not result["success"]:
                st.session_state.error_msg = result.get("error", "Unknown error occurred.")

    # ── Display Results ───────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    # Show error if any
    if st.session_state.error_msg:
        render_error(st.session_state.error_msg)

    # Show story cards if generation was successful
    if st.session_state.result and st.session_state.result.get("success"):
        result = st.session_state.result

        st.markdown('<hr>', unsafe_allow_html=True)
        render_success_badge()

        # Original prompt card
        render_prompt_card(result["prompt"])
        st.markdown("<br>", unsafe_allow_html=True)

        # Generated continuation card
        render_story_card(result["continuation"])
        st.markdown("<br>", unsafe_allow_html=True)

        # Stats
        word_count = len(result["continuation"].split())
        render_stats(result["length"], result["temperature"], word_count)

        st.markdown("<br>", unsafe_allow_html=True)

        # Copy button (copies continuation to clipboard via text area)
        st.markdown('<div class="section-label">📋 Copy Your Story</div>', unsafe_allow_html=True)
        full_story = f"{result['prompt']}\n\n{result['continuation']}"
        st.text_area(
            "Full Story (select all and copy)",
            value=full_story,
            height=160,
            label_visibility="collapsed",
            key="copy_area",
        )

        # Try again with same prompt
        if st.button("🔄 Generate Again (Different Variation)", use_container_width=True):
            with st.spinner("✍️ Generating a new variation..."):
                new_result = run_inference(
                    prompt=result["prompt"],
                    length=result["length"],
                    temperature=result["temperature"],
                )
            st.session_state.result = new_result
            if not new_result["success"]:
                st.session_state.error_msg = new_result.get("error", "Unknown error.")
            st.rerun()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
