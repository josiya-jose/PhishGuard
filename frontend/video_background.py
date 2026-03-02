import streamlit as st
import base64


def add_bg_image(image_path: str):
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    /* Target every possible Streamlit container */
    html {{
        background: url("data:image/png;base64,{data}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    body {{
        background: transparent !important;
    }}

    .stApp {{
        background: transparent !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
    }}

    [data-testid="stMain"] {{
        background: transparent !important;
    }}

    .main {{
        background: transparent !important;
    }}

    .block-container {{
        background: transparent !important;
    }}

    [data-testid="stHeader"] {{
        display: none !important;
    }}

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}


    # Find this line in video_background.py (around line 70)
    # Add AFTER the ::before background block:

    /* Dark overlay on top of image */
    [data-testid="stAppViewContainer"]::after {{
        content: "" !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: -998 !important;
        background-color: rgba(0, 0, 0, 0.2) !important;  /* ← Change this opacity (0.0-1.0) */
        pointer-events: none !important;
    }}


    /* Glassmorphism content area */
    .main .block-container {{
        backdrop-filter: blur(2px) !important;
        background-color: rgba(0, 0, 0, 0.15) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-top: 1rem !important;
    }}

    .stButton > button {{
        background: rgba(0, 0, 0, 0.55) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }}

    .stButton > button:hover {{
        background: rgba(0, 0, 0, 0.85) !important;
        border-color: #60a5fa !important;
        color: #60a5fa !important;
        transform: translateY(-2px) !important;
    }}

    input[type="text"],
    input[type="password"],
    input[type="email"],
    textarea,
    .stTextInput input {{
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: white !important;
    }}

    .stApp, .stApp p, .stApp span, .stApp label,
    .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp h5, .stApp h6,
    .stMarkdown {{
        color: white !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.7) !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background-color: rgba(10, 15, 30, 0.8) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def add_dark_bg_image(image_path: str):
    add_bg_image(image_path)