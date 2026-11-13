# ============================================================
# frontend/ui_components.py
#
# PURPOSE:
#   Reusable UI building blocks for the Streamlit app.
#   Keeps app.py clean by moving styling and components here.
# ============================================================

import streamlit as st


def apply_custom_css():
    """
    Inject custom CSS to make the UI attractive and modern.
    Streamlit allows raw HTML/CSS via st.markdown with unsafe_allow_html=True.
    """
    st.markdown("""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App background ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* ── Main content area ── */
    .main .block-container {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 2.5rem 2.5rem;
        margin-top: 1rem;
        max-width: 820px;
    }

    /* ── App Title ── */
    .app-title {
        font-family: 'Merriweather', serif;
        font-size: 2.4rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #f9d423, #ff4e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.55);
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        margin-bottom: 1.8rem;
    }

    /* ── Section labels ── */
    .section-label {
        color: rgba(255,255,255,0.75);
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    /* ── Text area override — dark background, light text ── */
    .stTextArea textarea,
    div[data-testid="stTextArea"] textarea,
    textarea {
        background-color: #1a1535 !important;
        color: #f0e6ff !important;
        border: 1.5px solid rgba(249,212,35,0.35) !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-family: 'Merriweather', serif !important;
        caret-color: #f9d423 !important;
    }
    .stTextArea textarea:focus,
    div[data-testid="stTextArea"] textarea:focus,
    textarea:focus {
        background-color: #1a1535 !important;
        color: #f0e6ff !important;
        border-color: #f9d423 !important;
        box-shadow: 0 0 0 2px rgba(249,212,35,0.25) !important;
        outline: none !important;
    }
    /* Wrapper div that Streamlit puts around textarea */
    .stTextArea > div,
    div[data-testid="stTextArea"] > div {
        background-color: #1a1535 !important;
        border-radius: 12px !important;
    }
    /* Placeholder text color */
    .stTextArea textarea::placeholder,
    textarea::placeholder {
        color: rgba(200, 180, 240, 0.4) !important;
        font-style: italic !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #f9d423, #ff4e50);
        color: #1a1a2e;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 50px;
        padding: 0.6rem 1.5rem;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255,78,80,0.4);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ── Slider ── */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #f9d423, #ff4e50) !important;
    }

    /* ── Generated story card ── */
    .story-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(249,212,35,0.3);
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        margin-top: 0.8rem;
        font-family: 'Merriweather', serif;
        font-size: 1rem;
        line-height: 1.9;
        color: rgba(255,255,255,0.90);
    }

    /* ── Prompt card ── */
    .prompt-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        margin-top: 0.8rem;
        font-family: 'Merriweather', serif;
        font-size: 0.95rem;
        line-height: 1.8;
        color: rgba(255,255,255,0.65);
        font-style: italic;
    }

    /* ── Card headers ── */
    .card-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .card-header-prompt { color: rgba(255,255,255,0.4); }
    .card-header-story  { color: #f9d423; }

    /* ── Stats bar ── */
    .stats-bar {
        display: flex;
        gap: 1.2rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    .stat-pill {
        background: rgba(255,255,255,0.08);
        border-radius: 50px;
        padding: 0.3rem 0.9rem;
        font-size: 0.78rem;
        color: rgba(255,255,255,0.6);
    }

    /* ── Error / warning box ── */
    .error-box {
        background: rgba(255,78,80,0.12);
        border: 1px solid rgba(255,78,80,0.4);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #ff6b6b;
        font-size: 0.9rem;
    }

    /* ── Success badge ── */
    .success-badge {
        display: inline-block;
        background: rgba(0,230,118,0.15);
        border: 1px solid rgba(0,230,118,0.4);
        border-radius: 50px;
        padding: 0.2rem 0.8rem;
        color: #00e676;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* ── Mode badge (top right) ── */
    .mode-badge {
        text-align: right;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.35);
        margin-bottom: 1.5rem;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f9d423 !important;
    }

    /* ── Radio buttons (Short/Long) ── */
    [data-testid="stRadio"] label {
        color: rgba(255,255,255,0.8) !important;
    }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.1) !important; }

    /* ── Spinner text ── */
    [data-testid="stSpinner"] p { color: #f9d423 !important; }

    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str):
    """Render the app title and subtitle."""
    st.markdown(f'<div class="app-title">{icon} {title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_mode_badge(mode: str):
    """Show the current inference mode (local / torchserve / sagemaker)."""
    labels = {
        "local":       "🖥️  Mode: Local PyTorch",
        "torchserve":  "⚙️  Mode: TorchServe",
        "sagemaker":   "☁️  Mode: Amazon SageMaker",
    }
    text = labels.get(mode, f"Mode: {mode}")
    st.markdown(f'<div class="mode-badge">{text}</div>', unsafe_allow_html=True)


def render_prompt_card(prompt: str):
    """Display the original user prompt in a styled card."""
    st.markdown(
        f'<div class="card-header card-header-prompt">📝 Your Story Prompt</div>'
        f'<div class="prompt-card">{prompt}</div>',
        unsafe_allow_html=True,
    )


def render_story_card(continuation: str):
    """Display the generated story continuation in a styled card."""
    st.markdown(
        f'<div class="card-header card-header-story">✨ Generated Continuation</div>'
        f'<div class="story-card">{continuation}</div>',
        unsafe_allow_html=True,
    )


def render_stats(length: str, temperature: float, word_count: int):
    """Show generation statistics as small pills."""
    st.markdown(
        f'<div class="stats-bar">'
        f'<span class="stat-pill">📏 {length.capitalize()} continuation</span>'
        f'<span class="stat-pill">🌡️ Temperature: {temperature}</span>'
        f'<span class="stat-pill">📊 ~{word_count} words generated</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_error(message: str):
    """Display an error message in a styled box."""
    st.markdown(
        f'<div class="error-box">⚠️ {message}</div>',
        unsafe_allow_html=True,
    )


def render_success_badge():
    """Show a small 'Generation Successful' badge."""
    st.markdown(
        '<div class="success-badge">✅ Generation Successful</div>',
        unsafe_allow_html=True,
    )


def render_sidebar(example_prompts: list) -> str | None:
    """
    Render the sidebar with example prompts and instructions.
    Returns the selected example prompt string, or None.
    """
    with st.sidebar:
        st.markdown("## 📚 Example Prompts")
        st.markdown("Click any prompt below to load it:")
        st.markdown("---")

        selected = None
        for i, prompt in enumerate(example_prompts, 1):
            # Show a truncated label on the button
            label = f"{i}. {prompt[:45]}..."
            if st.button(label, key=f"example_{i}"):
                selected = prompt

        st.markdown("---")
        st.markdown("## 🌡️ Temperature Guide")
        st.markdown("""
| Value | Effect |
|-------|--------|
| 0.1–0.4 | Focused, predictable |
| 0.5–0.8 | Balanced (recommended) |
| 0.9–1.3 | Creative, varied |
| 1.4–2.0 | Experimental, random |
        """)

        st.markdown("---")
        st.markdown("## ℹ️ About")
        st.markdown("""
**Model:** DistilGPT2  
**Framework:** PyTorch  
**Tokenizer:** Hugging Face  
**UI:** Streamlit  
        """)

    return selected
