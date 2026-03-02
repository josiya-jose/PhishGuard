import streamlit as st
import streamlit.components.v1 as components
import base64
import requests

BACKEND_URL = "http://127.0.0.1:8000"

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def save_login_to_storage(user_id, user_name, page="dashboard"):
    """Save login state to localStorage"""
    components.html(f"""
    <script>
    localStorage.setItem('phishguard_user', JSON.stringify({{
        user_id: '{user_id}',
        user_name: '{user_name}',
        page: '{page}'
    }}));
    </script>
    """, height=0)

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
    .login-card-visual {
        position: fixed; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 420px; height: 520px; border-radius: 32px;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 25px 50px rgba(0,0,0,0.20);
        z-index: 0; pointer-events: none;
    }
    .login-card-visual::before {
        content:""; position:absolute;
        top:0; left:12%; right:12%; height:1px;
        background:linear-gradient(90deg, transparent, rgba(255,255,255,0.55) 40%, rgba(255,255,255,0.55) 60%, transparent);
    }
    [data-testid="stVerticalBlock"] {
        width: 350px !important; margin: 0 auto !important; z-index: 10 !important;
    }
    .login-header { text-align: center; margin-bottom: 22px; }
    .login-header h1 { font-family:'Syne',sans-serif; font-size:30px; font-weight:800; color:white; margin:0; }
    .login-header p { font-size:13px; color:rgba(255,255,255,0.58); margin-top:6px; }
    div[data-testid="stTextInput"] label p {
        color:rgba(255,255,255,0.70)!important; font-size:11px!important;
        font-weight:600!important; letter-spacing:0.08em!important; text-transform:uppercase!important;
    }
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
        box-shadow:0 0 0 3px rgba(255,255,255,0.07)!important; outline:none!important;
    }
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
    div[data-testid="stButton"]:nth-of-type(1) button {
        height:52px!important; background:white!important; color:#1a1a2e!important;
        border:none!important; margin-top:18px!important;
        box-shadow:0 4px 20px rgba(0,0,0,0.25)!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p { color:#1a1a2e!important; }
    div[data-testid="stButton"]:nth-of-type(1) button:hover {
        transform:translateY(-2px)!important; box-shadow:0 8px 28px rgba(0,0,0,0.30)!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button {
        height:44px!important; background:transparent!important;
        color:rgba(255,255,255,0.52)!important;
        border:1px solid rgba(255,255,255,0.22)!important; margin-top:10px!important;
        font-weight:500!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button:hover {
        background:rgba(255,255,255,0.08)!important; color:white!important;
        border-color:rgba(255,255,255,0.50)!important;
    }
    div[data-testid="stStatusWidget"] { display:none!important; }
    </style>
    <div class="login-card-visual"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-header">
        <h1>Hello Again!</h1>
        <p>Welcome back — let's keep you safe.</p>
    </div>""", unsafe_allow_html=True)

    email    = st.text_input("Email",    placeholder="you@example.com",  key="login_email")
    password = st.text_input("Password", placeholder="••••••••", type="password", key="login_pw")

    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)

    # ── Sign In ──────────────────────────────────────
    if st.button("Sign In →", key="signin_btn", use_container_width=True):
        st.session_state.login_error = ""
        if not email or not password:
            st.session_state.login_error = "Please enter your email and password."
            st.rerun()
        else:
            try:
                res = requests.post(
                    f"{BACKEND_URL}/login",
                    json={"email": email, "password": password},
                    timeout=5
                )
                if res.status_code == 200:
                    data = res.json()
                    user_id = data.get("user_id", "")
                    user_name = data.get("name", "User")
                    
                    # Save to localStorage
                    st.markdown(f"""
                    <script>
                    localStorage.setItem('phishguard_user', JSON.stringify({{
                        user_id: '{user_id}',
                        user_name: '{user_name}',
                        page: 'dashboard'
                    }}));
                    // Redirect with query params
                    window.location.href = '/?user_id=' + encodeURIComponent('{user_id}') + 
                                           '&user_name=' + encodeURIComponent('{user_name}') + 
                                           '&page=dashboard';
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # Also update session state
                    st.session_state.user_id   = user_id
                    st.session_state.user_name = user_name
                    st.session_state.logged_in = True
                    st.session_state.page      = "dashboard"
                else:
                    st.session_state.login_error = "Invalid email or password."
                    st.rerun()
            except Exception:
                st.session_state.login_error = "Cannot connect to server. Is the backend running?"
                st.rerun()

    # ── Back to Home ─────────────────────────────────
    if st.button("⬅ Back to Home", key="back_btn", use_container_width=True):
        st.session_state.login_error = ""
        st.session_state.page = "launch"
        st.rerun()