import streamlit as st
import streamlit.components.v1 as components
import requests
import time
from datetime import datetime
import json
import calendar as cal_module

BACKEND_URL = "http://127.0.0.1:8000"


def build_results_html(prediction, confidence, risk_score, risk_level, shap_data):

    # ================== COLOR LOGIC ==================
    if prediction.lower() in ("safe", "legitimate"):
        pred_color, pred_arrow = "#34d399", "↓"
    elif prediction.lower() == "suspicious":
        pred_color, pred_arrow = "#fbbf24", "↑"
    else:
        pred_color, pred_arrow = "#f87171", "↑"

    if risk_level == "Low Risk":
        risk_color = "#34d399"
    elif risk_level == "Medium Risk":
        risk_color = "#fbbf24"
    else:
        risk_color = "#f87171"

    # ================== DATE & CALENDAR ==================
    now = datetime.now()
    month_name = now.strftime("%b").upper()
    today_day  = now.day
    today_str  = now.strftime("%d %b %Y")
    month_cal  = cal_module.monthcalendar(now.year, now.month)

    days_hdr = "".join(f'<div class="dn">{d}</div>' for d in ["MO","TU","WE","TH","FR","SA","SU"])
    cells = ""
    for week in month_cal:
        for d in week:
            if d == 0:
                cells += '<div class="dc"></div>'
            elif d == today_day:
                cells += f'<div class="dc today">{d}</div>'
            else:
                cells += f'<div class="dc">{d}</div>'

    # ================== SHAP ==================
    sorted_shap = sorted(shap_data, key=lambda x: abs(x["shap_value"]), reverse=True)[:9]
    total = sum(abs(x["shap_value"]) for x in sorted_shap) or 1
    threats = [{"name": x["feature"].replace("_"," "), "pct": round(abs(x["shap_value"])/total*100), "high": x["shap_value"]>0} for x in sorted_shap]
    tj = json.dumps(threats)

    # ================== VALUE FIX ==================
    # Confidence comes as 0-1 -> convert to percentage
    conf_percent = round(float(confidence) * 100, 2)
    # Risk score already 0-100 from backend
    risk_percent = round(float(risk_score), 2)

    conf_val  = conf_percent
    rs_val    = risk_percent
    conf_full = conf_percent
    rs_full   = risk_percent
    risk_short = risk_level.replace(" Risk","")

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'DM Sans',sans-serif;color:#fff;background:transparent;padding:0 0 20px;}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}}
.sc{{background:rgba(255,255,255,0.058);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:16px;border:1px solid rgba(255,255,255,0.10);box-shadow:0 4px 20px rgba(0,0,0,0.25),inset 0 1px 0 rgba(255,255,255,0.10);padding:18px 18px 0;position:relative;overflow:hidden;min-height:128px;display:flex;flex-direction:column;transition:transform 0.25s ease,box-shadow 0.25s ease;}}
.sc:hover{{transform:translateY(-4px);box-shadow:0 14px 36px rgba(0,0,0,0.32);}}
.sc-label{{font-size:10px;font-weight:700;color:rgba(255,255,255,0.40);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;}}
.sc-row{{display:flex;align-items:center;justify-content:space-between;flex:1;}}
.sc-val{{font-family:'Syne',sans-serif;font-size:30px;font-weight:800;line-height:1;}}
.sc-arrow{{font-size:20px;opacity:0.80;}}
.sc-sub-row{{display:flex;align-items:center;justify-content:space-between;margin:6px 0 12px;}}
.sc-sub{{font-size:9px;color:rgba(255,255,255,0.28);letter-spacing:0.10em;text-transform:uppercase;}}
.sc-pct{{font-size:9px;font-weight:700;color:rgba(255,255,255,0.40);background:rgba(255,255,255,0.08);padding:2px 7px;border-radius:20px;}}
.sc-bar{{position:absolute;bottom:0;left:0;right:0;height:3px;border-radius:0 0 16px 16px;}}
.bottom{{display:grid;grid-template-columns:1fr 290px;gap:14px;align-items:start;}}
.tc{{background:rgba(255,255,255,0.050);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:18px;border:1px solid rgba(255,255,255,0.09);box-shadow:0 4px 22px rgba(0,0,0,0.22),inset 0 1px 0 rgba(255,255,255,0.08);overflow:hidden;position:relative;}}
.tc::before{{content:"";position:absolute;top:0;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(167,139,250,0.5) 50%,transparent);}}
.tc-head{{padding:18px 20px 12px;border-bottom:1px solid rgba(255,255,255,0.055);}}
.tc-title{{font-family:'Syne',sans-serif;font-size:15px;font-weight:800;color:#fff;margin-bottom:2px;}}
.tc-sub{{font-size:10px;color:rgba(255,255,255,0.30);margin-bottom:8px;}}
.leg{{display:flex;gap:14px;}}
.leg-d{{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:4px;vertical-align:middle;}}
.leg-l{{font-size:10px;color:rgba(255,255,255,0.45);font-weight:600;letter-spacing:0.07em;text-transform:uppercase;}}
.tc-body{{display:flex;align-items:center;justify-content:center;padding:10px 0 14px;min-height:460px;}}
.ow{{position:relative;width:370px;height:370px;flex-shrink:0;}}
.or1{{position:absolute;inset:0;border-radius:50%;border:1.5px dashed rgba(167,139,250,0.20);}}
.or2{{position:absolute;inset:54px;border-radius:50%;border:1px dashed rgba(167,139,250,0.08);}}
.otick{{position:absolute;inset:-8px;border-radius:50%;border-top:2px solid rgba(167,139,250,0.38);border-right:2px solid transparent;border-bottom:2px solid transparent;border-left:2px solid transparent;animation:spin 7s linear infinite;}}
@keyframes spin{{to{{transform:rotate(360deg);}}}}
.cn{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:98px;height:98px;border-radius:50%;background:radial-gradient(circle at 38% 32%,rgba(124,58,237,0.92),rgba(28,10,75,0.97));border:1.5px solid rgba(167,139,250,0.48);box-shadow:0 0 28px rgba(124,58,237,0.32),inset 0 1px 0 rgba(255,255,255,0.18);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:10;text-align:center;padding:8px;animation:cpulse 3s ease-in-out infinite;cursor:default;}}
@keyframes cpulse{{0%,100%{{box-shadow:0 0 20px rgba(124,58,237,0.25);}}50%{{box-shadow:0 0 46px rgba(124,58,237,0.52);}}}}
.cn-pct{{font-family:'Syne',sans-serif;font-size:19px;font-weight:800;color:#fff;line-height:1;}}
.cn-lbl{{font-size:8px;color:rgba(255,255,255,0.50);text-transform:uppercase;letter-spacing:0.05em;margin-top:4px;line-height:1.3;}}
.bub{{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 30%,rgba(109,40,217,0.88),rgba(22,7,62,0.96));border:1px solid rgba(167,139,250,0.32);box-shadow:0 0 12px rgba(124,58,237,0.18),inset 0 1px 0 rgba(255,255,255,0.12);display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;transition:box-shadow 0.22s,border-color 0.22s,transform 0.18s;text-align:center;padding:5px;}}
.bub:hover{{box-shadow:0 0 28px rgba(167,139,250,0.55),inset 0 1px 0 rgba(255,255,255,0.22);border-color:rgba(167,139,250,0.80);transform:translate(-50%,-50%) scale(1.13) !important;z-index:20;}}
.bp{{font-family:'Syne',sans-serif;font-weight:800;color:#fff;line-height:1;}}
.ba{{font-size:7px;vertical-align:super;margin-left:1px;}}
.bn{{font-size:7px;color:rgba(255,255,255,0.55);margin-top:2px;line-height:1.2;}}
.conn{{position:absolute;top:50%;left:50%;transform-origin:0 0;height:1px;background:linear-gradient(90deg,rgba(167,139,250,0.15),transparent);pointer-events:none;z-index:1;}}
.rc{{display:flex;flex-direction:column;gap:13px;}}
.cal{{background:rgba(255,255,255,0.055);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:18px;border:1px solid rgba(255,255,255,0.09);box-shadow:0 4px 22px rgba(0,0,0,0.22),inset 0 1px 0 rgba(255,255,255,0.08);padding:18px;position:relative;overflow:hidden;}}
.cal::before{{content:"";position:absolute;top:0;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(167,139,250,0.45) 50%,transparent);}}
.cal-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}}
.cal-icon{{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#7c3aed,#a78bfa);display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 4px 12px rgba(124,58,237,0.4);}}
.cal-title{{font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#fff;margin-left:8px;}}
.cal-sub{{font-size:9px;color:rgba(255,255,255,0.30);margin-left:8px;margin-top:1px;}}
.cal-nav{{display:flex;gap:5px;}}
.nav-btn{{width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);display:flex;align-items:center;justify-content:center;font-size:9px;color:rgba(255,255,255,0.40);cursor:pointer;}}
.mrow{{font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:rgba(255,255,255,0.65);text-align:center;letter-spacing:0.10em;margin-bottom:9px;}}
.dgrid{{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-bottom:12px;}}
.dn{{text-align:center;font-size:8px;font-weight:700;color:rgba(255,255,255,0.25);letter-spacing:0.05em;text-transform:uppercase;padding-bottom:5px;}}
.dc{{text-align:center;font-size:11px;color:rgba(255,255,255,0.48);padding:5px 1px;border-radius:7px;cursor:pointer;transition:background 0.18s,color 0.18s;}}
.dc:hover{{background:rgba(167,139,250,0.14);color:#fff;}}
.dc.today{{background:linear-gradient(135deg,#7c3aed,#a78bfa);color:#fff;font-weight:800;font-family:'Syne',sans-serif;border-radius:50%;box-shadow:0 0 14px rgba(124,58,237,0.55);}}
.tbadge{{display:flex;align-items:center;gap:10px;background:rgba(124,58,237,0.14);border:1px solid rgba(124,58,237,0.26);border-radius:11px;padding:9px 12px;}}
.tbadge-num{{font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:#fff;line-height:1;}}
.tbadge-sup{{font-size:10px;color:rgba(255,255,255,0.40);vertical-align:super;}}
.tbadge-up{{font-size:8px;font-weight:700;color:#a78bfa;letter-spacing:0.10em;text-transform:uppercase;display:flex;align-items:center;gap:3px;margin-bottom:2px;}}
.tbadge-dot{{width:5px;height:5px;border-radius:50%;background:#a78bfa;}}
.tbadge-task{{font-size:10px;color:rgba(255,255,255,0.62);font-weight:500;}}
.det{{background:rgba(255,255,255,0.055);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:18px;border:1px solid rgba(255,255,255,0.09);box-shadow:0 4px 22px rgba(0,0,0,0.22),inset 0 1px 0 rgba(255,255,255,0.08);padding:16px 18px;position:relative;overflow:hidden;}}
.det::before{{content:"";position:absolute;top:0;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(167,139,250,0.45) 50%,transparent);}}
.det-title{{font-family:'Syne',sans-serif;font-size:12px;font-weight:800;color:#fff;margin-bottom:2px;}}
.det-sub{{font-size:9px;color:rgba(255,255,255,0.28);margin-bottom:11px;letter-spacing:0.04em;}}
.dr{{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);}}
.dr:last-child{{border-bottom:none;}}
.dl{{font-size:10px;color:rgba(255,255,255,0.36);}}
.dv{{font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:#fff;}}
</style></head><body>
<div class="cards">
  <div class="sc"><div class="sc-label">Prediction</div><div class="sc-row"><div class="sc-val" style="color:{pred_color};font-size:{'24px' if len(prediction)>8 else '30px'};">{prediction}</div><div class="sc-arrow" style="color:{pred_color};">{pred_arrow}</div></div><div class="sc-sub-row"><div class="sc-sub">AI Classification</div><div class="sc-pct">{conf_percent}%</div></div><div class="sc-bar" style="background:linear-gradient(90deg,{pred_color}66,{pred_color});"></div></div>
  <div class="sc"><div class="sc-label">Confidence</div><div class="sc-row"><div class="sc-val" style="color:#a78bfa;">{conf_val}%</div><div class="sc-arrow" style="color:#a78bfa;">↑</div></div><div class="sc-sub-row"><div class="sc-sub">Model Certainty</div><div class="sc-pct">{conf_percent}%</div></div><div class="sc-bar" style="background:linear-gradient(90deg,#6d28d9,#a78bfa);"></div></div>
  <div class="sc"><div class="sc-label">Risk Score</div><div class="sc-row"><div class="sc-val" style="color:{risk_color};">{rs_val}%</div><div class="sc-arrow" style="color:{risk_color};">{pred_arrow}</div></div><div class="sc-sub-row"><div class="sc-sub">Computed Score</div><div class="sc-pct">{rs_val}%</div></div><div class="sc-bar" style="background:linear-gradient(90deg,{risk_color}66,{risk_color});"></div></div>
  <div class="sc"><div class="sc-label">Risk Level</div><div class="sc-row"><div class="sc-val" style="color:{risk_color};font-size:{'22px' if len(risk_short)>6 else '30px'};">{risk_short}</div><div class="sc-arrow" style="color:{risk_color};">{pred_arrow}</div></div><div class="sc-sub-row"><div class="sc-sub">Threat Level</div><div class="sc-pct">{rs_val}%</div></div><div class="sc-bar" style="background:linear-gradient(90deg,{risk_color}55,{risk_color});"></div></div>
</div>
<div class="bottom">
  <div class="tc"><div class="tc-head"><div class="tc-title">⚡ Threat Breakdown</div><div class="tc-sub">Feature influence analysis · {today_str}</div><div class="leg"><span><span class="leg-d" style="background:#f87171;"></span><span class="leg-l">High Risk</span></span><span><span class="leg-d" style="background:#34d399;"></span><span class="leg-l">Low Risk</span></span></div></div><div class="tc-body"><div class="ow" id="ow"><div class="otick"></div><div class="or1"></div><div class="or2"></div><div class="cn" id="cn"><div class="cn-pct" id="cnp">—</div><div class="cn-lbl" id="cnl">Hover a<br>threat</div></div></div></div></div>
  <div class="rc">
    <div class="cal"><div class="cal-top"><div style="display:flex;align-items:center;"><div class="cal-icon">📅</div><div><div class="cal-title" style="margin-left:8px;">Calendar</div><div class="cal-sub" style="margin-left:8px;">{today_str}</div></div></div><div class="cal-nav"><div class="nav-btn">‹</div><div class="nav-btn">›</div></div></div><div class="mrow">{month_name} {now.year}</div><div class="dgrid">{days_hdr}{cells}</div><div class="tbadge"><div class="tbadge-num">{today_day}<span class="tbadge-sup">th</span></div><div><div class="tbadge-up"><div class="tbadge-dot"></div>Upcoming</div><div class="tbadge-task">Last scan result</div></div></div></div>
    <div class="det"><div class="det-title">Scan Details</div><div class="det-sub">Latest result breakdown</div><div class="dr"><span class="dl">Verdict</span><span class="dv" style="color:{pred_color};">{prediction}</span></div><div class="dr"><span class="dl">Confidence</span><span class="dv">{conf_full}%</span></div><div class="dr"><span class="dl">Risk Score</span><span class="dv" style="color:{risk_color};">{rs_full}%</span></div><div class="dr"><span class="dl">Risk Level</span><span class="dv" style="color:{risk_color};">{risk_level}</span></div><div class="dr"><span class="dl">Scanned</span><span class="dv" style="font-size:9px;color:rgba(255,255,255,0.35);">{today_str}</span></div></div>
  </div>
</div>
<script>
const threats={tj};const ow=document.getElementById('ow');const cx=185,cy=185;const sizes=[82,67,63,57,53,51,49,47,45];const r1=143,r2=113;const pos=[];
for(let i=0;i<9;i++){{const a=(i/9)*2*Math.PI-Math.PI/2;const r=i%3===1?r2:r1;pos.push({{x:cx+r*Math.cos(a),y:cy+r*Math.sin(a)}});}}
threats.forEach((t,i)=>{{const p=pos[i];const sz=sizes[i]||45;const arr=t.high?'↗':'↘';const ac=t.high?'#f87171':'#34d399';const fs=i===0?'15px':i<3?'12px':'10px';const dx=p.x-cx,dy=p.y-cy;const len=Math.sqrt(dx*dx+dy*dy)-51;const ang=Math.atan2(dy,dx)*180/Math.PI;const ln=document.createElement('div');ln.className='conn';ln.style.cssText=`width:${{len}}px;transform:rotate(${{ang}}deg);`;ow.appendChild(ln);const b=document.createElement('div');b.className='bub';b.style.cssText=`width:${{sz}}px;height:${{sz}}px;left:${{p.x}}px;top:${{p.y}}px;transform:translate(-50%,-50%);`;b.innerHTML=`<div class="bp" style="font-size:${{fs}}">${{t.pct}}%<span class="ba" style="color:${{ac}}">${{arr}}</span></div><div class="bn">${{t.name}}</div>`;b.addEventListener('mouseenter',()=>{{document.getElementById('cnp').textContent=t.pct+'%';document.getElementById('cnl').textContent=t.name;document.getElementById('cn').style.borderColor=ac;document.getElementById('cn').style.boxShadow=`0 0 40px ${{ac}}66`;}});b.addEventListener('mouseleave',()=>{{document.getElementById('cnp').textContent='—';document.getElementById('cnl').innerHTML='Hover a<br>threat';document.getElementById('cn').style.borderColor='rgba(167,139,250,0.48)';document.getElementById('cn').style.boxShadow='0 0 28px rgba(124,58,237,0.32)';}});ow.appendChild(b);}});
</script></body></html>"""


def show():
    try:
        st.set_page_config(page_title="PhishGuard", layout="wide", initial_sidebar_state="collapsed")
    except:
        pass

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
    [data-testid="stAppViewContainer"],[data-testid="stApp"]{{background:transparent !important;}}
    header,footer,#MainMenu{{visibility:hidden;}}
    section[data-testid="stSidebar"]{{display:none !important;}}
    html,body,.stApp{{font-family:'DM Sans',sans-serif;}}
    .main .block-container{{padding:0.5rem 2rem !important;max-width:100% !important;}}
    [data-testid="stMarkdownContainer"]{{width:100% !important;}}
    
    /* Make Scan History button height consistent */
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:nth-child(3) button{{
        background:transparent !important; color:rgba(255,255,255,0.55) !important;
        border:none !important; border-radius:0 !important; height:40px !important;
        font-size:12px !important; font-weight:500 !important; padding:0 !important;
        box-shadow:none !important; letter-spacing:0 !important; text-transform:none !important;
    }}
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:nth-child(3) button p{{
        font-size:12px !important; font-weight:500 !important;
        text-transform:none !important; letter-spacing:0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:nth-child(3) button:hover{{
        background:transparent !important; color:#fff !important;
        border-bottom:2px solid rgba(167,139,250,0.55) !important; box-shadow:none !important; transform:none !important;
    }}
    
    .prescan div[data-testid="stTextInput"] input{{background:rgba(255,255,255,0.07) !important;border:1px solid rgba(255,255,255,0.14) !important;border-radius:16px !important;color:#e2e8f0 !important;font-size:15px !important;height:54px !important;padding:0 22px !important;backdrop-filter:blur(20px) !important;}}
    .prescan div[data-testid="stTextInput"] input:focus{{border-color:rgba(124,58,237,0.55) !important;box-shadow:0 0 28px rgba(124,58,237,0.3) !important;}}
    .prescan div[data-testid="stTextInput"] input::placeholder{{color:rgba(255,255,255,0.3) !important;}}
    .prescan .stTextInput label{{display:none !important;}}
    .prescan div[data-testid="stButton"] button{{background:linear-gradient(135deg,#7c3aed,#6d28d9) !important;color:#fff !important;border:none !important;border-radius:16px !important;height:54px !important;font-weight:700 !important;letter-spacing:0.10em !important;text-transform:uppercase !important;box-shadow:0 8px 28px rgba(124,58,237,0.45) !important;white-space:nowrap !important;}}
    .prescan div[data-testid="stButton"] button:hover{{background:linear-gradient(135deg,#8b5cf6,#7c3aed) !important;box-shadow:0 12px 36px rgba(124,58,237,0.6) !important;transform:translateY(-3px) !important;}}
    .postscan div[data-testid="stTextInput"] input{{background:rgba(255,255,255,0.07) !important;border:1px solid rgba(255,255,255,0.13) !important;border-radius:12px !important;color:#e2e8f0 !important;font-size:14px !important;height:46px !important;backdrop-filter:blur(15px) !important;}}
    .postscan div[data-testid="stTextInput"] input:focus{{border-color:rgba(124,58,237,0.5) !important;}}
    .postscan .stTextInput label{{display:none !important;}}
    .postscan div[data-testid="stButton"] button{{background:linear-gradient(135deg,#7c3aed,#6d28d9) !important;color:#fff !important;border:none !important;border-radius:12px !important;height:46px !important;font-weight:700 !important;letter-spacing:0.08em !important;text-transform:uppercase !important;box-shadow:0 6px 20px rgba(124,58,237,0.4) !important;}}
    .postscan div[data-testid="stButton"] button:hover{{background:linear-gradient(135deg,#8b5cf6,#7c3aed) !important;box-shadow:0 8px 28px rgba(124,58,237,0.55) !important;transform:translateY(-2px) !important;}}
    div[data-testid="stStatusWidget"]{{display:none!important;}}
    </style>
    """, unsafe_allow_html=True)

    if st.query_params.get("_logout") == "1":
        st.query_params.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.page = "login"
        st.session_state.logged_in = False
        st.rerun()

    if "user_id" not in st.session_state:
        st.error("Please login first.")
        st.stop()

    if "scan_done" not in st.session_state:
        st.session_state.scan_done = False

    today = datetime.now().strftime("%d %b %Y")
    username = st.session_state.get("user_name", st.session_state.get("user_id", "User"))
    username = str(username)
    initials = ("".join([w[0].upper() for w in username.split()[:2]]) or "U")[:2]
    uid = str(st.session_state.get("user_id", ""))

    nav_l, nav_r = st.columns([5, 3])
    with nav_l:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px 0 10px 16px;">
          <span style="font-size:22px">🛡️</span>
          <span style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#a78bfa;letter-spacing:0.08em;">PHISHGUARD</span>
          <div style="display:flex;align-items:center;gap:24px;margin-left:26px;">
            <span style="font-size:12px;font-weight:700;color:#a78bfa;border-bottom:2px solid #a78bfa;padding-bottom:2px;">Dashboard</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with nav_r:
        nr1, nr2, nr3 = st.columns([2, 1.5, 1.5])
        with nr1:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:flex-end;height:100%;padding-right:4px;">
              <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.10);border-radius:18px;padding:5px 13px;font-size:11px;color:rgba(255,255,255,0.52);">📅 {today}</div>
            </div>""", unsafe_allow_html=True)
        with nr2:
            if st.button("Scan History", key="nav_scan_history", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
        with nr3:
            components.html(f"""
<script>
(function() {{
  var old = window.parent.document.getElementById('pg-user-widget');
  if (old) old.remove();
  var oldStyle = window.parent.document.getElementById('pg-user-style');
  if (oldStyle) oldStyle.remove();

  var style = window.parent.document.createElement('style');
  style.id = 'pg-user-style';
  style.textContent = `
    #pg-user-widget {{
      display:inline-flex;
      align-items:center;
      font-family:'DM Sans',sans-serif;
      position:absolute;
      top:50%;
      left:0;
      transform:translateY(-50%);
      z-index:999999;
    }}
    #pg-user-btn {{
      display:flex;align-items:center;gap:8px;cursor:pointer;
      background:rgba(17,24,39,0.6);border:1px solid rgba(255,255,255,0.1);
      border-radius:8px;padding:8px 18px 8px 8px;transition:all 0.2s;
      backdrop-filter:blur(8px);height:46px;min-width:120px;
    }}
    #pg-user-btn:hover {{ background:rgba(17,24,39,0.95);border-color:rgba(167,139,250,0.5); }}
    .pg-av {{
      width:32px;height:32px;border-radius:50%;flex-shrink:0;overflow:hidden;
      background:linear-gradient(135deg,#7c3aed,#a78bfa);
      display:flex;align-items:center;justify-content:center;
      font-size:13px;font-weight:700;color:#fff;
      border:1.5px solid rgba(167,139,250,0.55);
    }}
    .pg-av img {{ width:100%;height:100%;object-fit:cover; }}
    #pg-uname {{ font-size:12px;font-weight:600;color:rgba(255,255,255,0.9);white-space:nowrap; }}
    .pg-chev {{ font-size:10px;color:rgba(255,255,255,0.5);margin-left:2px;transition:transform 0.2s; }}
    .pg-chev.up {{ transform:rotate(180deg); }}
    #pg-dropdown {{
      display:none;position:absolute;top:calc(100% + 8px);left:0;
      width:250px;background:rgba(14,6,40,0.97);
      border:1px solid rgba(167,139,250,0.2);border-radius:18px;
      box-shadow:0 24px 64px rgba(0,0,0,0.7);backdrop-filter:blur(24px);overflow:hidden;
      z-index:9999999;
    }}
    #pg-dropdown.open {{ display:block;animation:pgFade 0.18s ease; }}
    @keyframes pgFade {{ from{{opacity:0;transform:translateY(-8px)}} to{{opacity:1;transform:translateY(0)}} }}
    .pg-dh {{ padding:16px;border-bottom:1px solid rgba(255,255,255,0.07);display:flex;align-items:center;gap:12px; }}
    .pg-dav {{
      width:46px;height:46px;border-radius:50%;flex-shrink:0;overflow:hidden;
      background:linear-gradient(135deg,#7c3aed,#a78bfa);
      display:flex;align-items:center;justify-content:center;
      font-size:17px;font-weight:700;color:#fff;
      border:2px solid rgba(167,139,250,0.5);cursor:pointer;position:relative;
    }}
    .pg-dav img {{ width:100%;height:100%;object-fit:cover; }}
    .pg-dav-ov {{
      position:absolute;inset:0;background:rgba(0,0,0,0.55);border-radius:50%;
      display:flex;align-items:center;justify-content:center;font-size:14px;
      opacity:0;transition:opacity 0.2s;
    }}
    .pg-dav:hover .pg-dav-ov {{ opacity:1; }}
    .pg-dn {{ font-size:13px;font-weight:700;color:#fff; }}
    .pg-duid {{ font-size:10px;color:rgba(255,255,255,0.32);margin-top:2px; }}
    .pg-db {{ padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.07); }}
    .pg-lbl {{ font-size:9px;font-weight:700;color:rgba(255,255,255,0.35);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:5px; }}
    .pg-inp {{
      width:100%;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
      border-radius:10px;color:#fff;font-size:12px;padding:8px 12px;outline:none;
      transition:border-color 0.2s;font-family:'DM Sans',sans-serif;margin-bottom:8px;
    }}
    .pg-inp:focus {{ border-color:rgba(167,139,250,0.55); }}
    .pg-save {{
      width:100%;padding:8px;background:linear-gradient(135deg,#7c3aed,#6d28d9);
      border:none;border-radius:10px;color:#fff;font-size:11px;font-weight:700;
      letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;transition:all 0.2s;
    }}
    .pg-save:hover {{ background:linear-gradient(135deg,#8b5cf6,#7c3aed); }}
    .pg-photo-row {{ display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap; }}
    .pg-pbtn {{
      font-size:10px;color:rgba(167,139,250,0.85);background:rgba(124,58,237,0.12);
      border:1px solid rgba(124,58,237,0.25);border-radius:8px;padding:5px 10px;cursor:pointer;
    }}
    .pg-pbtn:hover {{ background:rgba(124,58,237,0.25);color:#c4b5fd; }}
    .pg-rbtn {{
      font-size:10px;color:rgba(248,113,113,0.8);background:rgba(248,113,113,0.08);
      border:1px solid rgba(248,113,113,0.2);border-radius:8px;padding:5px 10px;cursor:pointer;
    }}
    .pg-rbtn:hover {{ background:rgba(248,113,113,0.18);color:#f87171; }}
    .pg-logout {{
      display:flex;align-items:center;gap:10px;padding:13px 16px;cursor:pointer;
      color:rgba(248,113,113,0.85);font-size:12px;font-weight:600;transition:background 0.18s;
    }}
    .pg-logout:hover {{ background:rgba(248,113,113,0.08);color:#f87171; }}
  `;
  window.parent.document.head.appendChild(style);

  var iframes = window.parent.document.querySelectorAll('iframe');
  var myIframe = null;
  iframes.forEach(function(f) {{ if (f.contentWindow === window) myIframe = f; }});

  var widget = window.parent.document.createElement('div');
  widget.id = 'pg-user-widget';
  widget.innerHTML = `
    <div id="pg-user-btn" onclick="window.parent.pgToggle()">
      <div class="pg-av" id="pg-nav-av" data-initials="{initials}"><span>{initials}</span></div>
      <span id="pg-uname">{username}</span>
      <span class="pg-chev" id="pg-chev">▾</span>
    </div>
    <div id="pg-dropdown">
      <div class="pg-dh">
        <div class="pg-dav" id="pg-dav" onclick="window.parent.document.getElementById('pg-photo-input').click()">
          <span>{initials}</span>
          <div class="pg-dav-ov">📷</div>
        </div>
        <div>
          <div class="pg-dn" id="pg-dn">{username}</div>
          <div class="pg-duid">{uid}</div>
        </div>
      </div>
      <div class="pg-db">
        <div class="pg-photo-row">
          <span class="pg-lbl" style="margin:0">Photo</span>
          <label class="pg-pbtn" for="pg-photo-input">📷 Change</label>
          <input type="file" id="pg-photo-input" accept="image/*" style="display:none" onchange="window.parent.pgPhoto(this)">
          <span class="pg-rbtn" id="pg-remove-btn" onclick="window.parent.pgRemovePhoto()" style="display:none">✕ Remove</span>
        </div>
        <div class="pg-lbl">Display Name</div>
        <input class="pg-inp" id="pg-name-inp" value="{username}" placeholder="Your name" />
        <button class="pg-save" id="pg-save-btn" onclick="window.parent.pgSave()">Save Changes</button>
      </div>
      <div class="pg-logout" onclick="window.parent.pgLogout()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Sign Out
      </div>
    </div>
  `;

  if (myIframe && myIframe.parentElement) {{
    myIframe.parentElement.style.position = 'relative';
    myIframe.parentElement.style.overflow = 'visible';
    myIframe.parentElement.style.zIndex = '999999';
    myIframe.style.cssText = 'border:none;height:40px;overflow:visible;';
    myIframe.parentElement.appendChild(widget);
  }} else {{
    widget.style.cssText = 'position:fixed;top:16px;right:24px;z-index:9999999;';
    window.parent.document.body.appendChild(widget);
  }}

  window.parent.pgOpen = false;
  window.parent.pgToggle = function() {{
    window.parent.pgOpen = !window.parent.pgOpen;
    var dd = window.parent.document.getElementById('pg-dropdown');
    dd.classList.toggle('open', window.parent.pgOpen);
    var chev = window.parent.document.getElementById('pg-chev');
    chev.textContent = window.parent.pgOpen ? '▴' : '▾';
  }};
  window.parent.document.addEventListener('click', function(e) {{
    var btn = window.parent.document.getElementById('pg-user-btn');
    var dd = window.parent.document.getElementById('pg-dropdown');
    if (btn && dd && !btn.contains(e.target) && !dd.contains(e.target)) {{
      window.parent.pgOpen = false;
      dd.classList.remove('open');
      var chev = window.parent.document.getElementById('pg-chev');
      if (chev) chev.textContent = '▾';
    }}
  }});
  window.parent.pgPhoto = function(input) {{
    if (!input.files[0]) return;
    var reader = new FileReader();
    reader.onload = function(e) {{
      var src = e.target.result;
      var imgTag = '<img src="' + src + '" />';
      var navAv = window.parent.document.getElementById('pg-nav-av');
      var dAv = window.parent.document.getElementById('pg-dav');
      if (navAv) navAv.innerHTML = imgTag;
      if (dAv) dAv.innerHTML = imgTag + '<div class="pg-dav-ov">📷</div>';
      localStorage.setItem('pg_avatar', src);
      var rb = window.parent.document.getElementById('pg-remove-btn');
      if (rb) rb.style.display = 'inline-block';
    }};
    reader.readAsDataURL(input.files[0]);
  }};
  window.parent.pgRemovePhoto = function() {{
    var navAv = window.parent.document.getElementById('pg-nav-av');
    var dAv = window.parent.document.getElementById('pg-dav');
    var ini = navAv ? (navAv.getAttribute('data-initials') || 'U') : 'U';
    if (navAv) navAv.innerHTML = '<span>' + ini + '</span>';
    if (dAv) dAv.innerHTML = '<span>' + ini + '</span><div class="pg-dav-ov">📷</div>';
    localStorage.removeItem('pg_avatar');
    var rb = window.parent.document.getElementById('pg-remove-btn');
    if (rb) rb.style.display = 'none';
  }};
  window.parent.pgSave = function() {{
    var name = window.parent.document.getElementById('pg-name-inp').value.trim();
    if (!name) return;
    window.parent.document.getElementById('pg-uname').textContent = name;
    window.parent.document.getElementById('pg-dn').textContent = name;
    localStorage.setItem('pg_username', name);
    var btn = window.parent.document.getElementById('pg-save-btn');
    btn.textContent = '✓ Saved!';
    btn.style.background = 'linear-gradient(135deg,#059669,#10b981)';
    setTimeout(function() {{ btn.textContent = 'Save Changes'; btn.style.background = ''; }}, 1800);
  }};
  window.parent.pgLogout = function() {{
    localStorage.removeItem('pg_user_id');
    localStorage.removeItem('pg_page');
    localStorage.removeItem('pg_username');
    localStorage.removeItem('pg_avatar');
    localStorage.removeItem('phishguard_user');
    window.top.location.href = window.top.location.origin + window.top.location.pathname + '?_logout=1';
  }};

  var realName = "{username}";
  var storedName = localStorage.getItem('pg_username');
  var displayName = (storedName && storedName !== '{uid}') ? storedName : realName;
  localStorage.setItem('pg_username', displayName);
  var un = window.parent.document.getElementById('pg-uname');
  var dn = window.parent.document.getElementById('pg-dn');
  var ni = window.parent.document.getElementById('pg-name-inp');
  if (un) un.textContent = displayName;
  if (dn) dn.textContent = displayName;
  if (ni) ni.value = displayName;

  var av = localStorage.getItem('pg_avatar');
  if (av) {{
    var imgTag = '<img src="' + av + '" />';
    var navAv2 = window.parent.document.getElementById('pg-nav-av');
    var dAv2 = window.parent.document.getElementById('pg-dav');
    if (navAv2) navAv2.innerHTML = imgTag;
    if (dAv2) dAv2.innerHTML = imgTag + '<div class="pg-dav-ov">📷</div>';
    var rb2 = window.parent.document.getElementById('pg-remove-btn');
    if (rb2) rb2.style.display = 'inline-block';
  }}
}})();
</script>
            """, height=40, scrolling=False)
    st.markdown('<div style="border-bottom:1px solid rgba(255,255,255,0.07);"></div>', unsafe_allow_html=True)

    if not st.session_state.scan_done:
        st.markdown("""<div style="width:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:6vh 20px 32px;margin:0 auto;"><div style="font-family:'Syne',sans-serif;font-size:clamp(28px,4vw,50px);font-weight:800;color:#fff;line-height:1.1;margin-bottom:32px;letter-spacing:-0.02em;">Is This Link <span style="background:linear-gradient(135deg,#a78bfa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;"> Safe?</span></div></div>""",unsafe_allow_html=True)
        _,mid,_=st.columns([1,3,1])
        with mid:
            st.markdown('<div class="prescan">',unsafe_allow_html=True)
            c1,c2=st.columns([5,1])
            with c1:url=st.text_input("url","",label_visibility="collapsed",placeholder="Paste a URL to scan...",key="url_input")
            with c2:scan_btn=st.button("SCAN",use_container_width=True,key="scan_btn")
            st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.markdown("<br>",unsafe_allow_html=True);st.markdown('<div class="postscan">',unsafe_allow_html=True)
        c1,c2=st.columns([7,1])
        with c1:url=st.text_input("url",st.session_state.get("last_url",""),label_visibility="collapsed",key="url_input")
        with c2:scan_btn=st.button("SCAN",use_container_width=True,key="scan_btn")
        st.markdown('</div>',unsafe_allow_html=True)

    if "url_input" in st.session_state:url=st.session_state.url_input

    if scan_btn:
        url_to_scan = url.strip()
        if not url_to_scan:
            st.error("⚠️ Please enter a URL to scan")
            st.stop()
        if not url_to_scan.startswith(("http://", "https://")):
            url_to_scan = "https://" + url_to_scan
        if len(url_to_scan) < 10:
            st.error("⚠️ URL is too short. Please enter a complete URL")
            st.stop()
        st.session_state.scan_done=False;st.session_state.last_url=url_to_scan;progress=st.progress(0)
        for i in range(101):time.sleep(0.01);progress.progress(i)
        try:
            res=requests.post(f"{BACKEND_URL}/predict",json={"url":url_to_scan,"user_id":st.session_state.user_id},timeout=20);progress.empty()
            if res.status_code==200:
                data=res.json();st.session_state.prediction=data.get("prediction");st.session_state.confidence=data.get("confidence");st.session_state.risk_score=data.get("risk_score");st.session_state.risk_level=data.get("risk_level");st.session_state.shap_values=data.get("shap_values",[]);st.session_state.scan_done=True;st.rerun()
            else:st.error(f"Backend returned {res.status_code}")
        except Exception as e:progress.empty();st.error(f"Backend error: {e}")

    if st.session_state.scan_done:
        components.html(build_results_html(st.session_state.prediction,st.session_state.confidence,st.session_state.risk_score,st.session_state.risk_level,st.session_state.shap_values),height=940,scrolling=False)

if __name__=="__main__":show()