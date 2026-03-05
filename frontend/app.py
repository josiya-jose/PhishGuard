import streamlit as st
import base64
from video_background import add_dark_bg_image
import streamlit.components.v1 as components

st.set_page_config(page_title="PhishGuard", page_icon="🛡️", layout="wide")

# ===================== LOGOUT HANDLER (must be first) =====================
if st.query_params.get("_logout") == "1":
    st.query_params.clear()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.rerun()

# CRITICAL: Check localStorage and restore session BEFORE anything else
def restore_session_from_storage():
    """Inject JavaScript to check localStorage and update session via hidden input"""
    restore_html = """
    <div id="session-restore" style="display:none;">
        <input type="hidden" id="user_id" />
        <input type="hidden" id="user_name" />
        <input type="hidden" id="page" />
    </div>
    <script>
    (function() {
        const userData = localStorage.getItem('phishguard_user');
        if (userData) {
            try {
                const user = JSON.parse(userData);
                document.getElementById('user_id').value = user.user_id || '';
                document.getElementById('user_name').value = user.user_name || '';
                document.getElementById('page').value = user.page || 'dashboard';
                
                // Signal Streamlit
                const event = new Event('input', { bubbles: true });
                document.getElementById('user_id').dispatchEvent(event);
            } catch (e) {
                console.error('Parse error:', e);
            }
        }
    })();
    </script>
    """
    components.html(restore_html, height=0)

# Call this FIRST
restore_session_from_storage()

# Initialize from query params if available (from localStorage restore)
query_params = st.query_params

if "logged_in" not in st.session_state:
    # Check if we have user_id in query params (means localStorage had data)
    if "user_id" in query_params:
        st.session_state.user_id = query_params.get("user_id", "")
        st.session_state.user_name = query_params.get("user_name", "User")
        st.session_state.logged_in = True
        st.session_state.page = query_params.get("page", "dashboard")
    else:
        st.session_state.logged_in = False
        st.session_state.page = "launch"

if "page" not in st.session_state:
    st.session_state.page = query_params.get("page", "launch")


def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


def go(page):
    st.session_state.page = page
    st.rerun()


# ===================== LAUNCH PAGE =====================
if st.session_state.page == "launch":
    add_dark_bg_image("assets/dynamic3.jpg")

    logo_base64 = get_base64_image("frontend/assets/logo.png")
    logo_html = (
        f"<img src='data:image/png;base64,{logo_base64}' class='brand-logo' alt='logo'>"
        if logo_base64 else "<span class='brand-emoji'>🛡️</span>"
    )

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    header[data-testid="stHeader"], footer, #MainMenu {{ display:none!important; }}
    html, body, .stApp {{ font-family:'DM Sans',sans-serif; overflow:hidden!important; }}
    .main .block-container {{
        padding:0!important; margin:0!important;
        max-width:100vw!important; background:transparent!important;
        height:100vh!important;
    }}

    .pg-scene {{
        position:fixed; inset:0;
        display:flex; align-items:center; justify-content:center;
        z-index:1; pointer-events:none;
    }}

    .pg-card {{
        position:relative;
        width:85vw; max-width:1300px;
        height:70vh; min-height:460px;
        border-radius:40px;
        background:rgba(255,255,255,0.03);
        backdrop-filter:blur(4px) saturate(110%);
        -webkit-backdrop-filter:blur(4px) saturate(110%);
        border:1px solid rgba(255,255,255,0.28);
        box-shadow:
            0 8px 56px rgba(0,0,0,0.38),
            inset 0 1px 0 rgba(255,255,255,0.22),
            0 0 20px rgba(140,80,255,0.4),
            0 0 60px rgba(140,80,255,0.2);
        display:flex; flex-direction:column;
        padding:44px 56px 48px;
        overflow:hidden;
    }}
    .pg-card::before {{
        content:""; position:absolute;
        top:0; left:10%; right:10%; height:1px;
        background:linear-gradient(90deg, transparent, rgba(255,255,255,0.55) 40%, rgba(255,255,255,0.55) 60%, transparent);
        pointer-events:none;
    }}
    .pg-card::after {{
        content:""; position:absolute; inset:0; border-radius:40px;
        background:linear-gradient(140deg, rgba(255,255,255,0.07) 0%, transparent 45%, rgba(255,255,255,0.03) 100%);
        pointer-events:none;
    }}

    .pg-nav {{
        display:flex; align-items:center; justify-content:space-between;
        flex-shrink:0; width:100%; z-index:2;
    }}
    .pg-brand {{ display:flex; align-items:center; gap:14px; }}
    .brand-logo {{
        width:50px; height:50px;
        filter:drop-shadow(0 2px 10px rgba(120,80,255,0.6));
        animation:pg-float 3.5s ease-in-out infinite;
    }}
    .brand-emoji {{ font-size:36px; animation:pg-float 3.5s ease-in-out infinite; }}
    @keyframes pg-float {{
        0%,100% {{ transform:translateY(0); }}
        50%      {{ transform:translateY(-9px); }}
    }}
    .pg-brand-name {{
        font-family:'Syne',sans-serif; font-size:30px; font-weight:700;
        color:#fff; text-shadow:0 2px 10px rgba(0,0,0,0.45);
    }}
    .pg-nav-links {{ display:flex; gap:32px; }}
    .pg-nav-link {{
        color:rgba(255,255,255,0.68); font-size:13px; font-weight:500;
        letter-spacing:0.07em; text-transform:uppercase;
    }}

    .pg-body {{
        flex:1; display:flex; flex-direction:column;
        justify-content:center;
        align-items:flex-start;
        max-width:65%; z-index:2; padding-bottom:4px;
    }}
    .pg-body h1 {{
        font-family:'Syne',sans-serif;
        font-size:clamp(22px,2.8vw,40px); font-weight:800;
        color:#fff; margin:0 0 16px; line-height:1.08;
        letter-spacing:-0.02em; text-shadow:0 3px 18px rgba(0,0,0,0.5);
    }}
    .pg-body p {{
        font-family:'DM Sans',sans-serif;
        font-size:14px; font-weight:300;
        color:rgba(255,255,255,0.72);
        margin:0 0 32px;
        line-height:1.7;
        letter-spacing:0.01em;
        max-width:520px;
    }}

    div[data-testid="stHorizontalBlock"] {{
        position: fixed !important;
        bottom: calc(15vh + 20px) !important;
        left: calc(7.5vw + 56px) !important;
        width: auto !important;
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 9999 !important;
        pointer-events: auto !important;
        background: transparent !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 0 0 172px !important;
        width: 172px !important;
        min-width: 172px !important;
        max-width: 172px !important;
        padding: 0 12px 0 0 !important;
        overflow: visible !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {{
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {{
        width: 100% !important;
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div > button,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] button {{
        border-radius: 50px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 15px !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: clip !important;
        cursor: pointer !important;
        line-height: 1.2 !important;
        width: 160px !important;
        min-width: 160px !important;
        max-width: 160px !important;
        height: 52px !important;
        min-height: 52px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.28s ease !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div > button,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button {{
        background: rgba(255,255,255,0.22) !important;
        color: #ffffff !important;
        border: 1.5px solid rgba(255,255,255,0.65) !important;
        font-weight: 700 !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.35) !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button:hover {{
        background: rgba(255,255,255,0.35) !important;
        border-color: rgba(255,255,255,0.95) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 36px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.45) !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) > div > button,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button {{
        background: rgba(255,255,255,0.08) !important;
        color: rgba(255,255,255,0.92) !important;
        border: 1.5px solid rgba(255,255,255,0.32) !important;
        font-weight: 500 !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button:hover {{
        background: rgba(255,255,255,0.20) !important;
        color: #fff !important;
        border-color: rgba(255,255,255,0.72) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.22) !important;
    }}

    div[data-testid="stHorizontalBlock"] button p {{
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: clip !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 15px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: inherit !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: inherit !important;
        line-height: 1.2 !important;
    }}

    div[data-testid="stStatusWidget"] {{ display:none!important; }}
    </style>

    <div class="pg-scene">
      <div class="pg-card">
        <div class="pg-nav">
          <div class="pg-brand">
            {logo_html}
            <span class="pg-brand-name">PhishGuard</span>
          </div>
          <div class="pg-nav-links">
            <span class="pg-nav-link">Home</span>
            <span class="pg-nav-link">About</span>
            <span class="pg-nav-link">Contact</span>
          </div>
        </div>
        <div class="pg-body">
          <h1>The Ultimate Guardian of Your Clicks.</h1>
          <p>We provide you with a seamless and dependable shield for total digital protection. Forget about suspicious links—we'll handle the security for your convenience.</p>
        </div>
      </div>
    </div>
    
    <script>
    // Auto-redirect to dashboard if logged in
    const userData = localStorage.getItem('phishguard_user');
    if (userData) {{
        try {{
            const user = JSON.parse(userData);
            if (user.user_id) {{
                window.location.href = '/?user_id=' + encodeURIComponent(user.user_id) + 
                                       '&user_name=' + encodeURIComponent(user.user_name) + 
                                       '&page=dashboard';
            }}
        }} catch(e) {{}}
    }}
    </script>
    """, unsafe_allow_html=True)

    col_login, col_signup = st.columns([1, 1])

    with col_login:
        if st.button("Login →", key="login_btn"):
            go("login")

    with col_signup:
        if st.button("Sign Up", key="signup_btn"):
            go("signup")


# ===================== OTHER PAGES =====================
elif st.session_state.page == "signup":
    add_dark_bg_image("assets/dynamic.jpg")
    import signup
    signup.show()

elif st.session_state.page == "login":
    add_dark_bg_image("assets/dynamic.jpg")
    import login
    login.show()

elif st.session_state.page == "dashboard":
    add_dark_bg_image("assets/dynamic_darker.jpg")
    
    # Redirect to login if not logged in
    if not st.session_state.logged_in:
        go("login")
    else:
        import dashboard
        dashboard.show()

elif st.session_state.page == "history":
    add_dark_bg_image("assets/dynamic_darker.jpg")
    
    # Redirect to login if not logged in
    if not st.session_state.logged_in:
        go("login")
    else:
        import history
        history.show()