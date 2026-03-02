import streamlit as st
import base64
import requests

BACKEND_URL = "http://127.0.0.1:8000"

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def show():
    # ── Background ──
    try:
        bin_str = get_base64("frontend/assets/dynamic3.jpg")
        st.markdown(f"""<style>.stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}</style>""", unsafe_allow_html=True)
    except:
        pass

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap');

    header[data-testid="stHeader"], footer, #MainMenu { display:none!important; }

    .main .block-container {
        max-width: 100vw !important; padding: 0 !important;
        display: flex !important; justify-content: center !important;
        align-items: center !important; height: 100vh !important;
        background: transparent !important;
    }

    /* Glass card — taller to fit 3 inputs */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stMain"],
    section.main, .main, .main .block-container,
    .block-container {
        overflow: hidden !important;
        max-height: 100vh !important;
    }

    .signup-card-visual {
        position: fixed; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 420px; height: 660px; border-radius: 32px;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 25px 50px rgba(0,0,0,0.20);
        z-index: 0; pointer-events: none;
    }
    .signup-card-visual::before {
        content:""; position:absolute;
        top:0; left:12%; right:12%; height:1px;
        background:linear-gradient(90deg, transparent,
            rgba(255,255,255,0.55) 40%,
            rgba(255,255,255,0.55) 60%, transparent);
    }

    [data-testid="stVerticalBlock"] {
        width: 350px !important; margin: 0 auto !important; z-index: 10 !important;
    }

    .signup-header { text-align: center; margin-bottom: 22px; }
    .signup-header h1 {
        font-family:'Syne',sans-serif; font-size:25px;
        font-weight:800; color:white; margin:0;
    }
    .signup-header p { font-size:13px; color:rgba(255,255,255,0.58); margin-top:6px; }

    /* Input labels */
    div[data-testid="stTextInput"] label p {
        color:rgba(255,255,255,0.70)!important; font-size:11px!important;
        font-weight:600!important; letter-spacing:0.08em!important;
        text-transform:uppercase!important;
    }

    /* Input fields */
    div[data-testid="stTextInput"] input {
        background:rgba(255,255,255,0.10)!important;
        border:1px solid rgba(255,255,255,0.22)!important;
        border-radius:12px!important; color:white!important;
        font-size:15px!important; padding:13px 16px!important;
    }
    div[data-testid="stTextInput"] input::placeholder { color:rgba(255,255,255,0.32)!important; }
    div[data-testid="stTextInput"] input:focus {
        border-color:rgba(255,255,255,0.58)!important;
        background:rgba(255,255,255,0.15)!important;
        box-shadow:0 0 0 3px rgba(255,255,255,0.07)!important;
        outline:none!important;
    }

    /* Button base */
    div[data-testid="stButton"], div[data-testid="stButton"] button { width:100%!important; }
    div[data-testid="stButton"] button {
        border-radius:50px!important; font-weight:700!important;
        text-transform:uppercase!important; letter-spacing:1px!important;
        transition:all 0.25s ease!important; cursor:pointer!important;
    }
    div[data-testid="stButton"] button p {
        color:inherit!important; font-weight:700!important;
        text-transform:uppercase!important; white-space:nowrap!important; margin:0!important;
    }

    /* Create Account — solid white (primary) */
    div[data-testid="stButton"]:nth-of-type(1) button {
        height:52px!important; background:white!important;
        color:#1a1a2e!important; border:none!important;
        margin-top:18px!important; box-shadow:0 4px 20px rgba(0,0,0,0.25)!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p { color:#1a1a2e!important; }
    div[data-testid="stButton"]:nth-of-type(1) button:hover {
        transform:translateY(-2px)!important;
        box-shadow:0 8px 28px rgba(0,0,0,0.30)!important;
    }

    /* Back to Home — ghost (secondary) */
    div[data-testid="stButton"]:nth-of-type(2) button {
        height:44px!important; background:transparent!important;
        color:rgba(255,255,255,0.52)!important;
        border:1px solid rgba(255,255,255,0.22)!important;
        margin-top:10px!important; font-weight:500!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button:hover {
        background:rgba(255,255,255,0.08)!important; color:white!important;
        border-color:rgba(255,255,255,0.50)!important;
    }

    div[data-testid="stAlert"] {
        background:rgba(239,68,68,0.15)!important;
        border:1px solid rgba(239,68,68,0.35)!important;
        border-radius:12px!important; margin-bottom:8px!important;
    }
    div[data-testid="stStatusWidget"] { display:none!important; }
    </style>

    <div class="signup-card-visual"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="signup-header">
        <h1>Create Account</h1>
        <p>Join PhishGuard to stay protected.</p>
    </div>""", unsafe_allow_html=True)

    name     = st.text_input("Full Name", placeholder="John Doe",          key="signup_name")
    email    = st.text_input("Email",     placeholder="you@example.com",   key="signup_email")
    password = st.text_input("Password",  placeholder="••••••••", type="password", key="signup_pw")

    if st.session_state.get("signup_error"):
        st.error(st.session_state.signup_error)
    if st.session_state.get("signup_success"):
        st.success(st.session_state.signup_success)

    # ── Create Account ──
    if st.button("Create Account", key="create_btn", use_container_width=True):
        st.session_state.signup_error   = ""
        st.session_state.signup_success = ""
        if not name or not email or not password:
            st.session_state.signup_error = "Please fill in all fields."
        else:
            try:
                res = requests.post(
                    f"{BACKEND_URL}/signup",
                    json={"name": name, "email": email, "password": password},
                    timeout=5
                )
                if res.status_code == 200:
                    st.session_state.signup_success = "Account created! Redirecting to login..."
                    st.session_state.page = "login"
                else:
                    st.session_state.signup_error = res.text or "Signup failed. Please try again."
            except Exception:
                st.session_state.signup_error = "Cannot connect to server. Is the backend running?"

    # ── Back to Home ──
    if st.button("⬅ Back to Home", key="back_btn", use_container_width=True):
        st.session_state.signup_error   = ""
        st.session_state.signup_success = ""
        st.session_state.page = "launch"